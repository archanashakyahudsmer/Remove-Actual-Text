# PDF Span Text Remover

A small local web app: HTML frontend + FastAPI backend + PyMuPDF processing.

## What it does

- Lets a user select or drag-and-drop a PDF in the browser.
- Sends the PDF to `POST /api/process-pdf`.
- Finds indirect PDF structure elements with `/S /Span`.
- Sets each found element's `/K` and `/ActualText` entries to `null`.
- Returns a modified PDF download.

**Important limitations:** this is a broad experimental operation, not a universal
accessibility-preserving transformation. It removes the content association from
every `/Span` element it finds, not just one selected span. This can affect
accessibility, reading order, and screen-reader behavior. It does not intentionally
modify page content streams, but validate the output in Adobe Acrobat and keep the
original PDF. PDFs with unusual structures may need a specialized implementation.

## Requirements

- Python 3.10+
- Internet access for the initial package installation

## Run on Windows / VS Code

Open PowerShell in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the local address printed by Uvicorn, normally `http://127.0.0.1:8000`.

## API

- `GET /` serves the frontend.
- `POST /api/process-pdf` accepts multipart form field `file` and returns a PDF.
- `GET /docs` opens FastAPI's interactive API documentation.

Maximum upload size: 100 MB. The app is intended for local development and does not
include authentication, persistent storage, or production deployment hardening.
