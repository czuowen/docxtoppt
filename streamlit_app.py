import streamlit as st
import os
import tempfile
from src.parser import QuizParser
from src.renderer import QuizRenderer

# 1. Page Config & CSS
st.set_page_config(page_title="山海寻梦 | 课件转换器", page_icon="🎨", layout="centered")

# Custom UI Styling (High-Fidelity Glassmorphism + Dynamic Canvas)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    .stApp {
        background: transparent !important;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Background Layer */
    #canvas-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        background: #020617;
    }

    /* Center the container and make it look premium */
    .block-container {
        padding-top: 3rem;
        max-width: 700px;
        z-index: 10;
    }

    .main-header {
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -3px;
        filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.4));
        animation: glow 3s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.2)); }
        to { filter: drop-shadow(0 0 25px rgba(99, 102, 241, 0.5)); }
    }

    .sub-header {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 3.5rem;
        font-weight: 300;
        letter-spacing: 4px;
        text-transform: uppercase;
        opacity: 0.8;
    }

    /* Glass Card Style for Uploader */
    div[data-testid="stFileUploadDropzone"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        padding: 50px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: rgba(99, 102, 241, 0.5) !important;
        background: rgba(15, 23, 42, 0.7) !important;
        box-shadow: 0 0 40px rgba(99, 102, 241, 0.15);
        transform: scale(1.01);
    }

    /* Meta Info at Bottom */
    .stMarkdown p {
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        width: 100%;
        border-radius: 16px !important;
        height: 4rem;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        border: none !important;
        margin-top: 30px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 15px 30px -10px rgba(99, 102, 241, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 25px 40px -10px rgba(99, 102, 241, 0.7);
    }

    /* Download Button Specific */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #06b6d4 0%, #10b981 100%) !important;
        box-shadow: 0 15px 30px -10px rgba(16, 185, 129, 0.5);
    }

    /* Sidebar and Widgets */
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    </style>

    <canvas id="canvas-bg"></canvas>

    <script>
    const canvas = document.getElementById('canvas-bg');
    const ctx = canvas.getContext('2d');
    let w, h, particles;

    const options = {
        particleColor: 'rgba(255, 255, 255, 0.2)',
        lineColor: 'rgba(99, 102, 241, 0.1)',
        particleAmount: 80,
        defaultRadius: 1,
        variantRadius: 2,
        defaultSpeed: 0.3,
        variantSpeed: 0.5,
        linkRadius: 150
    };

    function init() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
        particles = [];
        for (let i = 0; i < options.particleAmount; i++) {
            particles.push(new Particle());
        }
    }

    class Particle {
        constructor() {
            this.x = Math.random() * w;
            this.y = Math.random() * h;
            this.speed = options.defaultSpeed + Math.random() * options.variantSpeed;
            this.directionAngle = Math.floor(Math.random() * 360);
            this.color = options.particleColor;
            this.radius = options.defaultRadius + Math.random() * options.variantRadius;
            this.vector = {
                x: Math.cos(this.directionAngle) * this.speed,
                y: Math.sin(this.directionAngle) * this.speed
            };
        }
        update() {
            this.border();
            this.x += this.vector.x;
            this.y += this.vector.y;
        }
        border() {
            if (this.x >= w || this.x <= 0) this.vector.x *= -1;
            if (this.y >= h || this.y <= 0) this.vector.y *= -1;
            if (this.x > w) this.x = w;
            if (this.y > h) this.y = h;
            if (this.x < 0) this.x = 0;
            if (this.y < 0) this.y = 0;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.closePath();
            ctx.fillStyle = this.color;
            ctx.fill();
        }
    }

    function linkPoints(point, hub) {
        for (let i = 0; i < hub.length; i++) {
            let distance = Math.sqrt(Math.pow(point.x - hub[i].x, 2) + Math.pow(point.y - hub[i].y, 2));
            let opacity = 1 - distance / options.linkRadius;
            if (opacity > 0) {
                ctx.lineWidth = 0.5;
                ctx.strokeStyle = `rgba(99, 102, 241, ${opacity * 0.3})`;
                ctx.beginPath();
                ctx.moveTo(point.x, point.y);
                ctx.lineTo(hub[i].x, hub[i].y);
                ctx.closePath();
                ctx.stroke();
            }
        }
    }

    function loop() {
        ctx.clearRect(0, 0, w, h);
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
            linkPoints(particles[i], particles);
        }
        requestAnimationFrame(loop);
    }

    init();
    loop();

    window.addEventListener('resize', init);
    </script>
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
