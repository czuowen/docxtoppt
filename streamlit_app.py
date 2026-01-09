import streamlit as st
import os
import tempfile
from src.parser import QuizParser
from src.renderer import QuizRenderer

# 1. Page Config & CSS
st.set_page_config(page_title="山海寻梦 | 课件转换器", page_icon="🎨", layout="centered")

# Custom UI Styling (PDF2Go Style - Professional & Clean)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
    
    .stApp {
        background: #fdfdfd !important;
        font-family: 'Open Sans', sans-serif;
        color: #333;
    }
    
    /* Global Container */
    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }

    /* Header Section */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #c0392b; /* PDF2Go Red/Burgundy */
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    
    .sub-header {
        text-align: center;
        color: #7f8c8d;
        font-size: 1rem;
        margin-bottom: 2.5rem;
    }

    /* PDF2Go Style File Uploader Box */
    div[data-testid="stFileUploadDropzone"] {
        background: #f8f9fa !important;
        border: 2px dashed #bdc3c7 !important;
        border-radius: 8px !important;
        padding: 80px 40px !important;
        transition: all 0.2s ease;
        text-align: center;
    }
    div[data-testid="stFileUploadDropzone"]:hover {
        background: #fff !important;
        border-color: #c0392b !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Imitate the large central button look */
    div[data-testid="stFileUploadDropzone"] section button {
        background-color: #c0392b !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        padding: 15px 40px !important;
        font-size: 1.2rem !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }

    /* Action Buttons */
    div.stButton > button {
        background-color: #27ae60 !important; /* PDF2Go Successful Action Green */
        color: white !important;
        width: 100%;
        border-radius: 4px !important;
        height: 3.5rem;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border: none !important;
        margin-top: 20px;
        box-shadow: 0 4px 0 #219150;
        transition: transform 0.1s;
    }
    div.stButton > button:hover {
        transform: translateY(2px);
        box-shadow: 0 2px 0 #219150;
    }
    div.stButton > button:active {
        box-shadow: none;
        transform: translateY(4px);
    }

    /* Status Blocks */
    .stAlert {
        border-radius: 4px !important;
        border-left: 5px solid #c0392b !important;
    }

    /* Footer / Branding */
    .footer-area {
        margin-top: 50px;
        border-top: 1px solid #eee;
        padding-top: 20px;
        text-align: center;
        font-size: 0.9rem;
        color: #95a5a6;
    }
    .footer-links a {
        color: #2980b9;
        text-decoration: none;
        margin: 0 15px;
        font-weight: 600;
    }
    .footer-links a:hover { text-decoration: underline; }

    /* Hide Streamlit components */
    [data-testid="stHeader"] { background: #fff !important; border-bottom: 1px solid #eee; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 2. Main UI
st.markdown('<h1 class="main-header">山海寻梦 · 课件编辑器</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">高效、自动的 Docx 转 PPT 转换工具</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("选择文件或将其拖放到此处", type=["docx"])

if uploaded_file is not None:
    st.success(f"已就绪: {uploaded_file.name}")
    
    if st.button("立即转换"):
        with st.status("正在处理中...", expanded=True) as status:
            try:
                # Use temp files for cloud environment
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
                    tmp_in.write(uploaded_file.getvalue())
                    input_path = tmp_in.name
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp_out:
                    output_path = tmp_out.name

                st.write("🏃 开始解析文档...")
                parser = QuizParser()
                questions = parser.parse(input_path)
                
                if not questions:
                    st.error("❌ 未发现试题，请确认文档内容。")
                    st.stop()
                
                st.write(f"🎨 正在应用专业排版 ({len(questions)} 道题)...")
                renderer = QuizRenderer(output_path)
                renderer.create_title_slide()
                renderer.add_question_slides(questions)
                renderer.save()
                
                status.update(label="✅ 任务完成！", state="complete")
                
                # Provide download link
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ 免费下载生成的 PPTX 文件",
                        data=f,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                
                os.unlink(input_path)
            except Exception as e:
                status.update(label="❌ 发生错误", state="error")
                st.error(f"分析失败: {str(e)}")

# 3. Footer
st.markdown("""
    <div class="footer-area">
        <div class="footer-links">
            <a href="http://www.jxgqc.online" target="_blank">官方网站</a>
            <a href="https://xxyd.jxeduyun.com/index" target="_blank">江西教育云平台</a>
        </div>
        <p>© 2026 山海寻梦. 无需注册，完全免费的在线转换工具。</p>
    </div>
    """, unsafe_allow_html=True)
