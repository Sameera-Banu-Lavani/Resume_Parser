from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import json
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
    return "✅ Resume Parser Backend Running!"


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

        # STRICT JSON PROMPT
        prompt = f"""
        Extract the following details from this resume.
        
        Return ONLY valid JSON. No extra text. No explanation.

        Required JSON fields:
        {{
            "name": "",
            "email": "",
            "phone": "",
            "skills": []
        }}

        Resume Text:
        {text}
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        raw_output = response.output_text.strip()

        # Try fixing common issues where model adds text before/after JSON
        try:
            # Extract JSON portion only
            json_start = raw_output.find("{")
            json_end = raw_output.rfind("}") + 1
            cleaned_json = raw_output[json_start:json_end]

            parsed = json.loads(cleaned_json)
        except Exception:
            parsed = {"raw_output": raw_output, "error": "Failed to auto-parse JSON"}

        return jsonify(parsed)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
