import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PDFGenerator:
    
    COLORS = {
        'primary': HexColor('#1a1a2e'),
        'secondary': HexColor('#16213e'),
        'accent': HexColor('#0f3460'),
        'highlight': HexColor('#e94560'),
        'text': HexColor('#333333'),
        'light_text': HexColor('#666666'),
        'bg': white
    }
    
    def __init__(self, user_name: str, email: str):
        self.user_name = user_name
        self.email = email
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            name='Name',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.COLORS['primary'],
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Contact',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLORS['light_text'],
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.COLORS['highlight'],
            spaceBefore=16,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Summary',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLORS['text'],
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.COLORS['primary'],
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLORS['accent'],
            fontName='Helvetica-Oblique',
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='Bullet',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.COLORS['text'],
            leftIndent=15,
            spaceAfter=4,
            leading=12,
            bulletIndent=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='Skill',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.COLORS['text'],
            spaceAfter=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='Education',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLORS['text'],
            spaceAfter=6
        ))
    
    def generate(self, optimized_data: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        
        story.append(Paragraph(self.user_name, self.styles['Name']))
        story.append(Paragraph(self.email, self.styles['Contact']))
        story.append(Spacer(1, 0.2*inch))
        
        if optimized_data.get('summary'):
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeader']))
            story.append(Paragraph(optimized_data['summary'], self.styles['Summary']))
        
        if optimized_data.get('experience'):
            story.append(Paragraph("WORK EXPERIENCE", self.styles['SectionHeader']))
            for exp in optimized_data['experience']:
                company_line = f"<b>{exp.get('role', '')}</b> | {exp.get('company', '')}"
                story.append(Paragraph(company_line, self.styles['JobTitle']))
                story.append(Paragraph(exp.get('duration', ''), self.styles['Company']))
                for bullet in exp.get('bullets', []):
                    story.append(Paragraph(f"• {bullet}", self.styles['Bullet']))
                story.append(Spacer(1, 0.1*inch))
        
        if optimized_data.get('skills'):
            story.append(Paragraph("CORE SKILLS", self.styles['SectionHeader']))
            skills_text = " | ".join(optimized_data['skills'])
            story.append(Paragraph(skills_text, self.styles['Skill']))
        
        if optimized_data.get('education'):
            story.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
            for edu in optimized_data['education']:
                edu_text = f"<b>{edu.get('degree', '')}</b> - {edu.get('institution', '')} ({edu.get('year', '')})"
                story.append(Paragraph(edu_text, self.styles['Education']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

def generate_resume_pdf(user_name: str, email: str, optimized_data: dict, output_path: str):
    generator = PDFGenerator(user_name, email)
    pdf_bytes = generator.generate(optimized_data)
    
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    return output_path