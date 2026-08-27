import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG TỔNG THỂ ---
st.set_page_config(page_title="AI Story Studio Pro", page_icon="✒️", layout="wide")

# --- CSS TÙY CHỈNH LÀM ĐẸP GIAO DIỆN ---
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
        transition: border-color 0.3s;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3b82f6 !important;
        background-color: #ffffff !important;
    }
    /* Căn chỉnh nút bấm trong form */
    [data-testid="stFormSubmitButton"] button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        height: 100px !important; /* Làm nút cao lên cho dễ bấm */
        background-color: #eff6ff !important;
        border: 1px solid #bfdbfe !important;
        color: #1d4ed8 !important;
        transition: all 0.2s ease-in-out !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #dbeafe !important;
        transform: translateY(-2px);
    }
    h1, h2, h3 {
        color: #1e293b;
        font-family: 'Segoe UI', Roboto, sans-serif;
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
            "content": ""
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
                "content": ""
            }
            st.session_state.current_story = new_story_name
            st.rerun()
            
    st.divider()
    st.subheader("Hệ Thống Trí Tuệ")
    st.session_state.api_key = st.text_input("API Key (Gemini):", type="password", value=st.session_state.api_key)

# --- KHÔNG GIAN LÀM VIỆC CHÍNH ---
current_data = st.session_state.stories[st.session_state.current_story]
if "plot" not in current_data:
    current_data["plot"] = ""

st.title(f"📖 {st.session_state.current_story}")
st.markdown("---")

# BỐ CỤC 2 CỘT CHO CÀI ĐẶT
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚫 Giới Hạn Cấm Kỵ")
    updated_notes = st.text_area(
        "Nhập các quy tắc AI không được vi phạm:", 
        value=current_data["notes"], 
        height=150, 
        max_chars=15000
    )

with col2:
    st.markdown("### 🗺️ Cốt Truyện Tổng Thể")
    updated_plot = st.text_area(
        "Nhập sườn cốt truyện chính (Tối đa 2000 chữ):", 
        value=current_data["plot"], 
        height=150, 
        max_chars=15000 
    )

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("💾 Đồng Bộ Cài Đặt (Lưu Ghi Chú & Cốt Truyện)", use_container_width=True):
        st.session_state.stories[st.session_state.current_story]["notes"] = updated_notes
        st.session_state.stories[st.session_state.current_story]["plot"] = updated_plot
        st.success("Đã lưu thiết lập an toàn!")

st.markdown("---")

# BỐ CỤC MỚI: BÊN TRÁI (SÁNG TÁC) - BÊN PHẢI (LỊCH SỬ)
col_compose, col_history = st.columns([6, 4], gap="large")

# CỘT BÊN PHẢI: LỊCH SỬ SINH VĂN BẢN
with col_history:
    st.markdown("### 📜 Lịch Sử Bản Thảo")
    if current_data["content"]:
        # Dùng container có thanh cuộn (scrollbar) để giới hạn chiều cao, không làm web bị dài thượt
        with st.container(height=500):
            st.markdown(current_data["content"])
            
        st.download_button(
            label="📥 Xuất File Bản Thảo (.txt)",
            data=current_data["content"],
            file_name=f"{st.session_state.current_story}_Draft.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Trang giấy còn trắng. Bản thảo sẽ xuất hiện ở đây sau khi sinh.")

# CỘT BÊN TRÁI: KHU VỰC SÁNG TÁC
with col_compose:
    st.markdown("### ✨ Sáng Tác Chương Mới")
    
    # Biểu mẫu tự động làm trắng sau khi bấm nút (clear_on_submit=True)
    with st.form("compose_form", clear_on_submit=True):
        
        # Chia form làm 2 phần: Bên trái nhập liệu, bên phải nút bấm
        col_input, col_submit = st.columns([4, 1])
        
        with col_input:
            chapter_title = st.text_input("Tên chương (VD: Chương 1: Bước ngoặt):", placeholder="Gõ tên chương vào đây...")
            prompt = st.text_area("Đoạn hội ý / Tóm tắt diễn biến:", height=150, placeholder="Nhân vật A đi vào rừng và gặp...")
            
        with col_submit:
            # Đẩy nút bấm xuống cho cân đối với ô nhập liệu
            st.markdown("<br><br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 Kích Hoạt AI", use_container_width=True)
            
        if submitted:
            if not st.session_state.api_key:
                st.error("⚠️ Khóa API bị thiếu! Vui lòng điền ở menu bên trái.")
            elif not prompt:
                st.warning("⚠️ Vui lòng cung cấp diễn biến cho chương này.")
            else:
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    model = genai.GenerativeModel('gemini-3.6-flash')
                        
                    system_prompt = f"""Bạn là một tiểu thuyết gia chuyên nghiệp.
                    
                    CỐT TRUYỆN CHÍNH (Bám sát cốt truyện này để định hướng diễn biến):
                    {st.session_state.stories[st.session_state.current_story]["plot"]}

                    ĐIỀU KIỆN CẤM KỴ & QUY TẮC (Tuyệt đối tuân thủ, không được viết sai):
                    {st.session_state.stories[st.session_state.current_story]["notes"]}
                    
                    TÓM TẮT CÁC CHƯƠNG TRƯỚC (Để giữ mạch truyện liền mạch):
                    {current_data["content"][-4000:]} 
                    
                    YÊU CẦU MỚI CHO CHƯƠNG NÀY: Dựa vào bối cảnh và mạch truyện trên, hãy viết một chương truyện chi tiết.
                    Tên chương (nếu có): {chapter_title}
                    Diễn biến yêu cầu: {prompt}
                    """
                    
                    with st.spinner("⏳ AI đang xử lý kịch bản..."):
                        response = model.generate_content(system_prompt)
                    
                    # Trình bày đẹp mắt trước khi lưu vào lịch sử
                    display_title = f"### {chapter_title}" if chapter_title else "### Chương Mới"
                    new_chapter = f"\n\n{display_title}\n**Hội ý:** {prompt}\n\n{response.text}\n\n---\n"
                    
                    st.session_state.stories[st.session_state.current_story]["content"] += new_chapter
                    st.rerun() 
                    
                except Exception as e:
                    st.error(f"Hệ thống gặp sự cố: {e}")
