from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import base64
import io
import os
import traceback
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

# === Startup Logs ===
print("💡 Running resume_enhancer.py...")

# === Load environment variables ===
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
cohere_key = os.getenv("COHERE_API_KEY")
print("🔐 Loaded Cohere Key:", cohere_key[:8] + "..." if cohere_key else "❌ No API key found!")

# === LangChain Setup ===
from langchain_cohere import ChatCohere
from langchain.prompts import PromptTemplate

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB upload limit

llm = ChatCohere(model="command", temperature=0.5, cohere_api_key=cohere_key)

# === PDF Text Extraction ===
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)

# === Resume Enhancement Prompt ===
def get_suggestions_and_enhanced_resume(text):
    prompt = PromptTemplate(
        input_variables=["resume"],
        template="""
You are a highly experienced resume coach and expert resume writer.

Your goal is to enhance the following resume content and generate:
1. A list of clear, impactful, ATS-optimized suggestions.
2. A rewritten resume that is:
   - Professionally structured (Summary, Skills, Experience, Education, Projects, Achievements).
   - Keyword-rich and ATS-friendly.
   - Clean, modern, and ideally one page.
   - Improved with any available public profile content (LinkedIn, GitHub) if present in the resume.

Resume Input:
{resume}

Instructions:
- If the resume includes a LinkedIn or GitHub URL, extract valuable project descriptions, contributions, or achievements from them.
- Add a 'Projects' section if relevant projects or repos are available or can be inferred.
- Include a concise 'Achievements' section if accomplishments (awards, ranks, recognitions) are found or inferred.
- Reword experiences with measurable impact and bullet formatting.

Respond in the format:

Suggestions:
1. ...
2. ...
3. ...

Enhanced Resume:
Name: ...
Email: ...
LinkedIn: ...
GitHub: ...

Summary:
...

Experience:
- Role, Company (Dates)
  • Responsibility or achievement
  • Responsibility or achievement

Projects:
- Project Title
  • Description or technology used

Achievements:
- Achievement 1
- Achievement 2

Education:
- Degree, Institution, Year

Skills:
- Skill 1, Skill 2, Skill 3
"""
    )

    chain = prompt | llm
    response = chain.invoke({"resume": text})
    content = response.content.strip()

    try:
        suggestions_part = content.split("Enhanced Resume:")[0]
        resume_part = content.split("Enhanced Resume:")[1]

        suggestions = [
            line.strip()
            for line in suggestions_part.splitlines()
            if line.strip().startswith(tuple("123456789"))
        ]
        enhanced_text = resume_part.strip()

    except Exception as e:
        print("❌ Fallback parsing failed:", e)
        suggestions = ["Could not parse suggestions."]
        enhanced_text = "Error generating enhanced resume."

    return suggestions, enhanced_text

# === PDF Creation ===
def create_pdf_from_text(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=50)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='Title', fontSize=18, spaceAfter=10, alignment=TA_CENTER)
    header_style = ParagraphStyle(name='Header', fontSize=14, spaceAfter=6, spaceBefore=12, textColor=colors.HexColor("#4B0082"), alignment=TA_LEFT)
    body_style = ParagraphStyle(name='Body', fontSize=11, spaceAfter=5, alignment=TA_LEFT)
    bullet_style = ParagraphStyle(name='Bullet', fontSize=11, leftIndent=20, spaceAfter=4)

    story = []

    # Title
    story.append(Paragraph("Professional Resume", title_style))
    story.append(Spacer(1, 12))

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(":") and line[:-1].lower() in ["summary", "experience", "projects", "education", "skills", "achievements"]:
            story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
            story.append(Spacer(1, 6))
            story.append(Paragraph(line[:-1], header_style))
        elif line.startswith("- ") or line.startswith("• "):
            story.append(Paragraph(line, bullet_style))
        elif ":" in line and not line.startswith("•"):
            story.append(Paragraph(f"<b>{line}</b>", body_style))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# === Main API Route ===
@app.route("/enhance", methods=["POST"])
def enhance_resume():
    resume_file = request.files.get("resume")
    if not resume_file:
        print("❌ No resume file uploaded.")
        return jsonify({"error": "No resume uploaded"}), 400

    try:
        print("📄 Resume received:", resume_file.filename)

        # Add debug print
        print("📂 File type:", type(resume_file))
        print("📏 File size (approx):", len(resume_file.read()), "bytes")
        resume_file.seek(0)  # Important: Reset pointer before reading again

        resume_text = extract_text_from_pdf(resume_file)
        print("🧠 Extracted text length:", len(resume_text))

        suggestions, enhanced_resume_text = get_suggestions_and_enhanced_resume(resume_text)
        print("✅ Got suggestions and enhanced resume")

        enhanced_pdf = create_pdf_from_text(enhanced_resume_text)
        encoded_pdf = base64.b64encode(enhanced_pdf).decode("utf-8")

        print("📦 Sending enhanced resume...")
        return jsonify({
            "suggestions": suggestions,
            "enhanced_pdf": encoded_pdf
        })

    except Exception as e:
        print("❌ Enhancement Error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# === Run Server ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
