import streamlit as st
import os
import tempfile
from src.parser import QuizParser
from src.renderer import QuizRenderer

# 1. Page Config & CSS
st.set_page_config(page_title="山海寻梦 | 课件转换器", page_icon="🎨", layout="centered")

# Custom UI Styling
st.markdown("""
    <style>
    .stApp {
        background: #0f172a;
        color: #f8fafc;
    }
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4f46e5, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    div.stButton > button {
        background-color: #4f46e5;
        color: white;
        width: 100%;
        border-radius: 12px;
        height: 3rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
    }
    div.stButton > button:hover {
        background-color: #4338ca;
        transform: translateY(-2px);
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
                parser = QuizParser(input_path)
                questions = parser.parse()
                
                if not questions:
                    st.error("❌ 未在文档中发现有效的试题内容，请检查格式。")
                    st.stop()
                
                st.write(f"✍️ 正在渲染 {len(questions)} 道题目...")
                renderer = QuizRenderer(output_path)
                renderer.add_title_slide(uploaded_file.name.replace(".docx", ""))
                renderer.add_question_slides(questions)
                renderer.save()
                
                st.write("✨ 正在注入品牌标识与链接...")
                
                status.update(label="✅ 转换成功！", state="complete")
                
                # Provide download link
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ 立即下载生成的 PPTX",
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
