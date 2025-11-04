import spacy
import PyPDF2
import re

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def parse_resume(text):
    doc = nlp(text)
    info = {"Name": None, "Email": None, "Phone": None, "Skills": []}

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            info["Name"] = ent.text
            break

    email = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text)
    if email:
        info["Email"] = email.group(0)

    phone = re.search(r'\+?\d[\d -]{8,12}\d', text)
    if phone:
        info["Phone"] = phone.group(0)

    skills = ["python", "java", "flask", "django", "sql", "react", "ai", "machine learning"]
    for s in skills:
        if s.lower() in text.lower():
            info["Skills"].append(s.capitalize())

    return info
