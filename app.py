import streamlit as st
import json
import os
from pathlib import Path
from groq import Groq

CONFIG_FILE = Path(__file__).with_name("config.json")


def load_groq_api_key() -> str:
    env_api_key = os.getenv("GROQ_API_KEY", "").strip()
    if env_api_key:
        return env_api_key

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return ""

    return str(config.get("GROQ_API_KEY", "")).strip()

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="ESC/EAS 2025 Lipid Management AI Assistant",
    page_icon="🩺",
    layout="wide"
)

st.session_state["api_key"] = load_groq_api_key()  # Ưu tiên biến môi trường, sau đó fallback sang config.json

# Khởi tạo session state cho API Key nếu chưa có
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# Giao diện Sidebar để cấu hình API Key
st.sidebar.header("🔑 Cấu hình Hệ thống")
api_key_input = st.sidebar.text_input("Nhập Groq API Key:", type="password", value=st.session_state["api_key"])

if api_key_input:
    st.session_state["api_key"] = api_key_input

st.sidebar.markdown("""
---
### 📚 Thông tin Hướng dẫn (Guideline)
Ứng dụng sử dụng **Groq API** (Tốc độ siêu tốc) để tích hợp các cập nhật mới nhất từ **ESC/EAS 2025 Focused Update**:
- Phân tầng nguy cơ theo SCORE2 / SCORE2-OP.
- Mục tiêu LDL-C nghiêm ngặt.
- Khuyến nghị cá thể hóa phối hợp thuốc.
""")

# Tiêu đề chính ứng dụng
st.title("🩺 Hệ thống Hỗ trợ Quyết định Lâm sàng Lipid máu (Dùng Groq AI)")
st.markdown("Trợ lý AI hỗ trợ phân tầng nguy cơ tim mạch và khuyến nghị phác đồ hạ lipid máu dựa trên cập nhật đồng thuận mới nhất.")

if not st.session_state["api_key"]:
    st.info("💡 Vui lòng nhập Groq API Key ở thanh bên hoặc điền vào file config.json để bắt đầu sử dụng ứng dụng.")
else:
    # Khởi tạo Groq Client
    client = Groq(api_key=st.session_state["api_key"])

    # Bố cục giao diện nhập liệu dạng Form
    with st.form("clinical_case_form"):
        st.subheader("📋 Nhập thông tin Ca Lâm Sàng")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input("Tuổi bệnh nhân:", min_value=18, max_value=100, value=55)
            gender = st.selectbox("Giới tính:", ["Nam", "Nữ"])
            smoking = st.selectbox("Tiền sử hút thuốc lá:", ["Không", "Có hút thuốc"])
            
        with col2:
            sbp = st.number_input("Huyết áp tâm thu (mmHg):", min_value=90, max_value=220, value=130)
            cholesterol = st.number_input("Cholesterol toàn phần (mmol/L):", min_value=2.0, max_value=15.0, value=5.2, step=0.1)
            ldlc = st.number_input("LDL-Cholesterol hiện tại (mmol/L):", min_value=0.5, max_value=10.0, value=3.6, step=0.1)
            
        with col3:
            diabetes = st.selectbox("Đái tháo đường (Type 1/2):", ["Không", "Có"])
            ckd = st.selectbox("Bệnh thận mạn tính (CKD):", ["Không", "Giai đoạn 3", "Giai đoạn 4-5 hoặc suy thận"])
            ascvd = st.selectbox("Tiền sử bệnh tim mạch do xơ vữa (ASCVD/Hội chứng vành cấp):", ["Không", "Có"])
            fh = st.selectbox("Tăng cholesterol máu gia đình (FH):", ["Không", "Có nghi ngờ hoặc xác định"])

        st.markdown("---")
        additional_notes = st.text_area("Ghi chú bổ sung:", placeholder="Ví dụ: Bệnh nhân từng bị đau cơ khi dùng Statin...")

        submit_button = st.form_submit_button("🔮 Phân tích với AI (Tốc độ cao)")

    # Xử lý logic khi bấm submit
    if submit_button:
        with st.spinner("Đang chạy mô hình suy luận trên Groq Cloud..."):
            try:
                system_prompt = """
                Bạn là chuyên gia Tim mạch. Đưa ra khuyến nghị dựa trên ESC/EAS 2025 Focused Update.
                Hãy suy luận từng bước (Chain of Thought) và tuân thủ tuyệt đối định dạng của các ví dụ mẫu dưới đây.
                
                --- VÍ DỤ CHUẨN (FEW-SHOT EXAMPLES) ---
                
                [Ví dụ 1: Nguy cơ Rất Cao]
                Input: Nam, 60 tuổi, hút thuốc, HA 150, LDL-C 3.0 mmol/L, có tiền sử Nhồi máu cơ tim (ASCVD).
                Output:
                - Phân tầng nguy cơ: Rất Cao (Do có tiền sử ASCVD).
                - Mục tiêu LDL-C: < 1.4 mmol/L và giảm >50% so với nền.
                - Đánh giá hiện tại: LDL-C 3.0 chưa đạt mục tiêu.
                - Khuyến nghị Giai đoạn 1: Bắt đầu ngay Statin cường độ cao (VD: Rosuvastatin 20mg hoặc Atorvastatin 40-80mg).
                - Khuyến nghị Giai đoạn 2: Nếu sau 4-6 tuần thử máu lại LDL-C vẫn > 1.4, bổ sung Ezetimibe 10mg.
                
                [Ví dụ 2: Nguy cơ Trung Bình]
                Input: Nữ, 45 tuổi, không hút thuốc, HA 120, LDL-C 2.8 mmol/L, không đái tháo đường, không ASCVD.
                Output:
                - Phân tầng nguy cơ: Trung Bình (Theo thang điểm SCORE2).
                - Mục tiêu LDL-C: < 2.6 mmol/L.
                - Đánh giá hiện tại: LDL-C 2.8 mmol/L, hơi cao so với mục tiêu.
                - Khuyến nghị Giai đoạn 1: Tư vấn thay đổi lối sống, ăn uống tập luyện. Cân nhắc Statin cường độ trung bình (VD: Rosuvastatin 5mg) nếu không cải thiện sau 3 tháng.
                
                --- KẾT THÚC VÍ DỤ ---
                
                Bây giờ, hãy phân tích ca bệnh mới được cung cấp. Cấu trúc rõ ràng bằng Markdown. Không bịa ra thuốc ngoài Guideline. Phản hồi bằng tiếng Việt.
                """

                patient_profile = f"""
                THÔNG TIN CA LÂM SÀNG:
                - Tuổi: {age} | Giới tính: {gender}
                - Hút thuốc lá: {smoking}
                - Huyết áp tâm thu: {sbp} mmHg
                - Cholesterol toàn phần: {cholesterol} mmol/L
                - LDL-Cholesterol hiện tại: {ldlc} mmol/L
                - Đái tháo đường: {diabetes}
                - Bệnh thận mạn (CKD): {ckd}
                - Tiền sử ASCVD/Hội chứng vành cấp: {ascvd}
                - Tăng cholesterol máu gia đình (FH): {fh}
                - Ghi chú lâm sàng bổ sung: {additional_notes if additional_notes else "Không có"}
                """

                # Gọi API của Groq, sử dụng model Llama 3 siêu nhanh
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": patient_profile,
                        }
                    ],
                    model="llama-3.1-8b-instant", # Model Llama 3 8B cực kỳ nhanh và phù hợp
                    temperature=0.2, # Giảm nhiệt độ xuống thấp để AI trả lời chuẩn xác y khoa, ít sáng tạo
                )
                
                # Hiển thị kết quả
                st.success("✅ Phân tích hoàn tất chỉ trong tích tắc!")
                st.markdown("### 📑 Kết quả Khuyến nghị (Groq - Llama 3)")
                st.markdown(chat_completion.choices[0].message.content)
                
                st.warning("⚠️ **Lưu ý:** Ứng dụng là mô hình demo hỗ trợ quyết định lâm sàng.")
                
            except Exception as e:
                st.error(f"Đã xảy ra lỗi kết nối với Groq: {str(e)}")
                st.info("Vui lòng kiểm tra lại tính chính xác của API Key hoặc kết nối mạng.")