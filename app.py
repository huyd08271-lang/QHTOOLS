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
    [data-testid="stFormSubmitButton"] button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        height: 100px !important; 
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
            "content": "",
            "latest_suggestion": "" # Thêm biến lưu gợi ý mới nhất
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
                "latest_suggestion": ""
            }
            st.session_state.current_story = new_story_name
            st.rerun()
            
    st.divider()
    st.subheader("Hệ Thống Trí Tuệ")
    st.session_state.api_key = st.text_input("API Key (Gemini):", type="password", value=st.session_state.api_key)

# --- KHÔNG GIAN LÀM VIỆC CHÍNH ---
current_data = st.session_state.stories[st.session_state.current_story]
# Cập nhật cấu trúc cho các truyện cũ tránh bị lỗi
if "plot" not in current_data:
    current_data["plot"] = ""
if "latest_suggestion" not in current_data:
    current_data["latest_suggestion"] = ""

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

# BỐ CỤC: BÊN TRÁI (SÁNG TÁC) - BÊN PHẢI (LỊCH SỬ)
col_compose, col_history = st.columns([6, 4], gap="large")

# CỘT BÊN PHẢI: LỊCH SỬ SINH VĂN BẢN
with col_history:
    st.markdown("### 📜 Lịch Sử Bản Thảo")
    if current_data["content"]:
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
    
    # Hiển thị ô Gợi ý (Nếu có)
    if current_data["latest_suggestion"]:
        st.info(f"💡 **AI Gợi ý cho chương tiếp theo:**\n\n{current_data['latest_suggestion']}")
    
    with st.form("compose_form", clear_on_submit=True):
        
        col_input, col_submit = st.columns([4, 1])
        
        with col_input:
            chapter_title = st.text_input("Tên chương (VD: Chương 1: Bước ngoặt):", placeholder="Gõ tên chương vào đây...")
            prompt = st.text_area("Đoạn hội ý / Tóm tắt diễn biến:", height=150, placeholder="Nhân vật A đi vào rừng và gặp...")
            
        with col_submit:
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
                    
                    QUAN TRỌNG: Bạn BẮT BUỘC phải chia câu trả lời thành 2 phần, ngăn cách nhau bởi cụm từ chính xác là "---GOI_Y---". 
                    - Phần 1 (Trên ---GOI_Y---): Toàn bộ nội dung chương truyện.
                    - Phần 2 (Dưới ---GOI_Y---): Trình bày 5-10 dòng gợi ý các hướng phát triển kịch tính cho chương tiếp theo.
                    """
                    
                    with st.spinner("⏳ AI đang xử lý kịch bản..."):
                        response = model.generate_content(system_prompt)
                    
                    raw_text = response.text
                    
                    # Bộ lọc bóc tách phần Truyện và phần Gợi ý
                    if "---GOI_Y---" in raw_text:
                        parts = raw_text.split("---GOI_Y---")
                        chapter_text = parts[0].strip()
                        suggestion_text = parts[1].strip()
                    else:
                        chapter_text = raw_text
                        suggestion_text = "Tác giả cứ tự do sáng tạo diễn biến tiếp theo nhé!"
                    
                    # Lưu Truyện vào Lịch sử
                    display_title = f"### {chapter_title}" if chapter_title else "### Chương Mới"
                    new_chapter = f"\n\n{display_title}\n**Hội ý:** {prompt}\n\n{chapter_text}\n\n---\n"
                    st.session_state.stories[st.session_state.current_story]["content"] += new_chapter
                    
                    # Lưu Gợi ý để hiển thị ra ô màu xanh
                    st.session_state.stories[st.session_state.current_story]["latest_suggestion"] = suggestion_text
                    
                    st.rerun() 
                    
                except Exception as e:
                    st.error(f"Hệ thống gặp sự cố: {e}")
