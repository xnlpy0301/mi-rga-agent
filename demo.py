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

            /* 按钮容器 */
            .button-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                max-width: 900px;
                margin: 0 auto;
            }

            /* 按钮样式 */
            .feature-button {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: white;
                border: none;
                border-radius: 16px;
                padding: 25px 15px;
                box-shadow: 0 6px 16px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                height: 180px;
                text-align: center;
                cursor: pointer;
            }

            .feature-button:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(46, 139, 87, 0.25);
                background: linear-gradient(135deg, #ffffff 0%, #f0fff4 100%);
            }

            .feature-button .icon {
                font-size: 48px;
                margin-bottom: 15px;
            }

            .feature-button .title {
                font-size: 18px;
                font-weight: 600;
                color: #2c7744;
                margin-bottom: 8px;
            }

            .feature-button .desc {
                font-size: 14px;
                color: #5f7d95;
                max-width: 90%;
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
        page_title="农业智能系统",
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


def show_home():
    st.markdown('<div class="header"><h1>🌾 智慧农业智能系统</h1><p>科技助力现代农业，智能管理提高效率</p></div>',
                unsafe_allow_html=True)

    st.markdown("""
        <div style="max-width: 900px; margin: 0 auto 2rem auto; text-align: center;">
            <p style="font-size: 1.1rem; color: #4a6b7c;">
                覆盖农场全场景智能管理，从环境监测到作物健康，一站式解决方案
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="button-grid">', unsafe_allow_html=True)

    # 功能按钮定义
    features = [
        {"icon": "📄", "title": "文档问答", "desc": "农业知识库智能查询", "page": "document_qa"},
        {"icon": "🕒", "title": "实时农业助手", "desc": "即时解答农业生产问题", "page": "current_qa"},
        {"icon": "🎥", "title": "视频监控", "desc": "实时查看农田监控画面", "page": "video"},
        {"icon": "🧪", "title": "土壤监测", "desc": "土壤成分与湿度分析", "page": "soil"},
        {"icon": "🌦️", "title": "气象监测", "desc": "实时天气与灾害预警", "page": "weather"},
        {"icon": "🐛", "title": "病虫害监测", "desc": "作物健康与病虫害诊断", "page": "pest"}
    ]

    # 创建功能按钮
    for feature in features:
        with st.container():
            if st.markdown(f"""
                <div class="feature-button" onclick="window.streamlit:componentEvent('change_page', '{{'{feature["page"]}'}}')">
                    <div class="icon">{feature["icon"]}</div>
                    <div class="title">{feature["title"]}</div>
                    <div class="desc">{feature["desc"]}</div>
                </div>
            """, unsafe_allow_html=True):
                # 添加JavaScript处理
                st.write(f"""
                    <script>
                        window.addEventListener('load', function() {{
                            const buttons = document.querySelectorAll('.feature-button');
                            buttons.forEach(button => {{
                                button.addEventListener('click', function() {{
                                    const page = this.getAttribute('onclick').match(/'([^']+)'/)[1];
                                    window.streamlit:componentEvent('change_page', page);
                                }});
                            }});
                        }});
                    </script>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 添加页脚
    st.markdown("""
        <div class="footer">
            <p>智慧农业系统 © 2025 | 科技赋能农业，助力乡村振兴</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()