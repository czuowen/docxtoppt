import streamlit as st
import os
import tempfile
from src.parser import QuizParser
from src.renderer import QuizRenderer

# 1. Page Config & CSS
st.set_page_config(page_title="山海寻梦 | 课件转换器", page_icon="🎨", layout="centered")

# Custom UI Styling (High-Fidelity Glassmorphism)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        font-family: 'Outfit', sans-serif;
    }
    
    /* Center the container */
    .block-container {
        padding-top: 3rem;
        max-width: 700px;
    }

    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #eab308 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -2px;
        filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.3));
    }
    
    .sub-header {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 3rem;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Glass Card Style for Uploader */
    div[data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        padding: 40px !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: #6366f1 !important;
        background: rgba(99, 102, 241, 0.05) !important;
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.1);
    }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        width: 100%;
        border-radius: 14px !important;
        height: 3.5rem;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border: none !important;
        margin-top: 20px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.5);
    }
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 20px 30px -5px rgba(79, 70, 229, 0.6);
    }

    /* Download Button Specific */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.4);
    }

    /* Info/Status blocks */
    .stAlert {
        border-radius: 15px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(5px);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Main UI
st.markdown('<h1 class="main-header">山海寻梦</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">专业 Docx 转交互式 Quiz PPT 转换器</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("点击或拖拽上传您的 Word 文档 (.docx)", type=["docx"])

if uploaded_file is not None:
    st.info(f"📄 已选择: {uploaded_file.name}")
    
    if st.button("🚀 开始转换"):
        with st.status("正在进行深度解析与排版...", expanded=True) as status:
            try:
                # Use temp files for cloud environment
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
                    tmp_in.write(uploaded_file.getvalue())
                    input_path = tmp_in.name
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp_out:
                    output_path = tmp_out.name

                st.write("🔍 分析文档结构...")
                parser = QuizParser()
                questions = parser.parse(input_path)
                
                if not questions:
                    st.error("❌ 未在文档中发现有效的试题内容，请检查格式。")
                    st.stop()
                
                st.write(f"✍️ 正在渲染 {len(questions)} 道题目...")
                renderer = QuizRenderer(output_path)
                renderer.create_title_slide()
                renderer.add_question_slides(questions)
                renderer.save()
                
                st.write("✨ 正在注入品牌标识与链接...")
                
                status.update(label="✅ 转换成功！", state="complete")
                
                # Provide download link
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="💎 立即获取您的精美课件 (PPTX)",
                        data=f,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                
                # Cleanup temp files
                os.unlink(input_path)
                # Note: output_path can't be unlinked before download button is clicked 
                # but streamlit handles memory files well if we use BytesIO. 
                # For simplicity here, we leave it in temp.
                
            except Exception as e:
                status.update(label="❌ 转换失败", state="error")
                st.error(f"错误详情: {str(e)}")

# 3. Footer
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("[🌐 访问官网](http://www.jxgqc.online)")
with col2:
    st.markdown("[📊 江西教育云](https://xxyd.jxeduyun.com/index)")
st.caption("© 2026 山海寻梦. 由 Antigravity AI 技术驱动")
