"""
input_handler.py
Extracts and normalises code from paste, single-file upload, or zip archive.
"""
from __future__ import annotations

import io
import re
import zipfile
from collections import Counter
from typing import Optional

from fastapi import HTTPException, UploadFile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".go", ".rb", ".cs",
    ".cpp", ".c", ".h", ".html", ".css", ".json", ".yaml", ".md",
}

EXT_TO_LANGUAGE: dict[str, str] = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".java": "java", ".go": "go", ".rb": "ruby", ".cs": "csharp",
    ".cpp": "cpp", ".c": "c", ".h": "c", ".html": "html",
    ".css": "css", ".json": "json", ".yaml": "yaml", ".md": "markdown",
}

MAX_UPLOAD_BYTES = 10 * 1024 * 1024          # 10 MB raw upload guard
TOKEN_CAP        = 80_000                     # approximate token cap
CHAR_CAP         = TOKEN_CAP * 4              # ~320 000 chars


def _detect_language(ext_counts: Counter) -> str:
    """Return the language name for the most common extension."""
    for ext, _ in ext_counts.most_common():
        if ext in EXT_TO_LANGUAGE:
            return EXT_TO_LANGUAGE[ext]
    return "unknown"


def _detect_language_from_code(code: str) -> str:
    """Heuristic language detection from pasted source code.

    Each entry is (language, [patterns]).  A language is chosen when ANY of
    its patterns matches.  Entries are ordered so that more-specific signatures
    come before ambiguous ones (e.g. Java before Python, Go before Python).
    """
    signatures: list[tuple[str, list[str]]] = [
        # ── strongly-typed / distinctive keywords first ──────────────────────
        # Java: must match java-specific imports or JVM idioms
        ("java",       [r"^\s*import\s+java\.", r"\bpublic\s+static\s+void\s+main\b",
                        r"\bSystem\.out\.", r"\bSystem\.in\b"]),
        # C#: namespace or using System are unambiguous
        ("csharp",     [r"\busing\s+System\b", r"\bnamespace\s+\w+",
                        r"\bConsole\.(Write|Read)\b"]),
        ("cpp",        [r"#include\s*<[a-z_]+>", r"\bstd::", r"\bcout\b"]),
        ("c",          [r"#include\s*<[a-z_]+\.h>", r"\bprintf\s*\(",
                        r"\bmalloc\s*\(", r"int\s+main\s*\(\s*(void|int)"]),
        ("go",         [r"^package\s+\w+", r"^\s*import\s+\(",
                        r"\bfunc\s+\w+\s*\("]),
        ("typescript", [r":\s*(string|number|boolean|any|void)\b",
                        r"\binterface\s+\w+", r"^\s*import\s+.+\s+from\s+['\"]"]),
        ("javascript", [r"\bconsole\.log\(", r"=>\s*{",
                        r"\brequire\s*\(", r"^\s*import\s+.+\s+from\s+['\"]"]),
        # Ruby: `end` keyword is unambiguous; def alone is not
        ("ruby",       [r"\bputs\b", r"^\s*def\s+\w+.*\n[\s\S]*?\bend\b"]),
        # Python: colon-terminated def/class, or from…import
        ("python",     [r"^\s*def\s+\w+\s*\(.*\):", r"^\s*class\s+\w+.*:",
                        r"^\s*from\s+\w+\s+import\s+", r"print\(",
                        r"^\s*import\s+[a-z_]+\s*$"]),
        # ── markup / data formats ─────────────────────────────────────────────
        ("html",       [r"<!DOCTYPE\s+html", r"<html[\s>]", r"<body[\s>]"]),
        ("css",        [r"@media\b", r"@import\b",
                        r"[a-z-]+\s*:\s*[^;{]+;"]),
        ("json",       [r"^\s*\{[\s\S]*\"[^\"]+\"\s*:", r"^\s*\["]),
        ("yaml",       [r"^---", r"^\w[\w ]*:\s+\S"]),
        ("markdown",   [r"^#{1,6} ", r"^\*\*\S", r"^\s*- \S"]),
    ]

    for language, patterns in signatures:
        for pattern in patterns:
            if re.search(pattern, code, re.MULTILINE):
                return language

    return "unknown"


def _suffix(filename: str) -> str:
    dot = filename.rfind(".")
    return filename[dot:].lower() if dot != -1 else ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
async def extract_code(
    input_type: str,
    code:        Optional[str],
    file:        Optional[UploadFile],
) -> tuple[str, list[str], list[str], str]:
    """
    Returns (concatenated_code, files_analyzed, files_skipped, language).
    Raises HTTPException on validation failures.
    """
    if input_type == "paste":
        if not code:
            raise HTTPException(status_code=400, detail="No code provided for paste input.")
        return code, ["pasted_code"], [], _detect_language_from_code(code)

    if input_type in ("file", "zip"):
        if file is None:
            raise HTTPException(status_code=400, detail="No file uploaded.")

        raw = await file.read()
        if len(raw) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Upload exceeds 10 MB limit.")

        if input_type == "file":
            return _handle_single_file(file.filename or "uploaded_file", raw)

        # zip
        return _handle_zip(raw)

    raise HTTPException(status_code=400, detail=f"Unknown input_type: {input_type!r}")


# ---------------------------------------------------------------------------
# Single-file helper
# ---------------------------------------------------------------------------
def _handle_single_file(filename: str, raw: bytes) -> tuple[str, list[str], list[str], str]:
    ext = _suffix(filename)
    try:
        content = raw.decode("utf-8", errors="replace")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode file as UTF-8.")

    lang = EXT_TO_LANGUAGE.get(ext, "unknown")
    return content, [filename], [], lang


# ---------------------------------------------------------------------------
# Zip helper
# ---------------------------------------------------------------------------
def _handle_zip(raw: bytes) -> tuple[str, list[str], list[str], str]:
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid zip archive.")

    parts: list[str]            = []
    files_analyzed: list[str]   = []
    files_skipped_ext: list[str]   = []   # disallowed extension or unreadable
    files_skipped_token: list[str] = []   # over token cap
    ext_counts: Counter         = Counter()
    running_chars = 0
    budget_exhausted = False

    for info in sorted(zf.infolist(), key=lambda i: i.filename):
        if info.is_dir():
            continue
        ext = _suffix(info.filename)
        if ext not in ALLOWED_EXTENSIONS:
            files_skipped_ext.append(info.filename)
            continue

        if budget_exhausted:
            files_skipped_token.append(info.filename)
            continue

        try:
            content = zf.read(info.filename).decode("utf-8", errors="replace")
        except Exception:
            files_skipped_ext.append(info.filename)
            continue

        chunk = f"# --- FILE: {info.filename} ---\n{content}\n"
        if running_chars + len(chunk) > CHAR_CAP:
            files_skipped_token.append(info.filename)
            budget_exhausted = True
            continue

        parts.append(chunk)
        files_analyzed.append(info.filename)
        ext_counts[ext] += 1
        running_chars += len(chunk)

    if not parts:
        raise HTTPException(status_code=400, detail="Zip contained no readable source files.")

    files_skipped = files_skipped_ext + files_skipped_token
    concatenated = "\n".join(parts)
    if files_skipped_token:
        concatenated += f"\n# [TRUNCATED: {len(files_skipped_token)} files skipped due to token limit]"

    language = _detect_language(ext_counts)
    return concatenated, files_analyzed, files_skipped, language
