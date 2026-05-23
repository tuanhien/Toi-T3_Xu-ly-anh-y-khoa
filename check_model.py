import google.generativeai as genai

# Dán API key của anh vào trong ngoặc kép
genai.configure(api_key="AIzaSyBsZKO5DlUKXtaPBz_mHD1hlrnMW0lEee8")

print("Danh sách các model hỗ trợ tạo văn bản:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)