from flask import Flask, request, jsonify, render_template
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# API Key của OpenAI
load_dotenv()  # Load biến môi trường từ file .env
client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

# Đọc file Excel và lưu dữ liệu trong bộ nhớ
dataframe = None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    try:
        dataframe = pd.read_excel(filepath)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Lưu file vào thư mục uploads và đọc nội dung
    if dataframe is None:
        return jsonify({"error": "No data available. Please upload a file first."}), 400

    user_question = request.json.get('question', '')
    if not user_question:
        return jsonify({"error": "Question is required"}), 400

    # Tạo prompt dựa trên dữ liệu từ file Excel
    data_preview = dataframe  # Xem trước 5 dòng đầu của dữ liệu
    prompt = f"""
    Dưới đây là một phần của dữ liệu từ file Excel mà người dùng đã tải lên:
    {data_preview}

    Người dùng hỏi: {user_question}
    Hãy trả lời dựa trên dữ liệu trong file này.
    """

    try:

        # Gửi yêu cầu trả lời câu hỏi dựa trên tệp đã tải lên
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Chọn mô hình
            messages=[{
                "role": "system", "content": "You are a helpful data analyst."
            }, {
                "role": "user", "content": prompt
            }],
            max_tokens=10000,  # Số tokens tối đa
        )

        # Lấy câu trả lời và trả về cho người dùng
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)