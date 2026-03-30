from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from pdf_service import HtmlToPdfRequest, generate_pdf

app = FastAPI(title="HTML to PDF API")


@app.on_event("startup")
def startup_event():
    print("[STARTUP] HTML to PDF API is starting...", flush=True)


@app.get("/health")
def health():
    print("[HEALTH] Health check called", flush=True)
    return {"status": "ok"}


@app.post("/html-to-pdf")
def html_to_pdf(payload: HtmlToPdfRequest, request: Request):
    client_host = request.client.host if request.client else "unknown"
    print(f"[REQUEST] /html-to-pdf called from {client_host}", flush=True)
    print(f"[REQUEST] Requested file name: {payload.file_name}", flush=True)

    try:
        pdf_path, download_name = generate_pdf(payload.html, payload.file_name)
        print(f"[SUCCESS] Returning generated PDF: {pdf_path}", flush=True)

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=download_name
        )

    except ValueError as e:
        print(f"[VALIDATION ERROR] {str(e)}", flush=True)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"[ERROR] Unexpected server error: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/html-file-to-pdf")
def html_file_to_pdf(file: UploadFile = File(...)):
    print(f"[FILE REQUEST] Received file: {file.filename}", flush=True)

    try:
        if not file.filename.lower().endswith(".html"):
            raise ValueError("Only .html files are supported")

        content = file.file.read()
        html = content.decode("utf-8", errors="ignore")
        output_name = file.filename.rsplit(".", 1)[0] + ".pdf"

        pdf_path, download_name = generate_pdf(html, output_name)
        print(f"[SUCCESS] Returning generated PDF from file: {pdf_path}", flush=True)

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=download_name
        )

    except ValueError as e:
        print(f"[VALIDATION ERROR] {str(e)}", flush=True)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"[ERROR] File conversion failed: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail="Internal server error")