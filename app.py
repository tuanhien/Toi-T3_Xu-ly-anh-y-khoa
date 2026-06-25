import streamlit as st
import os
from groq import Groq

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="ESC/EAS 2025 Lipid Management AI Assistant",
    page_icon="🩺",
    layout="wide"
)

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
Ứng dụng sử dụng **Groq API** để tích hợp các cập nhật mới nhất từ **ESC/EAS 2025 Focused Update**:
- Phân tầng nguy cơ theo SCORE2 / SCORE2-OP.
- Mục tiêu LDL-C nghiêm ngặt.
- Khuyến nghị cá thể hóa phối hợp thuốc.
""")

# Tiêu đề chính ứng dụng
st.title("🩺 Hệ thống Hỗ trợ Quyết định Lâm sàng Lipid máu")
st.markdown("Trợ lý AI hỗ trợ phân tầng nguy cơ tim mạch và khuyến nghị phác đồ hạ lipid máu dựa trên cập nhật ESC/EAS 2025.")

if not st.session_state["api_key"]:
    st.info("💡 Vui lòng nhập Groq API Key ở thanh bên (Sidebar) để bắt đầu sử dụng ứng dụng.")
else:
    client = Groq(api_key=st.session_state["api_key"])

    with st.form("clinical_case_form"):
        st.subheader("📋 Nhập thông tin Ca Lâm Sàng")

        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.number_input("Tuổi bệnh nhân:", min_value=18, max_value=100, value=58)
            gender = st.selectbox("Giới tính:", ["Nam", "Nữ"])
            smoking = st.selectbox("Tiền sử hút thuốc lá:", ["Không", "Có hút thuốc"])

        with col2:
            sbp = st.number_input("Huyết áp tâm thu (mmHg):", min_value=90, max_value=220, value=150)
            cholesterol = st.number_input("Cholesterol toàn phần (mg/dL):", min_value=40, max_value=1000, value=200, step=1)
            ldlc = st.number_input("LDL-Cholesterol hiện tại (mg/dL):", min_value=10, max_value=800, value=130, step=1)

        with col3:
            diabetes = st.selectbox("Đái tháo đường (Type 1/2):", ["Không", "Có"])
            ckd = st.selectbox("Bệnh thận mạn tính (CKD):", ["Không", "Giai đoạn 3", "Giai đoạn 4-5 hoặc suy thận"])
            ascvd = st.selectbox("Tiền sử bệnh tim mạch do xơ vữa (ASCVD/Hội chứng vành cấp):", ["Không", "Có"])
            fh = st.selectbox("Tăng cholesterol máu gia đình (FH):", ["Không", "Có nghi ngờ hoặc xác định"])

        st.markdown("---")
        additional_notes = st.text_area("Ghi chú bổ sung:", placeholder="Ví dụ: Bệnh nhân từng bị đau cơ khi dùng Statin...")

        submit_button = st.form_submit_button("🔮 Phân tích với AI")

    if submit_button:
        with st.spinner("Đang chạy mô hình suy luận trên Groq Cloud..."):
            try:
                predicted_risk = ""
                reason = ""
                
                if ascvd == "Có" and fh == "Có nghi ngờ hoặc xác định":
                    predicted_risk = "RẤT CAO"
                    reason = "Bệnh nhân có Tăng cholesterol máu gia đình (FH) kèm theo bệnh tim mạch do xơ vữa (ASCVD)."
                elif ascvd == "Có" or ckd == "Giai đoạn 4-5 hoặc suy thận":
                    predicted_risk = "RẤT CAO"
                    reason = "Bệnh nhân có tiền sử ASCVD hoặc suy thận nặng (eGFR < 30)."
                elif fh == "Có nghi ngờ hoặc xác định" and ascvd == "Không":
                    predicted_risk = "CAO"
                    reason = "Bệnh nhân có Tăng cholesterol máu gia đình (FH) đơn thuần (chưa có biến cố ASCVD)."
                elif diabetes == "Có":
                    # (Có thể thêm logic check thời gian mắc tiểu đường ở đây nếu UI có trường này)
                    predicted_risk = "CAO"
                    reason = "Bệnh nhân mắc Đái tháo đường."
                elif sbp > 180 or cholesterol > 310:
                    predicted_risk = "CAO"
                    reason = "Bệnh nhân có một yếu tố nguy cơ đơn lẻ ở mức độ nặng (HA > 180 hoặc TC > 8 mmol/L)."
                else:
                    predicted_risk = "TRUNG BÌNH"
                    reason = "Bệnh nhân không có yếu tố nguy cơ cao tự động, đánh giá theo thang điểm SCORE2 (mặc định cho test)."
                system_prompt = f"""
                Bạn là chuyên gia Tim mạch. Đưa ra khuyến nghị dựa trên quy tắc của ESC/EAS 2025 Focused Update.
                
                Quy tắc trình bày BẮT BUỘC TUÂN THỦ:
                1. KHÔNG ĐƯỢC lặp lại các thông tin bệnh nhân đã nhập.
                2. BẮT BUỘC sử dụng Mức phân tầng nguy cơ và Lý do mà hệ thống đã tính toán cứng dưới đây. Tuyệt đối không tự suy luận lại mức nguy cơ.
                3. ĐƠN VỊ ĐO: Chỉ sử dụng duy nhất đơn vị mg/dL cho TẤT CẢ các chỉ số lipid máu. Tuyệt đối KHÔNG quy đổi hay nhắc đến đơn vị mmol/L.
                
                📌 KẾT QUẢ TỪ HỆ THỐNG (BẮT BUỘC ÁP DỤNG):
                - PHÂN TẦNG NGUY CƠ: {predicted_risk}
                - LÝ DO: {reason}
                
                --- VÍ DỤ CHUẨN (FEW-SHOT EXAMPLES) ---
                
                [Ví dụ 1: Nguy cơ Rất Cao]
                Output:
                ### 🚨 PHÂN TẦNG NGUY CƠ: RẤT CAO
                - **Lý do:** Bệnh nhân có tiền sử ASCVD.
                - **Mục tiêu LDL-C:** < 55 mg/dL và giảm >50% so với nền.
                - **Đánh giá hiện tại:** LDL-C 116 mg/dL (chưa đạt mục tiêu).
                - **Khuyến nghị Giai đoạn 1:** Bắt đầu ngay Statin cường độ cao (VD: Rosuvastatin 20mg hoặc Atorvastatin 40-80mg).
                - **Khuyến nghị Giai đoạn 2:** Nếu sau 4-6 tuần thử máu lại LDL-C vẫn > 55 mg/dL, bổ sung Ezetimibe 10mg.
                
                [Ví dụ 2: Nguy cơ Cao]
                Output:
                ### ⚠️ PHÂN TẦNG NGUY CƠ: CAO
                - **Lý do:** Theo thang điểm SCORE2 vùng nguy cơ cao, điểm của bệnh nhân là ~6.8%.
                - **Mục tiêu LDL-C:** < 70 mg/dL.
                - **Đánh giá hiện tại:** LDL-C 130 mg/dL (chưa đạt mục tiêu).
                - **Khuyến nghị Giai đoạn 1:** Bắt đầu Statin cường độ cao (VD: Rosuvastatin 20mg).
                
                --- KẾT THÚC VÍ DỤ ---
                
                Bây giờ, hãy tạo báo cáo khuyến nghị dựa trên chỉ định của hệ thống. Cấu trúc rõ ràng bằng Markdown.
                """

                patient_profile = f"""
                THÔNG TIN CA LÂM SÀNG (tất cả giá trị lipid máu theo đơn vị mg/dL):
                - Tuổi: {age} tuổi | Giới tính: {gender}
                - Hút thuốc lá: {smoking}
                - Huyết áp tâm thu: {sbp} mmHg
                - Cholesterol toàn phần: {cholesterol} mg/dL
                - LDL-Cholesterol hiện tại: {ldlc} mg/dL
                - Đái tháo đường: {diabetes}
                - Bệnh thận mạn (CKD): {ckd}
                - Tiền sử ASCVD/Hội chứng vành cấp: {ascvd}
                - Tăng cholesterol máu gia đình (FH): {fh}
                - Ghi chú lâm sàng bổ sung: {additional_notes if additional_notes else "Không có"}
                """
                
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
                    model="llama-3.1-8b-instant", 
                    temperature=0.1, 
                )

                st.success("✅ Phân tích hoàn tất!")
                st.markdown("### 📑 Kết quả Khuyến nghị")
                st.markdown(chat_completion.choices[0].message.content)

                st.warning("⚠️ **Lưu ý:** Ứng dụng là mô hình demo hỗ trợ quyết định lâm sàng.")

            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {str(e)}")