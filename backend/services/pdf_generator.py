import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors

def generate_premium_pdf(optimized_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', 
        parent=styles['Heading1'], 
        fontSize=20, 
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=15,
        alignment=1 # Center
    )
    heading_style = ParagraphStyle(
        'HeadingStyle', 
        parent=styles['Heading2'], 
        fontSize=12, 
        textColor=colors.HexColor('#0f3460'),
        spaceAfter=5,
        spaceBefore=15,
        textTransform='uppercase'
    )
    body_style = ParagraphStyle(
        'BodyStyle', 
        parent=styles['Normal'], 
        fontSize=10, 
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        leading=14
    )
    
    elements = []
    
    if optimized_data.get("name"):
        elements.append(Paragraph(optimized_data["name"], title_style))
    else:
        elements.append(Paragraph("Optimized Resume", title_style))
    
    def add_section(title, content_list):
        elements.append(Paragraph(title, heading_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'), spaceBefore=1, spaceAfter=8))
        for p in content_list:
            elements.append(p)
            
    if "summary" in optimized_data and optimized_data["summary"]:
        add_section("Professional Summary", [Paragraph(optimized_data["summary"], body_style)])
        
    if "experience" in optimized_data and optimized_data["experience"]:
        exp_elements = []
        for exp in optimized_data["experience"]:
            exp_header = f"<b>{exp['role']}</b> | {exp['company']} <font color='#666666'>({exp['duration']})</font>"
            exp_elements.append(Paragraph(exp_header, body_style))
            for bullet in exp.get("bullets", []):
                exp_elements.append(Paragraph(f"• {bullet}", body_style))
            exp_elements.append(Spacer(1, 5))
        add_section("Professional Experience", exp_elements)
            
    if "skills" in optimized_data and optimized_data["skills"]:
        if isinstance(optimized_data["skills"], dict):
            skills_text = []
            for k, v in optimized_data["skills"].items():
                skills_text.append(f"<b>{k}:</b> " + ", ".join(v))
            skills_paragraphs = [Paragraph(s, body_style) for s in skills_text]
        else:
            skills_text = " • ".join(optimized_data["skills"])
            skills_paragraphs = [Paragraph(skills_text, body_style)]
        add_section("Core Competencies", skills_paragraphs)
        
    if "education" in optimized_data and optimized_data["education"]:
        edu_elements = []
        for edu in optimized_data["education"]:
            edu_header = f"<b>{edu['degree']}</b>, {edu['institution']} <font color='#666666'>({edu['year']})</font>"
            edu_elements.append(Paragraph(edu_header, body_style))
        add_section("Education", edu_elements)
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
