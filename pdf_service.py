import os
import uuid
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "generated_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class HtmlToPdfRequest(BaseModel):
    html: str = Field(..., min_length=1, description="Full HTML content")
    file_name: str = Field(default="output.pdf", description="Desired PDF file name")


def generate_pdf(html: str, file_name: str):
    print("[SERVICE] Starting PDF generation...")

    if not html or not html.strip():
        print("[SERVICE] HTML content is empty")
        raise ValueError("HTML content is required")

    safe_name = file_name if file_name.endswith(".pdf") else f"{file_name}.pdf"
    unique_name = f"{uuid.uuid4()}_{safe_name}"
    pdf_path = os.path.join(OUTPUT_DIR, unique_name)

    print(f"[SERVICE] Output path resolved: {pdf_path}")

    try:
        with sync_playwright() as p:
            print("[SERVICE] Launching Chromium browser...")
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()
            print("[SERVICE] Setting HTML content in browser...")
            page.set_content(html, wait_until="networkidle")

            print("[SERVICE] Generating PDF now...")
            page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "20mm",
                    "right": "15mm",
                    "bottom": "20mm",
                    "left": "15mm"
                }
            )

            browser.close()
            print("[SERVICE] Chromium browser closed")

        print(f"[SERVICE] PDF generated successfully: {pdf_path}")
        return pdf_path, safe_name

    except Exception as e:
        print(f"[SERVICE ERROR] PDF generation failed: {str(e)}")
        raise


async def generate_pdf_from_file(file):
    if not file.filename.lower().endswith(".html"):
        raise ValueError("Only .html files are supported")

    content = await file.read()
    html = content.decode("utf-8", errors="ignore")

    output_name = os.path.splitext(file.filename)[0] + ".pdf"
    return generate_pdf(html, output_name)