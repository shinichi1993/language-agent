import streamlit as st
from google import genai

# ==========================================
# PHẦN 1: CẤU HÌNH GIAO DIỆN & CSS TÙY CHỈNH
# ==========================================
st.set_page_config(
    page_title="AI Language Tutor",
    page_icon="🎓",
    layout="centered"
)

# Nhúng một chút CSS để giao diện bớt "phèn", làm đẹp các bong bóng chat và thanh sidebar
st.markdown("""
    <style>
    /* Tùy chỉnh phong cách chung */
    .main {
        background-color: #f8f9fa;
    }
    /* Tiêu đề chính */
    h1 {
        color: #1f2937;
        font-family: 'Helvetica Neue', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 AI Language Tutor Pro")
st.markdown("Trợ lý thông minh giúp bạn luyện tập và sửa lỗi **Tiếng Anh - Tiếng Trung - Tiếng Nhật**.")


# ==========================================
# PHẦN 2: KHỞI TẠO API CLIENT VỚI KEY CỨNG
# ==========================================
# Lấy API Key từ cấu hình bảo mật của Streamlit
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("Chưa cấu hình GOOGLE_API_KEY trong Streamlit Secrets!")
    st.stop()

# ==========================================
# PHẦN 3: THANH CÔNG CỤ (SIDEBAR) ĐỂ TÙY CHỌN
# ==========================================
st.sidebar.header("⚙️ Tùy chỉnh học tập")

# Cho phép người dùng chọn ngôn ngữ mục tiêu
target_lang = st.sidebar.selectbox(
    "Chọn ngôn ngữ bạn muốn luyện tập:",
    ["Đa ngôn ngữ (Tự động nhận diện)", "Tiếng Anh (English)", "Tiếng Trung (中文)", "Tiếng Nhật (日本語)"]
)

# Chọn cấp độ học
level = st.sidebar.selectbox(
    "Chọn cấp độ của bạn:",
    ["Sơ cấp (Beginner)", "Trung cấp (Intermediate)", "Nâng cao (Advanced)"]
)

st.sidebar.markdown("---")
# Nút xóa lịch sử trò chuyện để làm lại từ đầu
if st.sidebar.button("🗑️ Xóa lịch sử chat"):
    st.session_state.messages = []
    st.rerun()


# ==========================================
# PHẦN 4: ĐỊNH NGHĨA "NHÂN DẠNG" CHO AGENT (PROMPT)
# ==========================================
# Dynamic Prompt dựa theo lựa chọn ở Sidebar của người dùng
SYSTEM_PROMPT = f"""
Bạn là một Gia sư Ngoại ngữ AI thông minh, chuyên nghiệp và thân thiện.
- Ngôn ngữ học tập hiện tại người dùng chọn: {target_lang}
- Cấp độ người học: {level}

Nhiệm vụ và nguyên tắc phản hồi:
1. Kiểm tra và sửa lỗi ngữ pháp/từ vựng (nếu câu người dùng viết bị sai) và giải thích ngắn gọn, dễ hiểu.
2. Hỗ trợ đặc thù theo ngôn ngữ:
   - Nếu là Tiếng Trung: Luôn đính kèm Pinyin và giải thích từ vựng quan trọng.
   - Nếu là Tiếng Nhật: Luôn bổ sung cách đọc Furigana/Romaji cho Kanji và nêu rõ cấp độ lịch sự (Keigo hoặc Thân mật).
   - Nếu là Tiếng Anh: Giải thích các Phrasal Verbs, Idioms hoặc cấu trúc câu hay.
3. Luôn giữ văn phong khích lệ, phù hợp với cấp độ {level}.
"""


# ==========================================
# PHẦN 5: QUẢN LÝ LỊCH SỬ CHAT VÀ GIAO DIỆN HIỂN THỊ
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Vòng lặp hiển thị lại toàn bộ lịch sử tin nhắn trong phiên làm việc
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ==========================================
# PHẦN 6: XỬ LÝ NHẬP LIỆU & GỌI GOOGLE GEMINI API
# ==========================================
if prompt := st.chat_input("Nhập câu cần học, dịch hoặc kiểm tra lỗi ở đây...", key="main_chat_input"):
    # Lưu tin nhắn của người dùng vào session
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Hiệu ứng chờ AI phản hồi
    with st.chat_message("assistant"):
        with st.spinner("Agent đang phân tích câu..."):
            # Tổng hợp System Prompt và lịch sử chat để gửi cho AI
            full_prompt = f"{SYSTEM_PROMPT}\n\nLịch sử trò chuyện:\n"
            for m in st.session_state.messages:
                full_prompt += f"{m['role']}: {m['content']}\n"

            response_text = None
            try:
                # Gọi model Gemini Flash mới nhất
                response = client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=full_prompt
                )
                response_text = response.text
            except Exception as e:
                response_text = f"⚠️ Đã xảy ra lỗi khi kết nối tới AI: `{str(e)}`"

            # Hiển thị câu trả lời và lưu vào lịch sử
            st.write(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})