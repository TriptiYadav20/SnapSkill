from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import spacy
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ Enables CORS for all origins

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Dummy Job Description (can be updated with a real one)
JOB_DESCRIPTION = """
We are looking for a Python developer with experience in Flask, REST APIs, 
machine learning, and teamwork. Knowledge of NLP is a plus.
"""

# Extract text from uploaded resume PDF
def extract_text_from_pdf(file):
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
    except Exception as e:
        print("❌ PDF extraction error:", e)
        traceback.print_exc()
        return None

# Extract keywords using spaCy POS tagging
def extract_keywords(text):
    doc = nlp(text.lower())
    return list(set([
        token.lemma_ for token in doc
        if token.pos_ in ("NOUN", "PROPN", "ADJ", "VERB")
    ]))

# ATS Matching Endpoint
@app.route("/match", methods=["POST"])
def match_resume():
    try:
        resume = request.files.get("resume")
        if not resume:
            return jsonify({"error": "No resume uploaded"}), 400

        resume_text = extract_text_from_pdf(resume)
        if resume_text is None:
            return jsonify({"error": "Failed to extract text from PDF"}), 400

        resume_keywords = extract_keywords(resume_text)
        jd_keywords = extract_keywords(JOB_DESCRIPTION)

        matched = list(set(resume_keywords) & set(jd_keywords))
        missing = list(set(jd_keywords) - set(resume_keywords))
        ats_score = int(len(matched) / len(jd_keywords) * 100) if jd_keywords else 0

        return jsonify({
            "score": ats_score,
            "matched_keywords": matched,
            "missing_keywords": missing
        })

    except Exception as e:
        print("❌ Match error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Run server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
