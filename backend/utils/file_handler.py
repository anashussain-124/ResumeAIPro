import re

def extract_text_from_txt(file_content: bytes) -> str:
    return file_content.decode('utf-8')

def extract_text_from_pdf(file_content: bytes) -> str:
    import io
    from pypdf import PdfReader
    
    reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    import io
    from docx import Document
    
    doc = Document(io.BytesIO(file_content))
    return "\n".join([para.text for para in doc.paragraphs])

def process_uploaded_file(filename: str, content: bytes) -> str:
    ext = filename.lower().split('.')[-1]
    
    if ext == 'txt':
        return extract_text_from_txt(content)
    elif ext == 'pdf':
        return extract_text_from_pdf(content)
    elif ext in ['doc', 'docx']:
        return extract_text_from_docx(content)
    else:
        raise ValueError(f"Unsupported file type: {ext}")