import mimetypes
import docx
from PIL import Image
import pytesseract
from pdfminer.high_level import extract_text

def extract_text_from_pdf(path):
    """Extrai texto de PDFs"""
    return extract_text(path)

def extract_text_from_image(path):
    """Extrai texto de imagens usando OCR"""
    img = Image.open(path)
    return pytesseract.image_to_string(img, lang="por")  # OCR em português

def extract_text_from_docx(path):
    """Extrai texto de arquivos DOCX"""
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(path):
    """Extrai texto de arquivos TXT"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text_auto(path, filename):
    """
    Detecta automaticamente o tipo do arquivo e extrai o texto.
    Suporta: PDF, imagens, DOCX, TXT
    Retorna None se o tipo não for suportado.
    """
    mime, _ = mimetypes.guess_type(filename)

    if mime == "application/pdf":
        return extract_text_from_pdf(path)
    elif mime and mime.startswith("image"):
        return extract_text_from_image(path)
    elif mime in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return extract_text_from_docx(path)
    elif mime == "text/plain":
        return extract_text_from_txt(path)
    else:
        # fallback: tenta TXT simples como último recurso
        try:
            return extract_text_from_txt(path)
        except Exception:
            return None
