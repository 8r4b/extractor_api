import os
import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
from fastapi import UploadFile
import tempfile

async def read_resume(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    content = await file.read()

    if ext == ".pdf":
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "temp_resume.pdf")
            with open(temp_path, "wb") as f:
                f.write(content)
            doc = fitz.open(temp_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()  # IMPORTANT: close file before cleanup!
            return text

    elif ext == ".docx":
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "temp_resume.docx")
            with open(temp_path, "wb") as f:
                f.write(content)
            doc = docx.Document(temp_path)
            return "\n".join([para.text for para in doc.paragraphs])

    elif ext in [".png", ".jpg", ".jpeg"]:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "temp_resume_img.png")
            with open(temp_path, "wb") as f:
                f.write(content)
            img = Image.open(temp_path)
            return pytesseract.image_to_string(img)

    return ""
