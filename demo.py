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
            .custom-feature-button {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: white;
                border: none;
                border-radius: 16px;
                padding: 30px 20px; /* 增加按钮内边距 */
                box-shadow: 0 6px 16px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                height: 220px; /* 增加按钮高度 */
                text-align: center;
                cursor: pointer;
                position: relative; /* 添加相对定位 */
            }
            /* 鼠标悬浮效果 */
            .custom-feature-button:hover {
                transform: translateY(-8px); /* 按钮轻微上升 */
                box-shadow: 0 12px 30px rgba(46, 139, 87, 0.3); /* 增强阴影效果 */
                background: linear-gradient(135deg, #ffffff 0%, #e6fde6 100%);
            }
            /* 按钮图标 */
            .custom-feature-button .icon {
                font-size: 54px; /* 增大图标尺寸 */
                margin-bottom: 20px;
            }
            /* 按钮标题 */
            .custom-feature-button .title {
                font-size: 20px; /* 增大标题字体 */
                font-weight: 600;
                color: #2c7744;
                margin-bottom: 10px;
            }
            /* 按钮描述 */
            .custom-feature-button .desc {
                font-size: 16px; /* 增大描述字体 */
                color: #5f7d95;
                max-width: 90%;
            }
            /* 解决方案1: 只针对功能按钮的透明按钮 */
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


def display_custom_buttons(features):
    # 添加浅蓝色按钮样式（只需一次）
    st.markdown("""
    <style>
        /* 增大标题字体 */
        h3 {
            font-size: 1.5rem !important;
        }

        /* 浅蓝色按钮 */
        div.stButton > button:first-child {
            background-color: #e6f7ff !important;
            border-color: #91d5ff !important;
            color: #1890ff !important;
        }

        /* 鼠标悬停效果 */
        div.stButton > button:hover {
            background-color: #bae7ff !important;
            border-color: #69c0ff !important;
        }

        /* 卡片圆角效果 */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, feature in enumerate(features):
        with cols[idx % 2]:
            with st.container(border=True):
                # 使用h3标签增大标题
                st.markdown(
                    f"<h3 style='margin-bottom: 8px;'>{feature['icon']} {feature['title']}</h3>",
                    unsafe_allow_html=True
                )

                # 描述文本
                st.markdown(f"<div style='margin-bottom: 16px;'>{feature['desc']}</div>",
                            unsafe_allow_html=True)

                # 浅蓝色按钮
                if st.button(
                        f"立即体验",
                        key=f"btn_{feature['page']}",
                        use_container_width=True
                ):
                    st.session_state.page = feature['page']
                    st.rerun()

                # 添加底部间距
                st.write("")


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
        {"icon": "🌱", "title": "农场智能助手", "desc": "结合实时农场数据提供最优决策建议", "page": "current_qa"},
        {"icon": "📚", "title": "农业百科助手", "desc": "权威农业知识与技术资料库", "page": "document_qa"},
        {"icon": "🎥", "title": "农田实况监控", "desc": "高清监控与作物生长状态分析", "page": "video"},
        {"icon": "🧪", "title": "土壤监测", "desc": "土壤墒情与肥力实时监测", "page": "soil"},
        {"icon": "🌦️", "title": "气象监测", "desc": "精准天气预警与灾害预防方案", "page": "weather"},
        {"icon": "🐛", "title": "病虫害监测", "desc": "智能识别与防治方案推荐", "page": "pest"},
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