from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import extract_text_from_pdf, parse_resume
import os

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = "uploads"

@app.route('/')
def home():
    return jsonify({"message": "Resume Parser API running!"})

@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    with open(filepath, 'rb') as pdf_file:
        text = extract_text_from_pdf(pdf_file)
        result = parse_resume(text)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
