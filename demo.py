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
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            /* 功能按钮容器 - 修复重叠问题 */
            .custom-button-container {
                position: relative;
                width: 100%;
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
                height: 220px;
                text-align: center;
                cursor: pointer;
                position: relative;
                overflow: hidden; /* 防止内容溢出 */
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
                margin-bottom: 15px; /* 减少间距 */
                color: #2c7744;
            }
            /* 按钮标题 */
            .custom-feature-button .title {
                font-size: 20px;
                font-weight: 600;
                color: #2c7744;
                margin-bottom: 8px; /* 减少间距 */
                line-height: 1.3; /* 更好的行高 */
            }
            /* 按钮描述 */
            .custom-feature-button .desc {
                font-size: 16px;
                color: #5f7d95;
                max-width: 90%;
                line-height: 1.5; /* 更好的行高 */
                padding: 0 10px; /* 添加内边距 */
            }
            /* 透明按钮样式 */
            .custom-button-container .stButton button {
                position: absolute;
                width: 100%;
                height: 100%;
                left: 0;
                top: 0;
                opacity: 0;
                z-index: 10;
            }

            /* 按钮容器 */
            .button-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 25px; /* 增加间距 */
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

            /* 响应式调整 */
            @media (max-width: 768px) {
                .button-grid {
                    grid-template-columns: 1fr;
                }
                .custom-feature-button {
                    height: auto;
                    min-height: 180px;
                }
            }
        </style>
    """, unsafe_allow_html=True)


def display_custom_buttons(features):
    # 创建网格容器
    st.markdown('<div class="button-grid">', unsafe_allow_html=True)

    for feature in features:
        # 为每个按钮创建容器
        container = st.container()
        with container:
            # 添加包裹容器
            st.markdown('<div class="custom-button-container">', unsafe_allow_html=True)

            # 功能按钮内容
            st.markdown(f"""
                <div class="custom-feature-button">
                    <div class="icon">{feature['icon']}</div>
                    <div class="title">{feature['title']}</div>
                    <div class="desc">{feature['desc']}</div>
                </div>
            """, unsafe_allow_html=True)

            # 透明按钮
            if st.button("", key=f"btn_{feature['page']}"):
                st.session_state.page = feature['page']
                st.rerun()

            # 关闭包裹容器
            st.markdown('</div>', unsafe_allow_html=True)

    # 关闭网格容器
    st.markdown('</div>', unsafe_allow_html=True)



def show_home():
    st.markdown('<div class="header"><h1>🌾 米农智家IoT一站式解决方案</h1><p>科技助力现代农业，智能管理提高效率</p></div>',
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
    if 'vs_manager' not in st.session_state:
        vs_manager = VectorStoreManager(config)
        st.session_state.vs_manager = vs_manager
        if vs_manager.is_empty():
            processor = DocumentProcessor(config)
            documents = processor.load_and_split_documents()
            vs_manager.populate_collection(documents)
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAGLLM(config, st.session_state.vs_manager)
    if 'current_llm' not in st.session_state:
        st.session_state.current_llm = LLM(config)
    st.set_page_config(
        page_title="米农智家IoT一站式解决方案",
        page_icon="🌾",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    # 初始化页面状态
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
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
    # 添加页面切换后的重运行
    if 'prev_page' not in st.session_state:
        st.session_state.prev_page = st.session_state.page
    if st.session_state.prev_page != st.session_state.page:
        st.session_state.prev_page = st.session_state.page
        st.rerun()


if __name__ == "__main__":
    main()