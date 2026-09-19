"""
llm_client.py
Async wrappers around the HuggingFace inference API for each analysis task.
"""
from __future__ import annotations

import os
import sys
import httpx
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

MODEL_ID   = "Qwen/Qwen2.5-Coder-7B-Instruct"
ENDPOINT   = "https://router.huggingface.co/v1/chat/completions"
MAX_TOKENS = 1024

_token: Optional[str] = None


def _get_token() -> str:
    global _token
    if _token is None:
        _token = os.getenv("HF_API_TOKEN", "")
        if not _token:
            print(
                "\n[ERROR] HF_API_TOKEN is not set in your .env file.\n"
                "  Add:  HF_API_TOKEN=hf_...\n"
                "  Get a token at: https://huggingface.co/settings/tokens\n",
                file=sys.stderr,
            )
    return _token


async def _call(system_prompt: str, code: str) -> tuple[str, str]:
    """Low-level call; returns (status, content)."""
    token = _get_token()
    if not token:
        return "error", (
            "HF_API_TOKEN is not set. Add it to your .env file and restart the server."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": code},
        ],
        "max_tokens": MAX_TOKENS,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(ENDPOINT, json=payload, headers=headers)

        if response.status_code == 402:
            return "error", (
                "HuggingFace credits exhausted. "
                "Purchase credits at https://huggingface.co/settings/billing "
                "or switch to a new token."
            )
        if response.status_code == 403:
            return "error", (
                "HuggingFace token lacks 'Inference API' permission. "
                "Go to https://huggingface.co/settings/tokens → edit token → "
                "enable 'Make calls to the serverless Inference API'."
            )
        if response.status_code == 401:
            return "error", (
                "HuggingFace token is invalid or expired. "
                "Generate a new token at https://huggingface.co/settings/tokens."
            )
        if not response.is_success:
            return "error", f"HuggingFace API error {response.status_code}: {response.text[:300]}"

        data = response.json()
        content = data["choices"][0]["message"]["content"] or ""
        return "done", content.strip()

    except httpx.ConnectError as exc:
        return "error", f"Cannot reach HuggingFace API: {exc}"
    except Exception as exc:
        return "error", str(exc)


# ---------------------------------------------------------------------------
# Four public analysis functions
# ---------------------------------------------------------------------------

async def get_explanation(code: str, language: str, ast_block: str) -> tuple[str, str]:
    system_prompt = (
        f"You are a code analysis assistant. Given the following {language} code, "
        "write a plain-language explanation of what it does, its main components, "
        "and its purpose. Be concise and structured. Do not output code. "
        f"{ast_block}"
    ).strip()
    return await _call(system_prompt, code)


async def get_diagram(code: str, language: str, ast_block: str) -> tuple[str, str]:
    system_prompt = (
        f"You are a software architecture assistant. Given the following {language} code, "
        "produce ONLY a valid Mermaid.js diagram (graph TD syntax) showing the architecture "
        "or flow. Output only the raw Mermaid syntax with no explanation, no markdown fences, "
        f"and no extra text. {ast_block}"
    ).strip()
    return await _call(system_prompt, code)


async def get_api_docs(code: str, language: str, ast_block: str) -> tuple[str, str]:
    system_prompt = (
        f"You are a technical documentation assistant. Given the following {language} code, "
        "generate API documentation in Markdown format. Include all public functions, classes, "
        "and endpoints. Use standard Markdown headers and code blocks. Output only the "
        f"Markdown. {ast_block}"
    ).strip()
    return await _call(system_prompt, code)


async def get_refactor(code: str, language: str, ast_block: str) -> tuple[str, str]:
    system_prompt = (
        f"You are a code review assistant. Given the following {language} code, first list all "
        "bugs, security vulnerabilities, and performance issues you find (use a Markdown list "
        "under a '## Issues Found' heading). Then provide a fully corrected and improved "
        "version of the code under a '## Corrected Code' heading. Output only Markdown. "
        f"{ast_block}"
    ).strip()
    return await _call(system_prompt, code)


async def get_optimise(code: str, language: str, ast_block: str) -> tuple[str, str]:
    system_prompt = (
        f"You are an algorithm optimisation expert. Analyse the following {language} code "
        "strictly for time and space complexity improvements. "
        "Produce a Markdown report with EXACTLY these four sections and no others:\n\n"
        "## Current Complexity\n"
        "A table with columns: Metric | Before | Notes — showing the current Time and Space "
        "Big-O of the original code.\n\n"
        "## Optimised Approach\n"
        "Name the better algorithm or data structure to use, and in 2–4 bullet points explain "
        "WHY it reduces time or space (e.g. replacing an O(n²) nested loop with a hash-map "
        "lookup for O(n)).\n\n"
        "## Optimised Code\n"
        "The fully rewritten code in a fenced code block. Keep the same language, same function "
        "signatures, and same observable behaviour — only change the algorithm internals.\n\n"
        "## Complexity After\n"
        "A table with columns: Metric | After | Improvement — comparing the new Big-O to the "
        "original and stating the gain (e.g. O(n²) → O(n)).\n\n"
        "Output only the Markdown. Do not include explanations outside the four sections. "
        f"{ast_block}"
    ).strip()
    return await _call(system_prompt, code)


async def get_complexity(code: str, language: str, ast_block: str) -> tuple[str, str]:
    system_prompt = (
        f"You are an algorithm complexity expert. Analyse the following {language} code and "
        "produce a Markdown report with exactly these sections:\n"
        "## Overall Complexity\n"
        "State the overall Time complexity and Space complexity in Big-O notation as a short table.\n"
        "## Per-Function Breakdown\n"
        "For each function or method, give its Time and Space complexity in a Markdown table with "
        "columns: Function | Time | Space | Notes.\n"
        "## Explanation\n"
        "In plain English, explain WHY the complexities are what they are — identify the loops, "
        "recursion, data structures, and algorithmic patterns that drive the complexity. "
        "Output only the Markdown report, no extra commentary. "
        f"{ast_block}"
    ).strip()
    return await _call(system_prompt, code)
