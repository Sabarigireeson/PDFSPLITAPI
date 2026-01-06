# PDF Splitter API using FastAPI and PyPDF2

from fastapi import FastAPI, UploadFile, HTTPException, File
from pypdf import PdfReader, PdfWriter
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

    # 🔐 HANDLE ENCRYPTED PDFs
    if reader.is_encrypted:
        try:
            reader.decrypt("")  # empty password (works for most PDFs)
        except Exception:
            raise ValueError("Encrypted PDF cannot be processed")

    base_name = os.path.splitext(original_name)[0]
    total_pages = len(reader.pages)

    pad = max(4, len(str(total_pages)))

    output_files = []

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        page_num = str(i).zfill(pad)
        filename = f"{page_num}_{base_name}.pdf"  #filename

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

    if len(pdf_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File too large for Render free tier"
        )

    try:
        pages = split_pdf_to_pages_bytes(pdf_bytes, file.filename)
        return {"pages": pages}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

