import random
from datetime import datetime, timedelta
import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from LLM_service import DocumentProcessor


def document_qa_page(config, logger):
    st.header("📄 文档智能问答")
    st.button("⬅️ 返回主页", on_click=lambda: setattr(st.session_state, 'page', 'home'))

    st.subheader("📂 文档管理")
    uploaded_files = st.file_uploader(
        "上传文档",
        type=config.supported_extensions,
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_path = os.path.join(config.data_dir, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            logger.info(f"保存文件: {save_path}")
        st.success("文件上传成功！")

    if st.button("🔄 重新加载文档"):
        try:
            processor = DocumentProcessor(config, logger)
            documents = processor.load_and_split_documents()
            st.session_state.vs_manager.reset_collection()
            st.session_state.vs_manager.populate_collection(documents)
            st.success(f"文档重新加载成功，共处理 {len(documents)} 个文档片段。")
        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            st.error(f"文档处理失败: {str(e)}")

    st.divider()
    st.subheader("🤖 智能问答")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("请输入您的问题"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(
                st.session_state.rag_system.generate_response(prompt)
            )

        st.session_state.messages.append({"role": "assistant", "content": response})

# ====================== 农业监测系统页面函数 ======================

def video_surveillance_page():
    st.header("🌾 农田视频监控系统")
    st.info("实时监控农田状态，支持多摄像头切换查看")
    st.button("⬅️ 返回主页", on_click=lambda: setattr(st.session_state, 'page', 'home'))

    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["摄像头1: 东区", "摄像头2: 西区", "摄像头3: 南区"])

    with tab1:
        st.subheader("东区监控 - 作物生长情况")
        st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
                 caption="东区作物生长情况 - 实时画面")

        col1, col2, col3 = st.columns(3)
        col1.metric("温度", "28.5°C", "+1.2°C")
        col2.metric("湿度", "65%", "-3%")
        col3.metric("光照强度", "8500 lux", "稳定")

        st.progress(75, text="作物生长进度")

    with tab2:
        st.subheader("西区监控 - 灌溉系统")
        st.image("https://images.unsplash.com/photo-1551650992-ee4fd47df41f?w=800",
                 caption="西区灌溉系统 - 实时画面")

        # 灌溉系统状态
        st.write("### 灌溉系统状态")
        irrigation_status = {
            "区域A": "运行中 (35%)",
            "区域B": "待机",
            "区域C": "运行中 (70%)",
            "区域D": "故障"
        }

        for area, status in irrigation_status.items():
            st.info(f"{area}: {status}")

    with tab3:
        st.subheader("南区监控 - 设备状态")
        st.image("https://images.unsplash.com/photo-1492496913980-501348b61469?w=800",
                 caption="南区设备状态 - 实时画面")

        # 设备状态表
        st.write("### 设备运行状态")
        device_data = {
            "设备名称": ["无人机1", "传感器节点5", "水泵3", "气象站2"],
            "状态": ["在线", "离线", "在线", "在线"],
            "电池电量": ["78%", "0%", "92%", "65%"],
            "最后活动": ["2分钟前", "3小时前", "5分钟前", "10分钟前"]
        }
        st.table(device_data)


def soil_monitoring_page():
    st.header("🌱 智能土壤监测系统")
    st.info("实时监测土壤各项指标，为精准农业提供数据支持")
    st.button("⬅️ 返回主页", on_click=lambda: setattr(st.session_state, 'page', 'home'))

    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["土壤湿度", "土壤养分", "土壤温度"])

    with tab1:
        st.subheader("土壤湿度监测")

        # 生成模拟数据
        dates = pd.date_range(end=datetime.now(), periods=24, freq='H')
        moisture = [random.uniform(15, 35) for _ in range(24)]

        # 创建图表
        fig = px.line(
            x=dates, y=moisture,
            title="过去24小时土壤湿度变化",
            labels={'x': '时间', 'y': '湿度 (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # 区域湿度分布
        st.write("### 不同区域土壤湿度")
        regions = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        moisture_levels = [round(random.uniform(20, 40), 1) for _ in regions]

        for region, level in zip(regions, moisture_levels):
            st.progress(int(level), text=f"{region}区: {level}%")

    with tab2:
        st.subheader("土壤养分分析")

        # 生成养分数据
        nutrients = ['氮(N)', '磷(P)', '钾(K)', '有机质']
        values = [round(random.uniform(0.5, 3.0), 2) for _ in nutrients]

        # 创建饼图
        fig = px.pie(
            names=nutrients,
            values=values,
            title="土壤养分比例"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 养分水平表
        st.write("### 养分水平评估")
        assessment = {
            "指标": ["氮含量", "磷含量", "钾含量", "pH值", "有机质"],
            "当前值": ["2.3 g/kg", "1.8 g/kg", "2.5 g/kg", "6.8", "3.2%"],
            "标准范围": ["1.5-2.5 g/kg", "1.2-2.0 g/kg", "2.0-3.0 g/kg", "6.0-7.0", ">2.5%"],
            "状态": ["正常", "正常", "正常", "正常", "充足"]
        }
        st.table(assessment)

    with tab3:
        st.subheader("土壤温度监测")

        # 生成温度数据
        depths = ['0-10cm', '10-20cm', '20-30cm', '30-40cm']
        temps = [round(random.uniform(18, 28), 1) for _ in depths]

        # 创建柱状图
        fig = px.bar(
            x=depths, y=temps,
            title="不同深度土壤温度",
            labels={'x': '深度', 'y': '温度 (°C)'},
            color=temps,
            color_continuous_scale='thermal'
        )
        st.plotly_chart(fig, use_container_width=True)

        # 温度趋势
        st.write("### 一周温度趋势")
        week_days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        week_temps = [round(random.uniform(20, 30), 1) for _ in week_days]
        st.line_chart(pd.DataFrame({'温度': week_temps}, index=week_days))


def weather_monitoring_page():
    st.header("🌦️ 农田气象监测系统")
    st.info("实时监测农田气象条件，提供精准气象预报")
    st.button("⬅️ 返回主页", on_click=lambda: setattr(st.session_state, 'page', 'home'))

    # 当前天气概览
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("当前温度", "26.5°C", "+1.5°C")
    col2.metric("相对湿度", "68%", "-2%")
    col3.metric("风速", "3.2 m/s", "西北风")
    col4.metric("降雨量", "0 mm", "过去24小时")

    # 天气预报
    st.subheader("未来7天天气预报")
    forecast_days = [(datetime.now() + timedelta(days=i)).strftime('%m/%d') for i in range(7)]
    forecast_data = {
        "日期": forecast_days,
        "天气": ["晴", "多云", "小雨", "晴", "多云", "晴", "晴"],
        "最高温": [28, 26, 24, 27, 26, 29, 30],
        "最低温": [18, 17, 16, 18, 17, 19, 20],
        "降雨概率": [10, 20, 60, 5, 15, 5, 5]
    }
    st.dataframe(forecast_data, use_container_width=True)

    # 气象数据图表
    st.subheader("气象数据趋势")

    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["温度变化", "降雨量", "风速"])

    with tab1:
        # 温度变化图
        hours = [f"{i}:00" for i in range(24)]
        temps = [20 + 8 * np.sin(i / 4) + random.uniform(-1, 1) for i in range(24)]
        fig = px.line(x=hours, y=temps, title="24小时温度变化趋势")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # 降雨量图
        days = [f"Day {i + 1}" for i in range(7)]
        rainfall = [random.randint(0, 15) for _ in range(7)]
        fig = px.bar(x=days, y=rainfall, title="未来7天降雨量预测 (mm)")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        # 风速风向图
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        speeds = [random.uniform(1, 8) for _ in directions]
        fig = px.bar_polar(r=speeds, theta=directions, title="风向风速分布")
        st.plotly_chart(fig, use_container_width=True)

    # 气象预警
    st.subheader("气象预警")
    with st.expander("查看预警详情"):
        st.warning("⚠️ 高温预警：预计未来三天日最高气温将在35°C以上")
        st.info("🌧️ 降雨提醒：预计周四有小到中雨，请合理安排灌溉计划")


def pest_health_page():
    st.header("🐛 病虫害与作物健康系统")
    st.info("监测作物健康状况，及时预警病虫害风险")
    st.button("⬅️ 返回主页", on_click=lambda: setattr(st.session_state, 'page', 'home'))

    # 健康评分
    col1, col2, col3 = st.columns(3)
    col1.metric("整体健康指数", "86/100", "+5%", delta_color="inverse")
    col2.metric("病虫害风险", "中等", "↓ 降低", delta_color="inverse")
    col3.metric("问题区域", "3处", "需处理")

    # 病虫害检测
    st.subheader("病虫害检测结果")

    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["病害识别", "虫害识别", "健康分析"])

    with tab1:
        st.write("### 常见病害检测")
        diseases = [
            {"name": "白粉病", "severity": "中度", "area": "B2区", "confidence": "92%"},
            {"name": "叶斑病", "severity": "轻度", "area": "A1区", "confidence": "85%"},
            {"name": "枯萎病", "severity": "低风险", "area": "C3区", "confidence": "78%"}
        ]

        for disease in diseases:
            with st.expander(f"{disease['name']} - {disease['severity']}"):
                st.write(f"**区域**: {disease['area']}")
                st.write(f"**置信度**: {disease['confidence']}")
                st.progress(int(disease['confidence'][:-1]), text="检测置信度")
                st.button(f"查看{disease['name']}详情", key=f"btn_{disease['name']}")

    with tab2:
        st.write("### 常见虫害检测")
        pests = [
            {"name": "蚜虫", "severity": "高度", "area": "A2区", "count": "150+",
             "image": "https://images.unsplash.com/photo-1587049633312-d628ae50a8ae?w=400"},
            {"name": "红蜘蛛", "severity": "中度", "area": "B3区", "count": "80+",
             "image": "https://images.unsplash.com/photo-1617791160536-598cf32026fb?w=400"},
            {"name": "棉铃虫", "severity": "低度", "area": "C1区", "count": "20+",
             "image": "https://images.unsplash.com/photo-1551651057-f1caae7c6f39?w=400"}
        ]

        for pest in pests:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(pest["image"], width=100)
            with col2:
                st.write(f"**{pest['name']}** ({pest['severity']}风险)")
                st.write(f"区域: {pest['area']} | 数量: {pest['count']}")
                st.progress(70 if pest['severity'] == '高度' else 50 if pest['severity'] == '中度' else 30,
                            text=f"风险等级: {pest['severity']}")

    with tab3:
        st.write("### 作物健康分析")

        # 健康分布图
        health_data = {
            "区域": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "健康指数": [92, 85, 78, 88, 90, 82],
            "叶绿素含量": [42, 38, 35, 40, 41, 37],
            "病虫害指数": [12, 25, 35, 18, 15, 28]
        }
        st.dataframe(health_data, use_container_width=True)

        # 健康热力图
        st.write("#### 健康指数热力图")
        fig = px.imshow(
            [[92, 85], [78, 88], [90, 82]],
            labels=dict(x="列", y="行", color="健康指数"),
            x=['A', 'B'],
            y=['1', '2', '3'],
            color_continuous_scale='greens'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 防治建议
    st.subheader("防治建议")
    st.success("✅ 推荐措施：")
    st.write("- 对B2区进行生物防治，使用瓢虫控制蚜虫")
    st.write("- A1区叶斑病建议使用低毒杀菌剂")
    st.write("- 加强C3区排水，预防枯萎病扩散")


def current_qa_page():
    st.header("📝 智能农业实时询问助手")
    st.info("此页面汇总各子系统信息，给予农户实时建议")
    st.button("⬅️ 返回主页", on_click=lambda: setattr(st.session_state, 'page', 'home'))

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summaries = generate_all_summaries()
    full_data = ''.join(summaries)

    full_prompt_template = """
    ### 智能农业助手系统提示
    **当前时间**: {current_time}
    **系统角色**: 您是一位专业的农业顾问，拥有作物种植、病虫害防治和农业管理的专业知识。
    **任务要求**: 请基于以下农场实时监测数据，提供专业的农业建议和分析。

    #### 农场监测数据摘要
    {current_data}

    #### 用户问题：{query}
    """

    st.divider()
    st.subheader("🤖 智能问答")

    if "current_messages" not in st.session_state:
        st.session_state.current_messages = []

    display_chat_history()

    if query := st.chat_input("请输入您的问题"):
        prompt = full_prompt_template.format(
            current_time=current_time,
            current_data=full_data,
            query=query
        )


        append_message("user", query)
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            response = st.write_stream(
                st.session_state.current_llm.generate_response(prompt)
            )
            if response:
                append_message("assistant", response)


def append_message(role, content):
    st.session_state.current_messages.append({
        "role": role,
        "content": content
    })


def display_chat_history():
    for message in st.session_state.current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])



def get_video_summary():
    return """
    ####  视频监控系统摘要
    - **东区作物生长情况**:
      温度: 28.5°C (+1.2°C变化)
      湿度: 65% (-3%变化)
      光照强度: 8500 lux (稳定)
      作物生长进度: 75%

    - **西区灌溉系统状态**:
      区域A: 运行中 (35%)
      区域B: 待机
      区域C: 运行中 (70%)
      区域D: 故障

    - **南区设备状态**:
      无人机1: 在线 (78%电量)
      传感器节点5: 离线
      水泵3: 在线 (92%电量)
      气象站2: 在线 (65%电量)
    """


def get_soil_summary():
    return """
    #### 土壤监测系统摘要
    - **土壤湿度**:
      过去24小时变化趋势: 整体稳定在20-40%之间
      区域分布: 
        A1: 32.5% | A2: 28.7% 
        B1: 35.2% | B2: 38.1%
        C1: 29.8% | C2: 33.4%

    - **土壤养分比例**:
      氮(N): 1.8 g/kg
      磷(P): 1.5 g/kg
      钾(K): 2.1 g/kg
      有机质: 3.0%

    - **土壤温度**:
      0-10cm: 25.3°C | 10-20cm: 23.8°C
      20-30cm: 22.1°C | 30-40cm: 20.7°C
    """


def get_weather_summary():
    return """
    #### 气象监测系统摘要
    - **当前天气**:
      温度: 26.5°C (+1.5°C变化)
      湿度: 68% (-2%变化)
      风速: 3.2 m/s (西北风)
      降雨量: 0 mm (过去24小时)

    - **天气预报**:
      今天: 晴, 18-28°C, 降雨概率10%
      明天: 多云, 17-26°C, 降雨概率20%
      后天: 小雨, 16-24°C, 降雨概率60%

    - **气象预警**:
      高温预警: 预计未来三天日最高气温将在35°C以上
      降雨提醒: 周四有小到中雨
    """


def get_pest_summary():
    return """
    #### 病虫害监测系统摘要
    - **作物健康概况**:
      整体健康指数: 86/100 (+5%提升)
      病虫害风险: 中等 (↓降低趋势)
      问题区域: 3处需处理

    - **病害检测**:
      白粉病: 中度 (B2区, 92%置信度)
      叶斑病: 轻度 (A1区, 85%置信度)
      枯萎病: 低风险 (C3区, 78%置信度)

    - **虫害检测**:
      蚜虫: 高度风险 (A2区, 150+只)
      红蜘蛛: 中度风险 (B3区, 80+只)
      棉铃虫: 低度风险 (C1区, 20+只)

    - **防治建议**:
      1. B2区进行生物防治，使用瓢虫控制蚜虫
      2. A1区叶斑病建议使用低毒杀菌剂
      3. 加强C3区排水，预防枯萎病扩散
    """


def generate_all_summaries():
    return [
        get_video_summary(),
        get_soil_summary(),
        get_weather_summary(),
        get_pest_summary()
    ]


