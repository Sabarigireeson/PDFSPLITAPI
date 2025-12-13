from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader, PdfWriter
import os
import io
import base64

app = FastAPI()

# ✅ Health check (VERY IMPORTANT for Render)
@app.get("/")
def health():
    return {"status": "ok"}

def split_pdf_to_pages_bytes(pdf_bytes: bytes, original_name: str):
    reader = PdfReader(io.BytesIO(pdf_bytes))

    base_name = os.path.splitext(original_name)[0]
    total_pages = len(reader.pages)

    pad = len(str(total_pages))
    total_str = str(total_pages).zfill(pad)

    output_files = []

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        page_num = str(i).zfill(pad)
        filename = f"{base_name}_{page_num}-{total_str}.pdf"

        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        output_files.append({
            "filename": filename,
            "content": base64.b64encode(buffer.read()).decode("utf-8")
        })

    return output_files


@app.post("/split-pdf")
async def split_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    # ✅ HARD LIMIT (Render free tier protection)
    if len(pdf_bytes) > 5 * 1024 * 1024:  # 5 MB
        return {
            "status": "error",
            "message": "File too large for Render free tier"
        }

    pages = split_pdf_to_pages_bytes(pdf_bytes, file.filename)
    return {"pages": pages}
