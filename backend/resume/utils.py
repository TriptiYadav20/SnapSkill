import os
import markdown
import pdfkit
from jinja2 import Environment, FileSystemLoader

# 🔧 Set up Jinja2 environment with the correct template path
base_dir = os.path.dirname(os.path.abspath(_file_))  # Points to 'resume/' directory
templates_dir = os.path.join(base_dir, "templates")    # Points to 'resume/templates/'

env = Environment(loader=FileSystemLoader(templates_dir))


def convert_markdown_to_html(markdown_text: str) -> str:
    """Converts markdown text to HTML using Python-Markdown."""
    return markdown.markdown(markdown_text)


def render_template_with_content(template_name: str, resume_content: str) -> str:
    """Loads an HTML template and injects the resume content."""
    template_path = os.path.join(templates_dir, template_name)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"❌ Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()

    return template.replace("{{ content }}", resume_content)


def save_html_as_pdf(html_content: str, output_path: str) -> None:
    """Converts HTML content to a PDF using pdfkit + wkhtmltopdf."""
    config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Users\hpnar\OneDrive\Desktop\ai_resume_builder\SnapSkill-1\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )
    options = {
        "enable-local-file-access": None
    }

    pdfkit.from_string(html_content, output_path, options=options, configuration=config)


def is_valid_template(template_name: str) -> bool:
    """Checks if the given template exists in the templates directory."""
    path = os.path.join(templates_dir, template_name)
    return os.path.isfile(path)
