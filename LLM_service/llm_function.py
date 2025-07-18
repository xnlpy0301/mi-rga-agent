import logging
import os
import time
import uuid
from datetime import datetime

import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from openai import OpenAI


# 配置类保持不变
class Config:
    def __init__(self):
        self.data_dir = "Documents"
        self.supported_extensions = ['.md', '.txt', '.doc', '.docx', '.pdf']
        self.chunk_size = 500
        self.chunk_overlap = 50
        self.embedding_model = "model/xiaobu-embedding-v2"
        self.collection_name = "accounts"
        self.max_results = 5
        self.distance_threshold = 0.25
        self.llm_api_key = ""
        self.llm_base_url = "https://api.deepseek.com"
        self.llm_model = "deepseek-chat"


# 提示模板保持不变
PROMPT_TEMPLATE = """
你是一个安全助手，需要根据提供的密码文档信息回答问题。请严格遵守以下规则：
1. 只使用提供的上下文信息回答
2. 不要透露任何文档来源或元数据
3. 如果信息不完整请明确说明
<上下文>
{docs}
</上下文>
<用户问题>
{question}
</用户问题>
请直接给出答案：
"""

# DocumentProcessor类保持不变
class DocumentProcessor:
    def __init__(self, config):
        self.config = config

    def load_and_split_documents(self):
        try:
            from pathlib import Path
            data_dir = os.path.abspath(os.path.expanduser(self.config.data_dir))

            path = Path(data_dir)
            files = []
            for ext in self.config.supported_extensions:
                files.extend(path.rglob(f"*{ext}"))
                files.extend(path.rglob(f"*{ext.upper()}"))
            files = list(set(files))

            all_documents = []
            for file_path in files:
                if file_path.is_file():
                    try:
                        loader = UnstructuredFileLoader(str(file_path))
                        docs = loader.load()
                        all_documents.extend(docs)

                    except Exception as e:

                        continue
            if not all_documents:
                raise RuntimeError("未加载到任何文档")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
            return splitter.split_documents(all_documents)
        except Exception as e:

            raise


class VectorStoreManager:
    def __init__(self, config):
        self.config = config

        self.documents = []
    def is_empty(self):
        return len(self.documents) == 0
    def reset_collection(self):
        self.documents = []

    def populate_collection(self, documents):
        # 为文档添加文件名前缀
        for doc in documents:
            file_path = doc.metadata["source"]
            file_name = os.path.basename(file_path)
            content = f'{file_name}: {doc.page_content}'
            self.documents.append(content)

    def query(self, question, n_results=5):
        if not self.documents:

            return {"documents": [[]], "distances": [[]]}
        # 简单的关键词匹配算法
        keywords = question.lower().split()
        scores = []
        for doc in self.documents:
            doc_lower = doc.lower()
            # 计算匹配的关键词数量作为简单的相关性分数
            score = sum(1 for keyword in keywords if keyword in doc_lower)
            scores.append((doc, score))
        # 按分数排序，取前n_results个
        sorted_docs = sorted(scores, key=lambda x: x[1], reverse=True)[:n_results]
        # 如果没有匹配项，返回前n_results个文档
        if all(score == 0 for _, score in sorted_docs) and self.documents:
            sorted_docs = [(doc, 0) for doc in self.documents[:n_results]]
        documents = [doc for doc, _ in sorted_docs]
        # 将分数转换为距离（分数越高，距离越小）
        distances = [1.0 - min(score/len(keywords), 1.0) for _, score in sorted_docs]
        return {
            "documents": [documents],
            "distances": [distances]
        }




class LLM:
    def __init__(self, config):
        self.config = config

        self.llm_client = self._initialize_llm()

    def _initialize_llm(self):
        return OpenAI(
            base_url=self.config.llm_base_url,
            api_key=self.config.llm_api_key
        )
    def generate_response(self, user_query):

        messages = [{"role": "user", "content": user_query}]

        try:
            completion = self.llm_client.chat.completions.create(
                model=self.config.llm_model,
                temperature=0.75,
                messages=messages,
                stream=True,
                stream_options={"include_usage": False}
            )

            full_response = []
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content is not None:
                    full_response.append(content)
                    yield content

        except Exception as e:
            yield "抱歉，处理您的请求时出现问题"


class RAGLLM:
    def __init__(self, config, vector_store):
        self.config = config

        self.vector_store = vector_store
        self.llm_client = self._initialize_llm()

    def _initialize_llm(self):
        return OpenAI(
            base_url=self.config.llm_base_url,
            api_key=self.config.llm_api_key
        )

    def _format_context(self, results):
        context_parts = []
        for doc, distance in zip(results["documents"][0], results["distances"][0]):
            if distance < self.config.distance_threshold:
                context_parts.append(f"[相关度: {1 - distance:.2f}]\n{doc}")
        return "\n\n---\n\n".join(context_parts) if context_parts else "未找到相关文档信息"

    def generate_response(self, user_query):
        results = self.vector_store.query(
            user_query,
            n_results=self.config.max_results
        )

        context = self._format_context(results)
        prompt = PROMPT_TEMPLATE.format(
            docs=context,
            question=user_query
        )


        messages = [{"role": "user", "content": prompt}]

        try:
            completion = self.llm_client.chat.completions.create(
                model=self.config.llm_model,
                temperature=0.75,
                messages=messages,
                stream=True,
                stream_options={"include_usage": False}
            )

            full_response = []
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content is not None:
                    full_response.append(content)
                    yield content

        except Exception as e:

            yield "抱歉，处理您的请求时出现问题"
