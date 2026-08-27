
import streamlit as st
import google.generativeai as genai

# Cấu hình trang
st.set_page_config(page_title="Studio Viết Truyện AI", page_icon="✍️", layout="wide")

st.title("✨ Studio Viết Truyện AI")
st.markdown("Công cụ sáng tác cốt truyện đa nền tảng - Tối ưu cho cả điện thoại và máy tính.")

# Bảng bên trái (Sidebar) - Quản lý thiết lập
with st.sidebar:
    st.header("⚙️ Cấu Hình Thế Giới")
    api_key = st.text_input("API Key (Google Gemini):", type="password", help="Nhập API Key miễn phí từ Google AI Studio")
    
    st.divider()
    
    genre = st.selectbox(
        "Thể loại:", 
        ["Tận thế", "Xuyên không", "Kiếm hiệp", "Tu tiên", "Hậu tận thế", "Siêu năng lực"], 
        index=3
    )
    setting = st.text_input("Bối cảnh hiện tại:", "Mật thất / Khu rừng đổ nát")
    
    st.divider()
    
    st.subheader("📝 Sổ tay bối cảnh (Wiki)")
    chars = st.text_area(
        "Hồ sơ Nhân vật:", 
        "Ngày sinh nhân vật chính: 5/11/2005.\nTính cách: Lạnh lùng, quyết đoán, tư duy logic cao.\nSố lượng nhân vật tối đa: 2-3 người.", 
        height=100
    )
    rules = st.text_area(
        "Quy tắc ngầm (Bắt buộc):", 
        "TUYỆT ĐỐI KHÔNG dùng từ Hán-Việt sáo rỗng (VD: linh khí).\nBẮT BUỘC dùng hệ thống thuật ngữ thuần Việt: 'Khí Thiêng', 'Sương Thần'.", 
        height=100
    )

# Không gian làm việc chính
st.subheader("Khung Ý Tưởng (Prompt Box)")
prompt = st.text_area(
    "Nhập tóm tắt diễn biến chương truyện muốn viết:", 
    placeholder="Ví dụ: Nhân vật chính đi vào mật thất, phát hiện một di tích cổ. Tại đây anh ta hấp thụ Sương Thần để đột phá...",
    height=150
)

# Nút kích hoạt AI
if st.button("🚀 Sinh Chương Truyện", use_container_width=True):
    if not api_key:
        st.warning("⚠️ Vui lòng nhập API Key ở thanh menu bên trái trước khi bắt đầu.")
    elif not prompt:
        st.warning("⚠️ Ông chưa nhập diễn biến kìa!")
    else:
        try:
            # Kết nối AI
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            system_prompt = f"""Bạn là một nhà văn chuyên nghiệp viết truyện {genre}.
            Hãy viết một chương truyện dựa trên các thông số sau:
            - Bối cảnh: {setting}
            - Thiết lập nhân vật: {chars}
            - Cốt truyện chương này: {prompt}
            - QUY TẮC VỀ THUẬT NGỮ BẮT BUỘC PHẢI TUÂN THỦ: {rules}
            
            Hãy viết thật sống động, miêu tả chi tiết không gian, nội tâm và hành động. Đảm bảo mạch văn logic, lôi cuốn."""
            
            with st.spinner("Đang chắp bút... Ông đợi một lát nhé!"):
                response = model.generate_content(system_prompt)
                
            st.success("Hoàn thành!")
            st.divider()
            
            # Hiển thị kết quả
            st.markdown("### 📜 Nội dung chương")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"Đã xảy ra lỗi: {e}")
