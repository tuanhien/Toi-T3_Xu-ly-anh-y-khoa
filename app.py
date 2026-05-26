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

    # Bố cục giao diện nhập liệu dạng Form
    with st.form("clinical_case_form"):
        st.subheader("📋 Nhập thông tin Ca Lâm Sàng")

        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.number_input("Tuổi bệnh nhân:", min_value=18, max_value=100, value=58)
            gender = st.selectbox("Giới tính:", ["Nam", "Nữ"])
            smoking = st.selectbox("Tiền sử hút thuốc lá:", ["Không", "Có hút thuốc"])

        with col2:
            sbp = st.number_input("Huyết áp tâm thu (mmHg):", min_value=90, max_value=220, value=150)
            # Điều chỉnh dải giá trị chuẩn cho đơn vị mg/dL
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

    # Xử lý logic khi bấm submit
    if submit_button:
        with st.spinner("Đang chạy mô hình suy luận trên Groq Cloud..."):
            try:
                system_prompt = """
                Bạn là chuyên gia Tim mạch. Đưa ra khuyến nghị dựa trên quy tắc của ESC/EAS 2025 Focused Update.
                
                Quy tắc trình bày BẮT BUỘC TUÂN THỦ:
                1. KHÔNG ĐƯỢC lặp lại các thông tin bệnh nhân đã nhập.
                2. BẮT BUỘC bắt đầu bằng dòng Phân tầng nguy cơ theo đúng định dạng ví dụ.
                3. ĐƠN VỊ ĐO: Chỉ sử dụng duy nhất đơn vị mg/dL cho TẤT CẢ các chỉ số lipid máu. Tuyệt đối KHÔNG quy đổi hay nhắc đến đơn vị mmol/L.
                
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
                - **Lý do:** Đái tháo đường type 2.
                - **Mục tiêu LDL-C:** < 70 mg/dL.
                - **Đánh giá hiện tại:** LDL-C 130 mg/dL (chưa đạt mục tiêu).
                - **Khuyến nghị Giai đoạn 1:** Bắt đầu Statin cường độ cao (VD: Rosuvastatin 20mg).
                
                [Ví dụ 3: Nguy cơ Trung Bình]
                Output:
                ### 🟡 PHÂN TẦNG NGUY CƠ: TRUNG BÌNH
                - **Lý do:** Theo thang điểm SCORE2.
                - **Mục tiêu LDL-C:** < 100 mg/dL.
                
                --- KẾT THÚC VÍ DỤ ---
                
                Bây giờ, hãy phân tích ca bệnh mới được cung cấp. Cấu trúc rõ ràng bằng Markdown. Không bịa ra thuốc ngoài Guideline. Chỉ sử dụng đơn vị mg/dL.
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
                
                Lưu ý: Tất cả giá trị mục tiêu LDL-C trong khuyến nghị phải được trình bày theo đơn vị mg/dL.
                """
                print("System Prompt:", age, smoking, sbp, cholesterol, ldlc, diabetes, ckd, ascvd, fh, additional_notes)
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