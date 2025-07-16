import json
import os
from openai import OpenAI,AsyncOpenAI


TABLE_REPORT_GENERATION_PROMPT = '''
根据以下数据和分析需求，生成一份完整、清晰且专业的报告。

数据报告标准：
1. 客观性：分析需完全基于用户提供的数据，杜绝主观推测，确保信息真实可靠。
2. 精确性：每一结论必须有数据支撑，数字与结果无误，绝不编造或夸大。
3. 逻辑性：分析结构清晰，确保报告内的各部分内容有条理，但关键点之间可独立存在，无需直接关联。
4. 可读性：语言表达简洁明了，避免术语堆砌，确保非专业人士也能理解。
5. 行动导向：报告需提出切实可行的建议或策略，支持用户决策。
6. 语言多样性：语言表达应丰富多样，避免单调重复，增强报告的吸引力和专业性。
7. 数据覆盖全面性：分析过程中应尽可能充分利用用户提供的数据，避免遗漏关键信息。

报告结构与格式：
1. 标题：
   - 格式：<h3 align="center">《标题》</h3>
   - 要求：简明扼要，直接反映分析主题与目标。

2. 正文内容：
   - 第一段：
     - 标题：<h5><i>序号、概述</i></h5>
     - 内容：概述数据背景及整体情况，简洁概括核心要点。
   - 中间四段：
     - 标题：<h5><i>序号、分析维度</i></h5>
     - 内容：逐一展开详细分析，每段须基于用户数据，结论明确且逻辑严谨，字数不少于300字。
   - 最后一段：
     - 标题：<h5><i>序号、总结与建议</i></h5>
     - 内容：总结分析结果，并结合数据提出实际、具体的建议。

3. 段落数量：
   - 全文包含5-7段，每段不少于300字，总字数不低于1000字。

生成要求：
1. 报告必须结构完整、详略得当，避免冗余或空洞描述。
2. 避免使用过多格式符号（如“###”）。
3. 数据缺失或不完整时，调整分析角度，不直接提及“数据不足”。
4. 遵循分析标准，根据数据合理推导和总结，避免模板化输出。

生成内容：
用户输入的分析需求：
=============================
{query}
=============================   


注意：报告内容必须严格依据用户上传的数据进行分析，避免引入未提供或不相关的信息。'''




class ReportGroundTruthGenerator:
    def __init__(self, model_name: str = None):
        """
        初始化 ReportGroundTruthGenerator 类。
        支持动态选择模型，配置 API 密钥和基础 URL。
        """

        self.models = {
            "qwen2.5-32b-instruct": {
                "api_key": os.getenv("QWEN_API_KEY"),
                "base_url": os.getenv("QWEN_BASE_URL"),
            },
            "deepseek-chat": {
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": os.getenv("DEEPSEEK_BASE_URL"),
            },
            "moonshot-v1-32k": {
                "api_key": os.getenv("MOONSHOT_API_KEY"),
                "base_url": os.getenv("MOONSHOT_BASE_URL"),
            },
        }

        if model_name not in self.models:
            raise ValueError(f"模型名称无效，请从以下列表中选择: {list(self.models.keys())}")

        self.model_name = model_name
        self.api_key = self.models[model_name]["api_key"]
        self.base_url = self.models[model_name]["base_url"]

        self.client =  OpenAI(api_key=self.api_key,base_url=self.base_url)

    def generate_response(self, sys_prompt,user_query: str):
        """
        根据任务类型生成对应的响应。
        Argument:
            query: str - 查询内容或分析角度
            key_points: str - 关键点
            data: str - 表格数据
        """

        # print(prompt)
        messages = [{"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_query}]

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                temperature=0.75,
                messages=messages,
                stream=True,
                stream_options={"include_usage": False}
            )

            for chunk in completion:
                yield json.loads(chunk.model_dump_json())['choices'][0]['delta']['content']

        except Exception as e:
            print(f"stream_response 调用出错: {e}")
            yield ''


if __name__ == '__main__':
    topic = '写一份关于《七月深北大道4S店车型差异化分析》的报告，详尽探讨各车型的店内销量和顾客欢迎度'
    sys = "你是一个表格生报告助手，请按照我的要求写一份数据分析报告"

    prompt = TABLE_REPORT_GENERATION_PROMPT.format(query=topic)        # 需要替代原始prompt中的部分

    model_list = ["qwen2.5-32b-instruct", "deepseek-chat", "moonshot-v1-32k"]

    for model in model_list:
        small_table_report_generator = ReportGroundTruthGenerator(model)
        res = ''

        try:
            for chunk in small_table_report_generator.generate_response(sys,prompt):
                if chunk is not None:
                    print(chunk, flush=True, end='')
                    res += chunk
            print(res)

        except Exception as e:
            print(f"Error occurred for model {model}: {e}")





