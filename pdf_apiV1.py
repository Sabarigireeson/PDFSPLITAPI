from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader, PdfWriter
import os
import io
import base64

app = FastAPI()

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

        file_b64 = base64.b64encode(buffer.read()).decode("utf-8")

        output_files.append({
            "filename": filename,
            "content": file_b64
        })

    return output_files


@app.post("/split-pdf")
async def split_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    pages = split_pdf_to_pages_bytes(pdf_bytes, file.filename)

    return {"pages": pages}
