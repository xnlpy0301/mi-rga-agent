import os
import streamlit as st
from LLM_service import Config, VectorStoreManager, DocumentProcessor, RAGLLM, LLM
from function_pages import video_surveillance_page, soil_monitoring_page, weather_monitoring_page, pest_health_page, \
    document_qa_page, current_qa_page


def apply_custom_css():
    st.markdown("""
        <style>
            /* 整体样式 */

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


# def display_custom_buttons(features):
#     # 添加无边框、带背景色的气泡风格卡片
#     st.markdown("""
#     <style>
#         /* 增大标题字体 */
#         h3 {
#             font-size: 1.5rem !important;
#             text-align: center !important;
#             margin-bottom: 12px !important;
#             color: #2e7d32 !important; /* 深绿色标题 */
#         }
#         /* 浅绿色按钮 - 方形设计 */
#         div.stButton > button:first-child {
#             background-color: rgba(230, 247, 255, 0.8) !important; /* 浅绿色背景 */
#             border: none !important;
#             color: #2e7d32 !important; /* 深绿色文字 */
#             border-radius: 15px !important;
#             transition: all 0.3s ease !important;
#             box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
#             font-size: 0.95rem !important;
#             padding: 20px !important;
#             text-align: center !important;
#             height: 120px !important;
#             min-width: 120px !important;
#             display: flex !important;
#             align-items: center !important;
#             justify-content: center !important;
#             flex-direction: column !important;
#         }
#         /* 鼠标悬停效果 */
#         div.stButton > button:hover {
#             background-color: rgba(200, 230, 201, 0.9) !important; /* 稍深的浅绿色 */
#             transform: translateY(-2px) !important;
#             box-shadow: 0 6px 12px rgba(46, 125, 50, 0.15) !important; /* 绿色阴影 */
#         }
#         /* 气泡风格卡片 - 无边框，有背景色 */
#         div[data-testid="stVerticalBlock"] > div[style*="border"] {
#             border: none !important;
#             border-radius: 20px !important;
#             background-color: #e8f5e9 !important; /* 浅绿色背景 */
#             box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08) !important;
#             padding: 20px !important;
#             text-align: center !important;
#             position: relative !important;
#             margin: 10px 5px 20px 5px !important;
#             transition: all 0.3s ease !important;
#         }
#         /* 气泡悬停效果 */
#         div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
#             transform: translateY(-5px) !important;
#             box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12) !important;
#             background-color: #c8e6c9 !important; /* 悬停时背景色稍深的绿色 */
#         }
#         /* 按钮内图标和文字样式 */
#         div.stButton > button span {
#             display: block !important;
#             width: 100% !important;
#         }
#     </style>
#     """, unsafe_allow_html=True)
#     cols = st.columns(2)
#     for idx, feature in enumerate(features):
#         with cols[idx % 2]:
#             # 按钮中显示描述文字
#             if st.button(
#                     f"{feature['icon']}\n{feature['title']}",  # 添加换行使图标和文字垂直排列
#                     key=f"btn_{feature['page']}",
#                     use_container_width=True
#             ):
#                 st.session_state.page = feature['page']
#                 st.rerun()


def display_custom_buttons(features):
    # 添加更强气泡风格的卡片和居中文本样式
    st.markdown("""
        <style>
            /* 增大标题字体 - 黑色 */
            h3 {
                font-size: 1.5rem !important;
                text-align: center !important;
                margin-bottom: 12px !important;
                color: #000000 !important;
            }
            /* 浅绿色按钮 */
            div.stButton > button:first-child {
                background-color: rgba(230, 247, 230, 0.8) !important;
                border-color: rgba(145, 213, 145, 0.5) !important;
                color: #18a018 !important;
                border-radius: 25px !important;
                backdrop-filter: blur(5px) !important;
                transition: all 0.3s ease !important;
            }
            /* 鼠标悬停效果 */
            div.stButton > button:hover {
                background-color: rgba(186, 231, 186, 0.9) !important;
                border-color: #69c069 !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 12px rgba(24, 160, 24, 0.15) !important;
            }
            /* 气泡风格卡片 - 增强边框阴影效果 */
            div[data-testid="stVerticalBlock"] > div[style*="border"] {
                border-radius: 30px !important;
                background: linear-gradient(145deg, #e6f7ff, #f0f9ff) !important;
                box-shadow:
                    0 10px 20px rgba(0, 0, 0, 0.15),
                    0 0 0 1px rgba(0, 0, 0, 0.05),
                    inset 0 -5px 12px rgba(255, 255, 255, 0.7),
                    inset 0 5px 12px rgba(255, 255, 255, 0.7) !important;
                padding: 20px !important;
                text-align: center !important;
                position: relative !important;
                border: none !important;
                backdrop-filter: blur(5px) !important;
                margin: 10px 5px 20px 5px !important;
                transition: all 0.3s ease !important;
            }
            /* 气泡悬停效果 - 增强阴影 */
            div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
                transform: translateY(-5px) !important;
                box-shadow:
                    0 15px 30px rgba(0, 0, 0, 0.25),
                    0 0 0 1px rgba(0, 0, 0, 0.08),
                    inset 0 -5px 12px rgba(255, 255, 255, 0.7),
                    inset 0 5px 12px rgba(255, 255, 255, 0.7) !important;
            }
            /* 描述文本居中 */
            .centered-text {
                text-align: center !important;
                margin-bottom: 20px !important;
                color: #555 !important;
                font-size: 0.95rem !important;
                line-height: 1.5 !important;
            }
            /* 添加气泡小装饰 */
            .bubble-card::before {
                content: "" !important;
                position: absolute !important;
                top: 10px !important;
                right: 10px !important;
                width: 15px !important;
                height: 15px !important;
                border-radius: 50% !important;
                background: rgba(255, 255, 255, 0.7) !important;
            }
            .bubble-card::after {
                content: "" !important;
                position: absolute !important;
                top: 25px !important;
                right: 25px !important;
                width: 8px !important;
                height: 8px !important;
                border-radius: 50% !important;
                background: rgba(255, 255, 255, 0.9) !important;
            }
        </style>
        """, unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, feature in enumerate(features):
        with cols[idx % 2]:
            with st.container(border=True):
                # 添加气泡装饰类
                st.markdown('<div class="bubble-card"></div>', unsafe_allow_html=True)
                # 使用h3标签增大标题并居中
                st.markdown(
                    f"<h3>{feature['icon']} {feature['title']}</h3>",
                    unsafe_allow_html=True
                )
                # 描述文本居中
                st.markdown(f"<div class='centered-text'>{feature['desc']}</div>",
                            unsafe_allow_html=True)
                # 气泡风格按钮
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
        {"icon": "🎥", "title": "农田实况监控", "desc": "高清监控与作物生长状态分析", "page": "video"},
        {"icon": "🧪", "title": "土壤监测", "desc": "土壤墒情与肥力实时监测", "page": "soil"},
        {"icon": "🌦️", "title": "气象监测", "desc": "精准天气预警与灾害预防方案", "page": "weather"},
        {"icon": "🐛", "title": "病虫害监测", "desc": "智能识别与防治方案推荐", "page": "pest"},
        {"icon": "🌱", "title": "农场智能助手", "desc": "结合实时农场数据提供最优决策建议", "page": "current_qa"},
        {"icon": "📚", "title": "农业百科助手", "desc": "权威农业知识与技术资料库", "page": "document_qa"}
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