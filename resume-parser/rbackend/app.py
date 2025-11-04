from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import openai
import os

app = Flask(__name__)
CORS(app)

# ✅ Replace this with your actual API key
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route('/')
def home():
    return "Resume Parser Backend is Running!"

@app.route('/extract_skills', methods=['POST'])
def extract_skills():
    try:
        pdf_file = request.files['file']

        # Read PDF content
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

        # Call OpenAI API to extract skills
        prompt = f"Extract only the professional skills mentioned in this resume:\n{text}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        skills = response["choices"][0]["message"]["content"].strip()

        return jsonify({"skills": skills})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
