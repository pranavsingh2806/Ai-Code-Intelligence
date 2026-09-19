"""
main.py
FastAPI application entry-point for AI Code Intelligence.
"""
from __future__ import annotations

from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ast_parser import parse_python_ast
from input_handler import extract_code
from orchestrator import analyze

load_dotenv()

app = FastAPI(title="AI Code Intelligence", version="1.0.0")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:5173",       # Vite dev server
    # "https://your-production-domain.com",   # <-- ADD PRODUCTION ORIGIN HERE
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global HTTPException handler — always returns the standard JSON shape
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "language_detected": None,
            "files_analyzed": [],
            "files_skipped": [],
            "ast_summary": None,
            "outputs": {
                "explanation": {"status": "error", "content": ""},
                "diagram":     {"status": "error", "content": ""},
                "api_docs":    {"status": "error", "content": ""},
                "refactor":    {"status": "error", "content": ""},
            },
            "error": exc.detail,
        },
    )


# ---------------------------------------------------------------------------
# POST /api/analyze
# ---------------------------------------------------------------------------
@app.post("/api/analyze")
async def api_analyze(
    input_type: str              = Form(...),
    code:       Optional[str]    = Form(None),
    language:   Optional[str]    = Form(None),
    file:       Optional[UploadFile] = File(None),
) -> JSONResponse:
    """
    Accepts multipart/form-data with:
      - input_type : "paste" | "file" | "zip"
      - code       : raw source text (paste mode)
      - language   : optional language hint
      - file       : uploaded file/zip (file/zip mode)

    Returns the standard analysis JSON shape.
    """
    # ------------------------------------------------------------------
    # 1. Extract / normalise code
    # ------------------------------------------------------------------
    try:
        extracted_code, files_analyzed, files_skipped, detected_language = (
            await extract_code(input_type, code, file)
        )
    except HTTPException:
        raise
    except Exception as exc:
        return _error_response(str(exc))

    effective_language = language or detected_language

    # ------------------------------------------------------------------
    # 2. AST parse (Python only)
    # ------------------------------------------------------------------
    ast_summary: Any = None
    if effective_language == "python":
        ast_summary = parse_python_ast(extracted_code)

    # ------------------------------------------------------------------
    # 3. Run LLM analysis concurrently
    # ------------------------------------------------------------------
    try:
        result = await analyze(extracted_code, effective_language, ast_summary)
    except Exception as exc:
        return _error_response(str(exc))

    # ------------------------------------------------------------------
    # 4. Assemble response
    # ------------------------------------------------------------------
    return JSONResponse(
        content={
            "status":            result["status"],
            "language_detected": effective_language,
            "files_analyzed":    files_analyzed,
            "files_skipped":     files_skipped,
            "ast_summary":       ast_summary,
            "outputs":           result["outputs"],
            "error":             None,
        }
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _error_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "status":            "error",
            "language_detected": None,
            "files_analyzed":    [],
            "files_skipped":     [],
            "ast_summary":       None,
            "outputs": {
                "explanation": {"status": "error", "content": ""},
                "diagram":     {"status": "error", "content": ""},
                "api_docs":    {"status": "error", "content": ""},
                "refactor":    {"status": "error", "content": ""},
            },
            "error": message,
        },
    )
