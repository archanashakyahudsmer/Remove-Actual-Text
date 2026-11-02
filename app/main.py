from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path
from typing import Annotated

import pymupdf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask
from fastapi.staticfiles import StaticFiles

# sys._MEIPASS is set by PyInstaller when running as a frozen exe.
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
MAX_UPLOAD_BYTES = 100 * 1024 * 1024  # 100 MB

app = FastAPI(
    title="PDF Span ActualText Remover",
    description=(
        "Remove only the /ActualText property from /Span "
        "structure elements while preserving their tags and children."
    ),
    version="2.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "favicon.ico", media_type="image/x-icon")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    index_file = FRONTEND_DIR / "index.html"
    return index_file.read_text(encoding="utf-8")


def is_span_structure_element(pdf: pymupdf.Document, xref: int) -> bool:
    """Return True when an indirect PDF object has /S /Span."""
    try:
        obj = pdf.xref_object(xref, compressed=False)
        return bool(re.search(r"/S\s*/Span\b", obj))
    except Exception:
        return False


def process_pdf_bytes(pdf_bytes: bytes) -> tuple[bytes, dict]:
    """
    Remove only /ActualText from objects identified as /Span.

    Preserve /S, /K, and all other object properties.
    Do not intentionally modify page content streams.
    """
    try:
        pdf = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a readable PDF.",
        ) from exc

    try:
        if pdf.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This PDF is encrypted. Upload an unencrypted PDF "
                    "that you are authorized to modify."
                ),
            )

        span_xrefs = [
            xref
            for xref in range(1, pdf.xref_length())
            if is_span_structure_element(pdf, xref)
        ]

        if not span_xrefs:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No /Span structure elements were found. "
                    "The PDF may be untagged or use a different structure."
                ),
            )

        updated = 0
        already_missing = 0

        for xref in span_xrefs:
            try:
                # Read the object's existing ActualText value.
                value_type, value = pdf.xref_get_key(xref, "ActualText")

                if value_type == "null":
                    already_missing += 1
                    continue

                # Remove ONLY ActualText.
                # Never clear /K or delete the Span structure element.
                pdf.xref_set_key(xref, "ActualText", "null")
                updated += 1

            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Could not remove ActualText from "
                        f"PDF structure object {xref}."
                    ),
                ) from exc

        output = pdf.tobytes(
            garbage=0,
            deflate=True,
        )

        metadata = {
            "pages": len(pdf),
            "span_elements_found": len(span_xrefs),
            "span_elements_updated": updated,
            "span_elements_without_actualtext": already_missing,
        }

        return output, metadata

    finally:
        pdf.close()


@app.post("/api/process-pdf")
async def process_pdf(
    file: Annotated[UploadFile, File(...)],
) -> FileResponse:
    filename = file.filename or "input.pdf"

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=415,
            detail="Please upload a .pdf file.",
        )

    pdf_bytes = await file.read()

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(pdf_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="PDF is too large. Maximum upload size is 100 MB.",
        )

    processed_bytes, _metadata = process_pdf_bytes(pdf_bytes)

    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            prefix="processed_",
            suffix=".pdf",
            delete=False,
        ) as temp:
            temp_path = Path(temp.name)
            temp.write(processed_bytes)

        safe_stem = Path(filename).stem
        output_name = f"{safe_stem}_actualtext_removed.pdf"

        return FileResponse(
            path=temp_path,
            media_type="application/pdf",
            filename=output_name,
            background=BackgroundTask(
                temp_path.unlink,
                missing_ok=True,
            ),
        )

    except Exception:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise