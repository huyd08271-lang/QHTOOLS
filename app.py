import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG TỔNG THỂ ---
st.set_page_config(page_title="AI Story Studio Pro", page_icon="✒️", layout="wide")

# --- HÀM TẠO CỬA SỔ POPUP ĐỌC TRUYỆN (ZOOM MODE) ---
@st.dialog("📖 Chế độ đọc tập trung (Toàn màn hình)", width="large")
def open_reading_mode(content):
    st.markdown(
        """
        <style>
            div[data-testid="stDialog"] .stMarkdown p {
                font-size: 22px !important;
                line-height: 1.8 !important;
                color: #0f172a !important;
            }
            div[data-testid="stDialog"] .stMarkdown h3 {
                font-size: 32px !important;
                color: #1e3a8a !important;
                margin-top: 20px !important;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 10px;
            }
        </style>
        """, unsafe_allow_html=True
    )
    st.markdown(content)

# --- CSS TÙY CHỈNH GIAO DIỆN ---
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3b82f6 !important;
        background-color: #ffffff !important;
    }
    [data-testid="stFormSubmitButton"] button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        height: 80px !important; 
        background-color: #eff6ff !important;
        border: 1px solid #bfdbfe !important;
        color: #1d4ed8 !important;
        transition: all 0.2s ease-in-out !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #dbeafe !important;
        transform: translateY(-2px);
    }
    .history-text p {
        font-size: 17px !important;
        line-height: 1.7 !important;
    }
    .chat-box {
        background-color: #f1f5f9;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 15px;
        font-size: 14px;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# --- BIẾN TRẠNG THÁI (STATE) ---
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

if 'stories' not in st.session_state:
    st.session_state.stories = {
        "Dự án Truyện 1": {
            "notes": "",
            "plot": "",
            "content": "",
            "latest_suggestion": "",
            "plot_chat_history": "", # Lưu lịch sử hội ý cốt truyện tổng thể
            "chap_chat_history": ""  # Lưu lịch sử hội ý viết chương
        }
    }
if 'current_story' not in st.session_state:
    st.session_state.current_story = "Dự án Truyện 1"

# --- THANH CÔNG CỤ BÊN TRÁI (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3131/3131610.png", width=60)
    st.header("Kho Lưu Trữ")
    
    story_names = list(st.session_state.stories.keys())
    selected_story = st.selectbox("Dự án đang mở:", story_names, index=story_names.index(st.session_state.current_story))
    st.session_state.current_story = selected_story
    
    st.divider()
    
    st.subheader("Bản Thảo Mới")
    new_story_name = st.text_input("Tên tác phẩm:")
    if st.button("➕ Khởi tạo dự án", use_container_width=True):
        if new_story_name and new_story_name not in st.session_state.stories:
            st.session_state.stories[new_story_name] = {
                "notes": "",
                "plot": "",
                "content": "",
                "latest_suggestion": "",
                "plot_chat_history": "",
                "chap_chat_history": ""
            }
            st.session_state.current_story = new_story_name
            st.rerun()
            
    st.divider()
    st.subheader("Hệ Thống Trí Tuệ")
    st.session_state.api_key = st.text_input("API Key (Gemini):", type="password", value=st.session_state.api_key)

# --- KHÔNG GIAN LÀM VIỆC CHÍNH ---
current_data = st.session_state.stories[st.session_state.current_story]
for key in ["plot", "latest_suggestion", "plot_chat_history", "chap_chat_history"]:
    if key not in current_data:
        current_data[key] = ""

st.title(f"📖 {st.session_state.current_story}")
st.markdown("---")

# ================= QUẢN LÝ CỐT TRUYỆN TỔNG THỂ (CHIA 2 PHẦN) =================
st.markdown("### 🗺️ Quản Lý Cốt Truyện Tổng Thể")
plot_col_chat, plot_col_main = st.columns(2, gap="large")

with plot_col_chat:
    st.markdown("💬 **Phần 1: Hội ý & Brainstorm Cốt Truyện với AI**")
    plot_idea = st.text_area("Trao đổi ý tưởng, thảo luận hướng đi tổng thể:", key="plot_idea_input", height=120, placeholder="Ví dụ: Theo ông phân đoạn đầu cho nhân vật chính gặp biến cố gì thì hợp lý?")
    
    if st.button("💡 Gửi Hội Ý Cốt Truyện", use_container_width=True):
        if not st.session_state.api_key:
            st.error("⚠️ Chưa có API Key!")
        elif not plot_idea:
            st.warning("⚠️ Hãy nhập nội dung cần hội ý.")
        else:
            try:
                genai.configure(api_key=st.session_state.api_key)
                model = genai.GenerativeModel('gemini-3.6-flash')
                chat_prompt = f"Với vai trò là trợ lý sáng tác kịch bản, hãy cùng tác giả thảo luận và góp ý cho ý tưởng tổng thể sau:\n{plot_idea}"
                with st.spinner("AI đang phân tích ý tưởng..."):
                    res = model.generate_content(chat_prompt)
                current_data["plot_chat_history"] = f"**Hỏi:** {plot_idea}\n\n**AI Góp Ý:** {res.text}\n\n---\n" + current_data["plot_chat_history"]
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")
                
    if current_data["plot_chat_history"]:
        with st.container(height=180):
            st.markdown(f'<div class="history-text">{current_data["plot_chat_history"]}</div>', unsafe_allow_html=True)

with plot_col_main:
    st.markdown("📝 **Phần 2: Bản Chốt Sườn Cốt Truyện Chính**")
    updated_plot = st.text_area(
        "Nội dung cốt truyện chính thức (để AI đọc khi viết chương):", 
        value=current_data["plot"], 
        height=215, 
        max_chars=15000 
    )
    if st.button("💾 Lưu Bản Chốt Cốt Truyện", use_container_width=True):
        st.session_state.stories[st.session_state.current_story]["plot"] = updated_plot
        st.success("Đã lưu cốt truyện chính thức!")

st.markdown("---")

# CÀI ĐẶT CẤM KỴ
st.markdown("### 🚫 Giới Hạn Cấm Kỵ Chung")
updated_notes = st.text_area(
    "Nhập các quy tắc AI không được vi phạm:", 
    value=current_data["notes"], 
    height=100, 
    max_chars=15000
)
if st.button("💾 Lưu Ghi Chú Cấm Kỵ"):
    st.session_state.stories[st.session_state.current_story]["notes"] = updated_notes
    st.success("Đã lưu quy tắc cấm kỵ!")

st.markdown("---")

# ================= KHU VỰC SÁNG TÁC (CHIA 2 PHẦN) & LỊCH SỬ =================
col_compose, col_history = st.columns([6, 4], gap="large")

# CỘT BÊN PHẢI: LỊCH SỬ BẢN THẢO
with col_history:
    head_col1, head_col2 = st.columns([6, 4])
    with head_col1:
        st.markdown("### 📜 Lịch Sử Bản Thảo")
    with head_col2:
        if current_data["content"]:
            if st.button("🔍 Đọc Toàn Màn Hình", use_container_width=True):
                open_reading_mode(current_data["content"])

    if current_data["content"]:
        with st.container(height=550):
            st.markdown(f'<div class="history-text">{current_data["content"]}</div>', unsafe_allow_html=True)
            
        st.download_button(
            label="📥 Xuất File Bản Thảo (.txt)",
            data=current_data["content"],
            file_name=f"{st.session_state.current_story}_Draft.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Trang giấy còn trắng. Bản thảo sẽ xuất hiện ở đây sau khi sinh.")

# CỘT BÊN TRÁI: KHU VỰC SÁNG TÁC (CHIA THÀNH 2 PHẦN RÕ RỆT)
with col_compose:
    st.markdown("### ✨ Sáng Tác Chương Mới")
    
    if current_data["latest_suggestion"]:
        st.info(f"💡 **AI Gợi ý cho chương tiếp theo:**\n\n{current_data['latest_suggestion']}")
    
    # PHẦN 1: HỘI Ý & THẢO LUẬN KỊCH BẢN CHƯƠNG VỚI AI
    with st.expander("💬 Phần 1: Bấm vào đây để Hội ý kịch bản chương với AI (Nháp)", expanded=False):
        chap_idea = st.text_area("Trao đổi các tình tiết trong chương với AI:", key="chap_idea_input", placeholder="Ví dụ: Theo ông cuộc đối thoại giữa 2 nhân vật nên căng thẳng hay ẩn ý?")
        if st.button("💭 Gửi Hội Ý Chương Này"):
            if not st.session_state.api_key:
                st.error("⚠️ Chưa có API Key!")
            elif not chap_idea:
                st.warning("⚠️ Nhập nội dung hội ý.")
            else:
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    chat_p = f"Dựa trên cốt truyện tổng thể:\n{current_data['plot']}\n\nHãy thảo luận và góp ý cho ý tưởng viết chương sau của tác giả:\n{chap_idea}"
                    with st.spinner("AI đang thảo luận kịch bản..."):
                        res = model.generate_content(chat_p)
                    current_data["chap_chat_history"] = f"**Hỏi:** {chap_idea}\n\n**AI Góp Ý:** {res.text}\n\n---\n" + current_data["chap_chat_history"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                    
        if current_data["chap_chat_history"]:
            st.markdown("---")
            st.markdown(current_data["chap_chat_history"])

    # PHẦN 2: BẢN CHỐT ĐỂ GỬI LỆNH VIẾT CHƯƠNG CHÍNH THỨC
    st.markdown("📝 **Phần 2: Bản Chốt Kịch Bản Để Viết Chương**")
    with st.form("compose_form", clear_on_submit=True):
        chapter_title = st.text_input("Tên chương (VD: Chương 1: Bước ngoặt):", placeholder="Gõ tên chương vào đây...")
        prompt = st.text_area("Chốt diễn biến cốt lõi để AI tiến hành viết:", height=130, placeholder="Nhập phần chốt kịch bản để AI biên soạn thành chương truyện hoàn chỉnh...")
        
        submitted = st.form_submit_button("🚀 Kích Hoạt AI Viết Chương Chính Thức", use_container_width=True)
            
        if submitted:
            if not st.session_state.api_key:
                st.error("⚠️ Khóa API bị thiếu! Vui lòng điền ở menu bên trái.")
            elif not prompt:
                st.warning("⚠️ Vui lòng cung cấp phần chốt diễn biến để viết chương.")
            else:
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    model = genai.GenerativeModel('gemini-3.6-flash')
                        
                    system_prompt = f"""Bạn là một tiểu thuyết gia chuyên nghiệp.
                    
                    CỐT TRUYỆN CHÍNH (Bám sát cốt truyện này để định hướng diễn biến):
                    {current_data["plot"]}

                    ĐIỀU KIỆN CẤM KỴ & QUY TẮC (Tuyệt đối tuân thủ, không được viết sai):
                    {current_data["notes"]}
                    
                    TÓM TẮT CÁC CHƯƠNG TRƯỚC (Để giữ mạch truyện liền mạch):
                    {current_data["content"][-4000:]} 
                    
                    YÊU CẦU CHỐT CHO CHƯƠNG NÀY: Dựa vào bối cảnh và mạch truyện trên, hãy viết một chương truyện chi tiết.
                    Tên chương (nếu có): {chapter_title}
                    Phần chốt diễn biến: {prompt}
                    
                    QUAN TRỌNG: Bạn BẮT BUỘC phải chia câu trả lời thành 2 phần, ngăn cách nhau bởi cụm từ chính xác là "---GOI_Y---". 
                    - Phần 1 (Trên ---GOI_Y---): Toàn bộ nội dung chương truyện.
                    - Phần 2 (Dưới ---GOI_Y---): Trình bày 5-10 dòng gợi ý các hướng phát triển kịch tính cho chương tiếp theo.
                    """
                    
                    with st.spinner("⏳ AI đang chắp bút viết chương..."):
                        response = model.generate_content(system_prompt)
                    
                    raw_text = response.text
                    
                    if "---GOI_Y---" in raw_text:
                        parts = raw_text.split("---GOI_Y---")
                        chapter_text = parts[0].strip()
                        suggestion_text = parts[1].strip()
                    else:
                        chapter_text = raw_text
                        suggestion_text = "Tác giả cứ tự do sáng tạo diễn biến tiếp theo nhé!"
                    
                    display_title = f"### {chapter_title}" if chapter_title else "### Chương Mới"
                    new_chapter = f"\n\n{display_title}\n**Phần chốt:** {prompt}\n\n{chapter_text}\n\n---\n"
                    current_data["content"] += new_chapter
                    current_data["latest_suggestion"] = suggestion_text
                    
                    st.rerun() 
                    
                except Exception as e:
                    st.error(f"Hệ thống gặp sự cố: {e}")
