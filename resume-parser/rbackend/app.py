from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Load API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


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

        if text.startswith("Error reading PDF"):
            return jsonify({"error": text}), 400

        if not OPENAI_API_KEY:
            return jsonify({"error": "Missing OPENAI_API_KEY"}), 500

        # STRICT JSON OUTPUT
        prompt = f"""
        You are an advanced resume parser.
        Extract the following fields from the resume text.
        Respond ONLY in valid JSON. No explanation. No extra text.

        Required Fields:
        - name
        - email
        - phone
        - skills
        - education
        - experience
        - projects

        Resume Text:
        {text}
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            response_format={"type": "json_object"}   # 🔥 Forces JSON output
        )

        # Extract JSON output
        final_json = response.output_text

        return jsonify({"result": final_json})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
