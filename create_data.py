import json
import random

def generate_synthetic_data(num_cases=500):
    dataset = []
    
    for _ in range(num_cases):
        age = random.randint(35, 80)
        gender = random.choice(["Nam", "Nữ"])
        smoking = random.choice(["Không", "Có hút thuốc"])
        sbp = random.randint(110, 180)
        ldlc = round(random.uniform(1.8, 5.5), 1)
        
        # Tạo xác suất cho các bệnh lý nền
        ascvd = "Có" if random.random() < 0.2 else "Không"
        diabetes = "Có" if random.random() < 0.25 and ascvd == "Không" else "Không"
        ckd = random.choice(["Không", "Giai đoạn 3", "Giai đoạn 4-5 hoặc suy thận"]) if random.random() < 0.15 else "Không"
        
        # Tính toán nhãn (Ground Truth) bằng rule-based ESC 2025
        risk_level = "THẤP"
        target_ldlc = "< 3.0 mmol/L"
        recommendation = "Tư vấn thay đổi lối sống."
        
        if ascvd == "Có" or ckd == "Giai đoạn 4-5 hoặc suy thận":
            risk_level = "RẤT CAO"
            target_ldlc = "< 1.4 mmol/L và giảm >50% so với nền"
            recommendation = "Bắt đầu ngay Statin cường độ cao (VD: Rosuvastatin 20-40mg). Đánh giá lại sau 4-6 tuần, nếu chưa đạt cân nhắc Ezetimibe 10mg."
        elif diabetes == "Có" or ckd == "Giai đoạn 3":
            risk_level = "CAO"
            target_ldlc = "< 1.8 mmol/L"
            recommendation = "Bắt đầu Statin cường độ cao. Mục tiêu kép giảm LDL-C."
        elif sbp > 160 or smoking == "Có hút thuốc":
            risk_level = "TRUNG BÌNH"
            target_ldlc = "< 2.6 mmol/L"
            recommendation = "Thay đổi lối sống. Cân nhắc Statin cường độ trung bình (VD: Rosuvastatin 5-10mg)."

        # Ghép thành prompt đầu vào
        input_text = f"THÔNG TIN CA LÂM SÀNG:\n- Tuổi: {age} | Giới tính: {gender}\n- Hút thuốc lá: {smoking}\n- Huyết áp tâm thu: {sbp} mmHg\n- LDL-Cholesterol hiện tại: {ldlc} mmol/L\n- Đái tháo đường: {diabetes}\n- Bệnh thận mạn (CKD): {ckd}\n- Tiền sử ASCVD: {ascvd}"
        
        # Ghép thành kết quả mong muốn (Output)
        output_text = f"### 🚨 PHÂN TẦNG NGUY CƠ: {risk_level}\n- **Mục tiêu LDL-C:** {target_ldlc}\n- **Đánh giá hiện tại:** LDL-C {ldlc} mmol/L.\n- **Khuyến nghị:** {recommendation}"
        
        # Format chuẩn Alpaca
        case = {
            "instruction": "Bạn là chuyên gia Tim mạch. Đưa ra khuyến nghị điều trị lipid máu dựa trên ESC/EAS 2025 Focused Update. Bắt đầu bằng dòng Phân tầng nguy cơ.",
            "input": input_text,
            "output": output_text
        }
        dataset.append(case)
        
    with open("esc2025_dataset.jsonl", "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"Đã tạo thành công {num_cases} ca lâm sàng vào file esc2025_dataset.jsonl")

# Chạy hàm sinh dữ liệu
generate_synthetic_data(500)