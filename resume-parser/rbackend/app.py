from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import json
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Load API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
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

        # ------------------------------
        #      OPENAI SYSTEM PROMPT
        # ------------------------------
        prompt = f"""
        Extract the following fields from the resume text below.
        Return ONLY a valid JSON object. No explanations.

        Required JSON format:
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

        # Raw text returned by OpenAI
        output_text = response.output_text.strip()

        # ----------------------------------------------------
        #  FIX: Convert OpenAI's JSON string → Python dict
        # ----------------------------------------------------
        try:
            extracted_json = json.loads(output_text)   # Clean JSON
        except json.JSONDecodeError:
            # In case the model adds extra text, try to extract JSON substring
            import re
            json_match = re.search(r"\{.*\}", output_text, re.DOTALL)
            if json_match:
                extracted_json = json.loads(json_match.group(0))
            else:
                return jsonify({
                    "error": "Failed to parse JSON from OpenAI response",
                    "raw_output": output_text
                }), 500

        return jsonify(extracted_json)   # CLEAN JSON RESPONSE

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
