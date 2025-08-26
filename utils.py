import mimetypes
import docx
from pdfminer.high_level import extract_text

def extract_text_from_pdf(path):
    """Extrai texto de PDFs digitais"""
    try:
        return extract_text(path)
    except Exception:
        return None

def extract_text_from_docx(path):
    """Extrai texto de arquivos DOCX"""
    try:
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return None

def extract_text_from_txt(path):
    """Extrai texto de arquivos TXT"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None

def extract_text_auto(path, filename):
    """
    Detecta automaticamente o tipo do arquivo e extrai o texto.
    Suporta: PDF, DOCX, TXT
    Para imagens ou outros tipos, retorna None.
    """
    mime, _ = mimetypes.guess_type(filename)

    if mime == "application/pdf":
        return extract_text_from_pdf(path)
    elif mime in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return extract_text_from_docx(path)
    elif mime == "text/plain":
        return extract_text_from_txt(path)
    elif mime and mime.startswith("image"):
        # Não há OCR local no Render
        return None
    else:
        # Tipo desconhecido
        return None
