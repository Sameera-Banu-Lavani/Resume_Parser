import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import PyPDF2
from openai import OpenAI

# Your OpenAI API Key
OPENAI_API_KEY = "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"


app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

@app.route("/parse", methods=["POST"])
def parse_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Read PDF text
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # Process text with spaCy
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Summarize using OpenAI
    summary_prompt = f"Extract key details like name, skills, education, and experience from this resume:\n\n{text}"
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    summary = completion.choices[0].message.content

    return jsonify({
        "entities": entities,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(debug=True)






import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_entities_spacy(text):
    doc = nlp(text)
    entities = {
        "name": None,
        "education": [],
        "skills": [],
        "experience": []
    }

    # Extract Name (PERSON entity)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["name"] = ent.text
            break

    # Education keywords
    education_keywords = [
        "B.Tech", "M.Tech", "B.E", "M.E", "B.Sc", "M.Sc", "PhD", "Bachelor", "Master"
    ]
    for keyword in education_keywords:
        if keyword.lower() in text.lower():
            entities["education"].append(keyword)

    # Skills list
    skills_list = [
        "python", "java", "c++", "machine learning", "deep learning",
        "flask", "django", "sql", "html", "css", "javascript", "react",
        "data analysis", "nlp", "pandas", "numpy", "tensorflow", "pytorch"
    ]
    detected_skills = [s for s in skills_list if s in text.lower()]
    entities["skills"] = detected_skills

    # Experience extraction (simple heuristic)
    for line in text.split("\n"):
        if "experience" in line.lower():
            entities["experience"].append(line.strip())

    return entities


def refine_with_openai(text, entities):
    """
    Use OpenAI to improve entity extraction accuracy.
    """
    prompt = f"""
    Extract structured resume details from the text below.
    Include: Full Name, Education, Skills, and Experience.
    Return the output as a JSON object.
    Resume Text:
    {text}
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    try:
        refined = response.output[0].content[0].text
        return refined
    except Exception:
        return entities


@app.route("/parse", methods=["POST"])
def parse_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    text = extract_text_from_pdf(file)

    # Step 1: Extract entities using spaCy
    spacy_data = extract_entities_spacy(text)

    # Step 2: Refine results using OpenAI
    openai_data = refine_with_openai(text, spacy_data)

    return jsonify({
        "status": "success",
        "spacy_data": spacy_data,
        "openai_data": openai_data
    })


if __name__ == "__main__":
    app.run(debug=True)
