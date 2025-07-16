import logging
import os

import chromadb
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from openai import OpenAI
import streamlit as st


# 配置类
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
        self.llm_api_key = "sk-9711b868641243f1bd50983d7da7f3b1"
        self.llm_base_url = "https://api.deepseek.com"
        self.llm_model = "deepseek-chat"


# 日志类（适配Streamlit）
class StreamlitLogger:
    def info(self, message):
        st.sidebar.info(message)
        logging.info(message)

    def error(self, message):
        st.sidebar.error(message)
        logging.error(message)


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


class DocumentProcessor:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def load_and_split_documents(self):
        try:
            from pathlib import Path
            data_dir = os.path.abspath(os.path.expanduser(self.config.data_dir))
            self.logger.info(f"开始加载目录: {data_dir}")

            path = Path(data_dir)
            files = []
            for ext in self.config.supported_extensions:
                files.extend(path.rglob(f"*{ext}"))
                files.extend(path.rglob(f"*{ext.upper()}"))

            files = list(set(files))
            self.logger.info(f"找到 {len(files)} 个支持格式的文件")

            all_documents = []
            for file_path in files:
                if file_path.is_file():
                    try:
                        loader = UnstructuredFileLoader(str(file_path))
                        docs = loader.load()
                        all_documents.extend(docs)
                        self.logger.info(f"成功加载文件: {file_path}")
                    except Exception as e:
                        self.logger.error(f"加载文件 {file_path} 失败: {str(e)}")
                        continue

            if not all_documents:
                raise RuntimeError("未加载到任何文档")

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
            return splitter.split_documents(all_documents)
        except Exception as e:
            self.logger.error(f"文档处理失败: {str(e)}")
            raise


class VectorStoreManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.client = chromadb.PersistentClient()
        self.embedding_function = self._create_embedding_function()
        self.collection = self._initialize_collection()

    def _create_embedding_function(self):
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.config.embedding_model
        )

    def _initialize_collection(self):
        try:
            collection = self.client.get_collection(
                name=self.config.collection_name,
                embedding_function=self.embedding_function
            )
            self.logger.info(f"使用现有集合: {self.config.collection_name}")
            return collection
        except NotFoundError:
            self.logger.info(f"创建新集合: {self.config.collection_name}")
            return self.client.create_collection(
                name=self.config.collection_name,
                configuration={
                    "hnsw": {
                        "space": "cosine",
                    },
                    "embedding_function": self.embedding_function
                }
            )

    def is_empty(self):
        return self.collection.count() == 0

    def reset_collection(self):
        try:
            self.client.delete_collection(self.config.collection_name)
            self.logger.info(f"删除集合: {self.config.collection_name}")
        except NotFoundError:
            pass
        self.collection = self._initialize_collection()

    def populate_collection(self, documents):
        chroma_docs = []
        chroma_ids = []

        for idx, doc in enumerate(documents):
            file_path = doc.metadata["source"]
            file_name = os.path.basename(file_path)
            content = f'{file_name}: {doc.page_content}'
            chroma_docs.append(content)
            chroma_ids.append(f"doc_{idx}_{file_name}")

        self.collection.add(
            documents=chroma_docs,
            ids=chroma_ids
        )
        self.logger.info(f"已加载 {len(chroma_docs)} 个文档片段")

    def query(self, question, n_results=5):
        return self.collection.query(
            query_texts=[question],
            n_results=n_results,
            include=["documents", "distances"]
        )


class LLM:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

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
            self.logger.error(f"生成响应时出错: {e}")
            yield "抱歉，处理您的请求时出现问题"


class RAGLLM:
    def __init__(self, config, logger, vector_store):
        self.config = config
        self.logger = logger
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

        self.logger.info(f"生成提示词: {prompt}")
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
            self.logger.error(f"生成响应时出错: {e}")
            yield "抱歉，处理您的请求时出现问题"