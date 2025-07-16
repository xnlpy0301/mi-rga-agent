import os

import streamlit as st

from LLM_service import Config,  VectorStoreManager, DocumentProcessor, RAGLLM, LLM
from function_pages import video_surveillance_page, soil_monitoring_page, weather_monitoring_page, pest_health_page, \
    document_qa_page,current_qa_page

def apply_custom_css():
    st.markdown("""
        <style>
            .stButton > button {
                border: 1px solid #4CAF50;
                border-radius: 12px;
                background-color: #f0f9f4;
                color: #333333;
                font-weight: bold;
                padding: 12px 20px;
                margin: 5px 0px;
                font-size: 16px;
                min-width: 200px;
                height: 50px;
                transition: background-color 0.3s, color 0.3s, transform 0.2s;
            }
            .stButton > button:hover {
                background-color: #4CAF50;
                color: white;
                transform: scale(1.05);
            }
        </style>
    """, unsafe_allow_html=True)



def main():
    apply_custom_css()
    # 初始化配置和日志
    config = Config()


    os.makedirs(config.data_dir, exist_ok=True)

    if 'vs_manager' not in st.session_state:
        vs_manager = VectorStoreManager(config)
        st.session_state.vs_manager = vs_manager

        if vs_manager.is_empty():
            logger.info("向量数据库为空，开始加载初始文档...")
            processor = DocumentProcessor(config)
            documents = processor.load_and_split_documents()
            vs_manager.populate_collection(documents)

    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAGLLM(config, st.session_state.vs_manager)
    if 'current_llm' not in st.session_state:
        st.session_state.current_llm = LLM(config)

    st.set_page_config(page_title="农业智能系统", page_icon="🌾", layout="centered")

    # 初始化页面状态
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'document_qa':
        document_qa_page(config, logger)
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
    st.title("🌾 农业智能系统")
    st.subheader("💡 请选择以下功能模块：")
    st.caption("覆盖视频监控、土壤检测、气象监测与病虫害诊断等")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 文档问答"):
            st.session_state.page = 'document_qa'
    with col2:
        if st.button("🕒 实时农业助手"):
            st.session_state.page = 'current_qa'

    col3, col4 = st.columns(2)
    with col3:
        if st.button("🎥 视频监控"):
            st.session_state.page = 'video'
    with col4:
        if st.button("🧪 土壤监测"):
            st.session_state.page = 'soil'

    col5, col6 = st.columns(2)
    with col5:
        if st.button("🌦️ 气象监测"):
            st.session_state.page = 'weather'
    with col6:
        if st.button("🐛 病虫害监测"):
            st.session_state.page = 'pest'



if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()