import io
from typing import Optional
from pypdf import PdfReader
from docx import Document

class FileHandler:
    MAX_SIZE_MB = 10
    ALLOWED_TYPES = ['pdf', 'docx', 'doc', 'txt']
    
    @classmethod
    def validate_file(cls, filename: str, file_size: int) -> tuple[bool, str]:
        ext = filename.lower().split('.')[-1]
        
        if ext not in cls.ALLOWED_TYPES:
            return False, f"File type '{ext}' not supported. Upload PDF, DOCX, or TXT"
        
        size_mb = file_size / (1024 * 1024)
        if size_mb > cls.MAX_SIZE_MB:
            return False, f"File too large. Max size is {cls.MAX_SIZE_MB}MB"
        
        return True, "Valid"
    
    @classmethod
    def extract_text(cls, filename: str, content: bytes) -> str:
        ext = filename.lower().split('.')[-1]
        
        if ext == 'txt':
            return cls._extract_txt(content)
        elif ext == 'pdf':
            return cls._extract_pdf(content)
        elif ext in ['doc', 'docx']:
            return cls._extract_docx(content)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    @staticmethod
    def _extract_txt(content: bytes) -> str:
        return content.decode('utf-8', errors='ignore')
    
    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    
    @staticmethod
    def _extract_docx(content: bytes) -> str:
        doc = Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])