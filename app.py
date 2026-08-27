import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG TỔNG THỂ ---
st.set_page_config(page_title="AI Story Studio Pro", page_icon="✒️", layout="wide")

# --- CSS TÙY CHỈNH LÀM ĐẸP GIAO DIỆN ---
st.markdown("""
<style>
    /* Căn chỉnh không gian tổng thể */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    /* Làm đẹp ô Text Area */
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        transition: border-color 0.3s;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        background-color: #ffffff !important;
    }
    /* Làm đẹp Nút bấm */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        border: 1px solid #e2e8f0 !important;
    }
    .stButton > button:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px);
    }
    /* Tiêu đề */
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
    st.image("https://cdn-icons-png.flaticon.com/512/3131/3131610.png", width=60) # Thêm logo nhỏ cho ngầu
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

# BỐ CỤC 2 CỘT: CẤM KỴ & CỐT TRUYỆN
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚫 Giới Hạn Cấm Kỵ")
    updated_notes = st.text_area(
        "Nhập các quy tắc AI không được vi phạm (từ cấm, motif không dùng):", 
        value=current_data["notes"], 
        height=220, 
        max_chars=15000
    )

with col2:
    st.markdown("### 🗺️ Cốt Truyện Tổng Thể")
    # Đã nâng giới hạn lên 15.000 ký tự (khoảng 2000 - 2500 chữ)
    updated_plot = st.text_area(
        "Nhập sườn cốt truyện chính (Hỗ trợ tối đa 2000 chữ):", 
        value=current_data["plot"], 
        height=220, 
        max_chars=15000 
    )

# Nút lưu đặt ở giữa cho cân đối
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("💾 Đồng Bộ Cài Đặt (Lưu Ghi Chú & Cốt Truyện)", use_container_width=True):
        st.session_state.stories[st.session_state.current_story]["notes"] = updated_notes
        st.session_state.stories[st.session_state.current_story]["plot"] = updated_plot
        st.success("Đã lưu thiết lập an toàn!")

st.markdown("---")

# KHU VỰC HIỂN THỊ TRUYỆN
st.markdown("### 📜 Lịch Sử Sinh Văn Bản")
if current_data["content"]:
    # Dùng khối expander để nếu truyện quá dài có thể thu gọn lại cho gọn web
    with st.expander("Nhấp để xem/thu gọn toàn bộ bản thảo", expanded=True):
        st.markdown(current_data["content"])
        
    st.download_button(
        label="📥 Xuất File Bản Thảo (.txt)",
        data=current_data["content"],
        file_name=f"{st.session_state.current_story}_Draft.txt",
        mime="text/plain",
        use_container_width=True
    )
else:
    st.info("Trang giấy còn trắng. Hãy ra lệnh cho AI ở bên dưới.")

st.markdown("---")

# KHU VỰC ĐIỀU KHIỂN AI
st.markdown("### ✨ Sáng Tác Chương Mới")
prompt = st.text_area("Tóm tắt diễn biến tiếp theo (Cảnh quay, hội thoại, hành động):", height=120)

if st.button("🚀 Kích Hoạt AI Viết Tiếp", use_container_width=True):
    if not st.session_state.api_key:
        st.error("⚠️ Khóa API bị thiếu! Vui lòng điền ở thanh bên trái.")
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
            
            YÊU CẦU MỚI CHO CHƯƠNG NÀY: Dựa vào bối cảnh và mạch truyện trên, hãy viết tiếp một chương truyện chi tiết cho diễn biến sau:
            {prompt}
            """
            
            with st.spinner("⏳ AI đang xử lý kịch bản..."):
                response = model.generate_content(system_prompt)
            
            new_chapter = f"\n\n### 🎬 Diễn biến: {prompt}\n\n{response.text}\n\n---\n"
            st.session_state.stories[st.session_state.current_story]["content"] += new_chapter
            st.rerun() 
            
        except Exception as e:
            st.error(f"Hệ thống gặp sự cố: {e}")
