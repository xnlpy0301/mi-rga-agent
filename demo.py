import os
import streamlit as st
from LLM_service import Config, VectorStoreManager, DocumentProcessor, RAGLLM, LLM
from function_pages import video_surveillance_page, soil_monitoring_page, weather_monitoring_page, pest_health_page, \
    document_qa_page, current_qa_page


def apply_custom_css():
    st.markdown("""
        <style>
            /* 整体样式 */
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
                background-attachment: fixed;
            }
            /* 标题样式 */
            .header {
                text-align: center;
                padding: 1.5rem 0;
                margin-bottom: 2rem;
                background: linear-gradient(90deg, #2c7744 0%, #5aaf70 100%);
                color: white;
                border-radius: 0 0 20px 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }
            /* 按钮容器 - 修复点击区域 */
            .button-container {
                position: relative;
                height: 220px;
                margin-bottom: 20px;
            }
            .custom-feature-button {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: white;
                border: none;
                border-radius: 16px;
                padding: 30px 20px;
                box-shadow: 0 6px 16px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                height: 100%;
                text-align: center;
                cursor: pointer;
            }
            /* 鼠标悬浮效果 */
            .custom-feature-button:hover {
                transform: translateY(-8px);
                box-shadow: 0 12px 30px rgba(46, 139, 87, 0.3);
                background: linear-gradient(135deg, #ffffff 0%, #e6fde6 100%);
            }
            /* 按钮图标 */
            .custom-feature-button .icon {
                font-size: 54px;
                margin-bottom: 20px;
            }
            /* 按钮标题 */
            .custom-feature-button .title {
                font-size: 20px;
                font-weight: 600;
                color: #2c7744;
                margin-bottom: 10px;
            }
            /* 按钮描述 */
            .custom-feature-button .desc {
                font-size: 16px;
                color: #5f7d95;
                max-width: 90%;
            }
            /* 透明按钮覆盖层 */
            .transparent-button {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                opacity: 0;
                cursor: pointer;
                z-index: 10;
            }
            /* 按钮网格布局 */
            .button-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                max-width: 900px;
                margin: 0 auto;
            }
            /* 页脚样式 */
            .footer {
                text-align: center;
                padding: 1.5rem 0;
                margin-top: 3rem;
                color: #6c757d;
                font-size: 0.9rem;
                border-top: 1px solid #eaeaea;
            }
        </style>
    """, unsafe_allow_html=True)


def display_custom_buttons(features):
    # 使用Streamlit的原生交互组件
    cols = st.columns(2)  # 创建两列布局

    for idx, feature in enumerate(features):
        with cols[idx % 2]:  # 每列交替放置按钮
            # 创建按钮容器
            container = st.container()
            container.markdown(
                f"""
                <div class="button-container">
                    <div class="custom-feature-button">
                        <div class="icon">{feature['icon']}</div>
                        <div class="title">{feature['title']}</div>
                        <div class="desc">{feature['desc']}</div>
                    </div>
                    <div class="transparent-button" id="btn_{feature['page']}"></div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # 添加按钮点击事件处理
            if container.button("", key=f"btn_{feature['page']}", use_container_width=True):
                st.session_state.page = feature['page']
                st.experimental_rerun()


def show_home():
    st.markdown(
        '<div class="header"><h1>🌾 米农智家IoT一站式解决方案</h1><p>科技助力现代农业，智能管理提高效率</p></div>',
        unsafe_allow_html=True)
    st.markdown("""
        <div style="max-width: 900px; margin: 0 auto 2rem auto; text-align: center;">
            <p style="font-size: 1.1rem; color: #4a6b7c;">
                覆盖农场全场景智能管理，从环境监测到作物健康，一站式解决方案
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 定义功能按钮
    features = [
        {"icon": "📄", "title": "农业百科助手", "desc": "农业知识库智能查询", "page": "document_qa"},
        {"icon": "🕒", "title": "实时农场助手", "desc": "即时解答农业生产问题", "page": "current_qa"},
        {"icon": "🎥", "title": "视频监控", "desc": "实时查看农田监控画面", "page": "video"},
        {"icon": "🧪", "title": "土壤监测", "desc": "土壤成分与湿度分析", "page": "soil"},
        {"icon": "🌦️", "title": "气象监测", "desc": "实时天气与灾害预警", "page": "weather"},
        {"icon": "🐛", "title": "病虫害监测", "desc": "作物健康与病虫害诊断", "page": "pest"}
    ]

    # 显示功能按钮
    display_custom_buttons(features)

    # 添加页脚
    st.markdown("""
        <div class="footer">
            <p>米家智慧农业系统 © 2025 | 科技赋能农业，助力乡村振兴</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    apply_custom_css()
    config = Config()
    os.makedirs(config.data_dir, exist_ok=True)

    # 初始化向量存储
    if 'vs_manager' not in st.session_state:
        vs_manager = VectorStoreManager(config)
        st.session_state.vs_manager = vs_manager
        if vs_manager.is_empty():
            processor = DocumentProcessor(config)
            documents = processor.load_and_split_documents()
            vs_manager.populate_collection(documents)

    # 初始化RAG系统
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAGLLM(config, st.session_state.vs_manager)

    # 初始化LLM
    if 'current_llm' not in st.session_state:
        st.session_state.current_llm = LLM(config)

    # 设置页面配置
    st.set_page_config(
        page_title="米农智家IoT一站式解决方案",
        page_icon="🌾",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # 初始化页面状态
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    # 页面路由
    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'document_qa':
        document_qa_page(config)
    elif st.session_state.page == 'current_qa':
        current_qa_page()
    elif st.session_state.page == 'video':
        video_surveillance_page()
    elif st.session_state.page == 'soil':
        soil_monitoring_page()
    elif st.session_state.page == 'weather':
        weather_monitoring_page()
    elif st.session_state.page == 'pest':
        pest_health_page()


if __name__ == "__main__":
    main()