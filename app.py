from flask import Flask, request, jsonify, render_template
import pandas as pd
import openai
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# API Key của OpenAI
load_dotenv()  # Load biến môi trường từ file .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Đọc file Excel và lưu dữ liệu trong bộ nhớ
dataframe = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global dataframe
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Lưu file vào thư mục uploads và đọc nội dung
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        dataframe = pd.read_excel(filepath)
        return jsonify({"message": "File uploaded successfully", "columns": dataframe.columns.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    global dataframe
    if dataframe is None:
        return jsonify({"error": "No data available. Please upload a file first."}), 400

    user_question = request.json.get('question', '')
    if not user_question:
        return jsonify({"error": "Question is required"}), 400

    # Tạo prompt dựa trên dữ liệu từ file Excel
    data_preview = dataframe.head(5).to_string()  # Xem trước 5 dòng đầu của dữ liệu
    prompt = f"""
    Dưới đây là một phần của dữ liệu từ file Excel mà người dùng đã tải lên:
    {data_preview}

    Người dùng hỏi: {user_question}
    Hãy trả lời dựa trên dữ liệu trong file này.
    """

    try:
        # Gửi yêu cầu đến OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        reply = response['choices'][0]['message']['content']
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)