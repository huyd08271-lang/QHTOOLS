import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Studio Viết Truyện AI", page_icon="✍️", layout="wide")

# --- HỆ THỐNG LƯU TRỮ TẠM THỜI ---
if 'stories' not in st.session_state:
    st.session_state.stories = {
        "Dự án Truyện 1": {
            "notes": "Hồ sơ Nhân vật: Ngày sinh 5/11/2005. Tính cách quyết đoán.\n\nQUY TẮC THẾ GIỚI (Bắt buộc tuân thủ):\n- TUYỆT ĐỐI KHÔNG dùng từ Hán-Việt sáo rỗng (như linh khí, tu chân).\n- BẮT BUỘC dùng hệ thống thuật ngữ thuần Việt: 'Khí Thiêng', 'Sương Thần'.\n\n(Hãy ghi thêm các luật lệ sức mạnh, vật phẩm, bối cảnh vào đây...)",
            "content": ""
        }
    }
if 'current_story' not in st.session_state:
    st.session_state.current_story = "Dự án Truyện 1"

# --- THANH MENU BÊN TRÁI (QUẢN LÝ TRUYỆN) ---
with st.sidebar:
    st.header("📚 Quản Lý Truyện")
    
    # Dropdown Chọn truyện đang viết
    story_names = list(st.session_state.stories.keys())
    selected_story = st.selectbox("Đang mở bộ truyện:", story_names, index=story_names.index(st.session_state.current_story))
    st.session_state.current_story = selected_story
    
    st.divider()
    
    # Khu vực tạo truyện mới
    new_story_name = st.text_input("Tên bộ truyện mới:")
    if st.button("➕ Tạo truyện mới", use_container_width=True):
        if new_story_name and new_story_name not in st.session_state.stories:
            st.session_state.stories[new_story_name] = {
                "notes": "Hồ sơ Nhân vật: Ngày sinh 5/11/2005. Tính cách quyết đoán.\n\nQUY TẮC THẾ GIỚI (Bắt buộc tuân thủ):\n- TUYỆT ĐỐI KHÔNG dùng từ Hán-Việt sáo rỗng.\n- BẮT BUỘC dùng hệ thống thuật ngữ thuần Việt: 'Khí Thiêng', 'Sương Thần'.",
                "content": ""
            }
            st.session_state.current_story = new_story_name
            st.rerun()
            
    st.divider()
    st.header("⚙️ Kết Nối AI")
    api_key = st.text_input("API Key (Google Gemini):", type="password")

# --- KHÔNG GIAN LÀM VIỆC CHÍNH ---
current_data = st.session_state.stories[st.session_state.current_story]

st.title(f"📖 {st.session_state.current_story}")

# 1. Khung Ghi Chú Lớn
st.subheader("📝 Ghi chú & Thiết lập Thế giới")
st.caption("Hãy bấm 'Lưu Ghi Chú' ngay sau khi ông viết thêm thiết lập để không bị mất dữ liệu nhé!")

# Khung nhập liệu
updated_notes = st.text_area(
    "Nội dung ghi chú:", 
    value=current_data["notes"], 
    height=250, 
    max_chars=20000 
)

# NÚT LƯU GHI CHÚ MỚI THÊM VÀO
if st.button("💾 Lưu Ghi Chú"):
    st.session_state.stories[st.session_state.current_story]["notes"] = updated_notes
    st.success("Đã lưu ghi chú thành công! Ông có thể thoải mái chuyển truyện khác.")

st.divider()

# 2. Lịch sử Truyện (Lưu nối tiếp các chương)
st.subheader("📜 Nội dung bản thảo")
if current_data["content"]:
    st.markdown(current_data["content"])
    
    # Nút tải file về máy để không bị mất dữ liệu
    st.download_button(
        label="📥 Tải bộ truyện này xuống máy (File TXT)",
        data=current_data["content"],
        file_name=f"{st.session_state.current_story}.txt",
        mime="text/plain",
    )
else:
    st.info("Chưa có chương nào được viết. Hãy nhập ý tưởng bên dưới để bắt đầu!")

st.divider()

# 3. Khu vực Sinh Chương Mới
st.subheader("✨ Sáng tác chương tiếp theo")
prompt = st.text_area("Nhập diễn biến ông muốn AI viết tiếp:", height=150)

if st.button("🚀 Viết Tiếp", use_container_width=True):
    if not api_key:
        st.warning("⚠️ Vui lòng nhập API Key ở menu bên trái!")
    elif not prompt:
        st.warning("⚠️ Vui lòng nhập diễn biến muốn viết!")
    else:
        try:
            genai.configure(api_key=api_key)
            # Đã sửa thành model mới nhất để tránh lỗi 404
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Gộp cả Ghi chú tổng và Nội dung cũ để AI hiểu văn cảnh
            system_prompt = f"""Bạn là một tiểu thuyết gia chuyên nghiệp.
            
            BỐI CẢNH VÀ QUY TẮC CỐT LÕI (Bắt buộc tuân thủ):
            {st.session_state.stories[st.session_state.current_story]["notes"]}
            
            TÓM TẮT CÁC CHƯƠNG TRƯỚC (Để giữ mạch truyện liền mạch):
            {current_data["content"][-4000:]} 
            
            YÊU CẦU MỚI: Dựa vào bối cảnh và mạch truyện trên, hãy viết tiếp một chương truyện chi tiết cho diễn biến sau:
            {prompt}
            """
            
            with st.spinner("Đang chắp bút... Ông đợi một lát nhé!"):
                response = model.generate_content(system_prompt)
            
            # Lưu nối tiếp nội dung mới vào bản thảo
            new_chapter = f"\n\n### Ý tưởng: {prompt}\n\n{response.text}\n\n---\n"
            st.session_state.stories[st.session_state.current_story]["content"] += new_chapter
            st.rerun() 
            
        except Exception as e:
            st.error(f"Đã xảy ra lỗi: {e}")
