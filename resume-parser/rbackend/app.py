from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# ✅ Load API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

@app.route('/')
def home():
    return "✅ Resume Parser Backend with OpenAI is Running!"

@app.route('/extract_skills', methods=['POST'])
def extract_skills():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        pdf_file = request.files['file']
        text = extract_text_from_pdf(pdf_file)

        if not text.strip():
            return jsonify({"error": "No text found in the PDF."}), 400

        # ✅ Use OpenAI API to extract structured data
        prompt = f"""
        Extract the following details from this resume:
        - Full Name
        - Email
        - Phone
        - Key Skills (list)
        Resume Text:
        {text}
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        result_text = response.output_text

        return jsonify({"skills": result_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
