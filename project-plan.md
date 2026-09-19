# ai_code_intelligence — Project Plan

## Top-Level Overview

Build a web tool where a user submits code (via paste, single file upload, or
zip upload) and receives four structured outputs:

1. **Plain-language explanation** — what the code does
2. **Architecture diagram** — rendered as Mermaid.js syntax
3. **API documentation** — rendered as Markdown
4. **Refactor report** — bugs, security issues, and performance problems
   identified in the code, plus a corrected/improved version of the code

**Stack:**
- Frontend: React (Vite)
- Backend: Python + FastAPI — LLM orchestration is I/O-bound and Python's
  `asyncio` + `httpx` make concurrent LLM calls trivial; rich ecosystem for
  text/zip processing and the built-in `ast` module covers Python static analysis
- LLM: IBM Granite via the Hugging Face Inference API
  (`ibm-granite/granite-3.1-8b-instruct`) using the `huggingface_hub` Python SDK
- Token guard: hard limit with graceful truncation and a skipped-files list
  in the response
- AST pre-pass: for Python inputs, the built-in `ast` module extracts a
  structured code summary (classes, functions, imports) that is injected into
  every LLM prompt to improve output quality; non-Python inputs skip this step

**Key decisions:**
- 4 LLM calls run **concurrently** (one per output type) using `asyncio.gather`
- Frontend makes **one blocking POST**, receives one complete JSON response
- The JSON response shape is designed so a future SSE upgrade only requires
  streaming the same fields incrementally
- Multi-file input: files are concatenated with path headers; files beyond the
  token limit are skipped and listed in the response
- AST summary is generated synchronously before the LLM calls and passed into
  every prompt; it adds no latency because it runs before `asyncio.gather`

---

## System Architecture

```
User Browser (React)
  │
  │  POST /api/analyze  (multipart or JSON)
  ▼
FastAPI Backend
  ├── Input handler (paste / file / zip extraction)
  ├── Token guard (truncate + track skipped files)
  ├── AST parser (Python only — extracts classes, functions, imports)
  └── LLM Orchestrator — asyncio.gather
        ├── Call A → Granite → plain-language explanation
        ├── Call B → Granite → Mermaid.js diagram syntax
        ├── Call C → Granite → API documentation (Markdown)
        └── Call D → Granite → refactor report + corrected code
  │
  │  JSON response
  ▼
React Frontend
  ├── Explanation panel (plain text)
  ├── Diagram panel (Mermaid.js renderer)
  ├── API Docs panel (Markdown renderer)
  └── Refactor panel (diff / annotated code view)
```

---

## API Contract

### `POST /api/analyze`

**Request** — `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `input_type` | string | yes | `"paste"` \| `"file"` \| `"zip"` |
| `code` | string | if paste | Raw pasted code |
| `file` | binary | if file/zip | Uploaded file or zip archive |
| `language` | string | no | Hint e.g. `"python"`. Auto-detected if omitted |

**Response — 200 OK** — `application/json`

```jsonc
{
  "status": "success",               // "success" | "partial"
  "language_detected": "python",
  "files_analyzed": ["main.py", "utils.py"],
  "files_skipped": [],               // files omitted due to token limit
  "ast_summary": {                   // present for Python only; null otherwise
    "classes": ["MyClass"],
    "functions": ["helper", "main"],
    "imports": ["os", "sys"]
  },
  "outputs": {
    "explanation": {
      "status": "done",              // "done" | "error"
      "content": "This codebase..."  // plain text string
    },
    "diagram": {
      "status": "done",
      "content": "graph TD\n  A --> B\n..."  // raw Mermaid syntax string
    },
    "api_docs": {
      "status": "done",
      "content": "## Endpoints\n\n### GET /users\n..."  // Markdown string
    },
    "refactor": {
      "status": "done",
      "content": "## Issues Found\n\n### Bug: ...\n\n## Corrected Code\n\n```python\n..."
      // Markdown string: issues list followed by corrected code block
    }
  },
  "error": null                      // top-level error message if status != success
}
```

**Notes for future SSE upgrade:** Each `outputs.*` object maps directly to an
SSE event type (`explanation`, `diagram`, `api_docs`, `refactor`). The shape
does not need to change — only the transport layer.

**Error response — 4xx/5xx**

```jsonc
{
  "status": "error",
  "error": "Zip file exceeds maximum allowed size of 10 MB"
}
```

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffolding and Repo Setup

**Intent:** Get both the frontend and backend running locally with a single
hello-world end-to-end call so all team members can start working in parallel
immediately.

**Expected Outcomes:**
- React (Vite) dev server runs at `localhost:5173`
- FastAPI server runs at `localhost:8000` with CORS enabled for the frontend
- `POST /api/analyze` returns a hardcoded stub JSON matching the full response
  shape above (all four outputs present)
- A `.env.example` documents the `HF_API_TOKEN` variable
- `requirements.txt` lists `fastapi uvicorn python-multipart httpx
  huggingface_hub python-dotenv`
- `README.md` documents how to run both servers locally

**Todo List:**
1. Initialise a monorepo with two folders: `frontend/` and `backend/`
2. Scaffold frontend with `npm create vite@latest frontend -- --template react`
3. Scaffold backend: create `backend/main.py` with FastAPI, `backend/requirements.txt`
   with `fastapi uvicorn python-multipart httpx huggingface_hub python-dotenv`
4. Add CORS middleware to FastAPI allowing `http://localhost:5173`
5. Implement `POST /api/analyze` stub that ignores input and returns the full
   hardcoded response shape (all four outputs)
6. Add `.env.example` with `HF_API_TOKEN=`
7. Write `README.md` with setup steps for both servers

**Relevant Context:**
- Full response shape (including `ast_summary` and `refactor` output) is
  defined in the API Contract section above
- CORS must allow both `http://localhost:5173` (dev) and the production origin

**Status:** [ ] pending

---

### Sub-Task 2 — Input Handling and Token Guard (Backend)

**Intent:** Accept all three input types, extract code content into a single
annotated string, and enforce a token limit with graceful truncation so the
LLM orchestrator always receives a safe, well-formed payload.

**Expected Outcomes:**
- `POST /api/analyze` correctly parses `paste`, `file`, and `zip` inputs
- For zip uploads, all text files are extracted and concatenated with
  `# --- FILE: <path> ---` headers
- Files beyond the token limit are excluded; their paths appear in
  `files_skipped` in the response
- Language is auto-detected from file extensions when not provided
- Input larger than 10 MB (raw) is rejected with a `413` error before any
  extraction

**Todo List:**
1. Create `backend/input_handler.py` with a function
   `extract_code(input_type, code, file) -> (str, list[str], list[str], str)`
   returning `(concatenated_code, files_analyzed, files_skipped, language)`
2. For `"paste"`: treat the whole string as one anonymous file
3. For `"file"`: read the uploaded file, wrap with a single path header
4. For `"zip"`: use Python's `zipfile` module to iterate entries; skip
   binaries (extension allowlist: `.py .js .ts .java .go .rb .cs .cpp
   .c .h .html .css .json .yaml .md`); concatenate with headers
5. Implement token guard: use a simple character count approximation
   (`len(text) / 4` ≈ tokens); set a hard cap of 80,000 tokens (≈ 320,000
   chars); when exceeded, stop adding files and record the remainder in
   `files_skipped`; append a notice at the end of the code string:
   `# [TRUNCATED: N files skipped due to token limit]`
6. Auto-detect language: count file extensions in the analyzed file list,
   return the most common one's language name; fall back to `"unknown"`
7. Wire `extract_code` into the `/api/analyze` route

**Relevant Context:**
- Token cap of 80,000 keeps the combined system prompt + code + response well
  within Granite's context window
- Binary file detection should be extension-based only (no magic-byte check
  needed for hackathon scope)

**Status:** [ ] pending

---

### Sub-Task 3 — Python AST Pre-Pass (Backend)

**Intent:** For Python inputs, extract a structured summary of the code using
the built-in `ast` module before any LLM calls are made. Inject this summary
into every LLM prompt to give the model richer context and improve output
quality without extra latency. Non-Python inputs skip this step entirely.

**Expected Outcomes:**
- For Python code, a structured `ast_summary` dict is produced containing:
  - `classes`: list of class names defined at module level
  - `functions`: list of top-level function names
  - `imports`: list of imported module names
- The summary is included as a formatted block in every LLM prompt (see
  prompts in Sub-Task 4)
- The summary is also returned in the API response as the `ast_summary` field
- For non-Python inputs, `ast_summary` is `null` and prompts are unchanged
- AST parse errors (e.g. syntax errors in the submitted code) are caught
  gracefully; on failure the summary is `null` and analysis continues without it

**Todo List:**
1. Create `backend/ast_parser.py` with a function
   `parse_python_ast(code: str) -> dict | None`
   - Use `ast.parse(code)` to build the AST
   - Walk the tree to collect `ast.ClassDef` names, `ast.FunctionDef` /
     `ast.AsyncFunctionDef` names, and `ast.Import` / `ast.ImportFrom` module
     names
   - Return `{"classes": [...], "functions": [...], "imports": [...]}` on
     success
   - Return `None` on any `SyntaxError` or unexpected exception
2. Call `parse_python_ast` in the `/api/analyze` route after `extract_code`,
   when `language == "python"`; store the result as `ast_summary`
3. Format the summary as an injectable string helper
   `format_ast_summary(ast_summary: dict | None) -> str` that returns a
   fenced block like:
   ```
   Code structure summary (from static analysis):
   - Classes: MyClass, OtherClass
   - Functions: helper, main
   - Imports: os, sys
   ```
   Returns an empty string when `ast_summary` is `None`
4. Pass `ast_summary` (the raw dict) and the formatted string into the
   orchestrator so prompts can include it

**Relevant Context:**
- The `ast` module is part of the Python standard library — no extra dependency
- Only top-level classes and functions need to be captured (no need to recurse
  into nested definitions for MVP)
- The formatted string is injected between the system prompt and the code block
  in every LLM call (see Sub-Task 4 prompts)

**Status:** [ ] pending

---

### Sub-Task 4 — LLM Orchestration (Backend)

**Intent:** Send the prepared code string (and optional AST summary) to IBM
Granite via the Hugging Face Inference API in four concurrent async calls —
one per output type — and assemble the results into the final response JSON.

**Expected Outcomes:**
- Four LLM calls run concurrently via `asyncio.gather`
- Each call uses a focused system prompt tuned for its output type, with the
  AST summary block injected when available
- If one call fails, its `outputs.<type>.status` is set to `"error"` and the
  other outputs are still returned (partial success)
- The top-level `status` is `"partial"` if any output errored, `"success"`
  if all four succeeded
- LLM responses are returned as raw strings (no post-processing needed for MVP)

**Todo List:**
1. Create `backend/llm_client.py` with four async functions:
   - `get_explanation(code, language, ast_block) -> (status, content)`
   - `get_diagram(code, language, ast_block) -> (status, content)`
   - `get_api_docs(code, language, ast_block) -> (status, content)`
   - `get_refactor(code, language, ast_block) -> (status, content)`
2. Each function calls the Hugging Face Inference API using
   `huggingface_hub.AsyncInferenceClient` with model
   `ibm-granite/granite-3.1-8b-instruct`; load `HF_API_TOKEN` from environment
3. Wrap each call in `try/except`; return `("done", text)` on success or
   `("error", error_message)` on failure
4. Create `backend/orchestrator.py` with
   `async def analyze(code, language, ast_summary) -> dict` that calls
   `asyncio.gather` over all four LLM functions and assembles the response dict
5. Create `backend/prompts.py` with the four prompt constants (see below)
6. Wire `orchestrator.analyze` into the `/api/analyze` route, passing
   `ast_summary` through; replace the stub response

**Prompts (in `backend/prompts.py`):**

- **Explanation prompt:**
  > "You are a code analysis assistant. Given the following {language} code,
  > write a plain-language explanation of what it does, its main components,
  > and its purpose. Be concise and structured. Do not output code.
  > {ast_block}"

- **Diagram prompt:**
  > "You are a software architecture assistant. Given the following {language}
  > code, produce ONLY a valid Mermaid.js diagram (graph TD syntax) showing
  > the architecture or flow. Output only the raw Mermaid syntax with no
  > explanation, no markdown fences, and no extra text.
  > {ast_block}"

- **API docs prompt:**
  > "You are a technical documentation assistant. Given the following
  > {language} code, generate API documentation in Markdown format. Include
  > all public functions, classes, and endpoints. Use standard Markdown headers
  > and code blocks. Output only the Markdown.
  > {ast_block}"

- **Refactor prompt:**
  > "You are a code review assistant. Given the following {language} code,
  > first list all bugs, security vulnerabilities, and performance issues you
  > find (use a Markdown list under a '## Issues Found' heading). Then provide
  > a fully corrected and improved version of the code under a
  > '## Corrected Code' heading. Output only Markdown.
  > {ast_block}"

**Relevant Context:**
- FastAPI route handlers must be `async def` for `asyncio.gather` to work
  without blocking
- Use `huggingface_hub.AsyncInferenceClient` (v0.20+) for async support;
  call `.text_generation(prompt, max_new_tokens=1024)`
- `HF_API_TOKEN` is loaded via `python-dotenv` at app startup

**Status:** [ ] pending

---

### Sub-Task 5 — Frontend: Upload UI and API Integration

**Intent:** Build the input form that accepts all three input types and calls
the backend, showing a loading state while the request is in flight.

**Expected Outcomes:**
- User can switch between three input modes: paste, single file, zip upload
- Submit triggers `POST /api/analyze` with correct `multipart/form-data`
- A loading spinner/overlay is shown while waiting
- On error (4xx/5xx), a clear error message is displayed
- On success, raw response JSON is passed to the results components (Sub-Task 6)

**Todo List:**
1. Create `frontend/src/components/CodeInputForm.jsx` with three tabs/modes:
   Paste (textarea), File Upload (file input), Zip Upload (file input)
2. On submit, build a `FormData` object with `input_type`, and either `code`
   or `file` field
3. Call `fetch('/api/analyze', { method: 'POST', body: formData })`
4. Manage loading state with a React `useState` boolean; show a spinner overlay
5. On response, set a `result` state that triggers the results panel to render
6. On error, parse the `error` field from the JSON and display it inline
7. Configure Vite dev proxy: in `vite.config.js`, proxy `/api` →
   `http://localhost:8000` so no CORS issues during development

**Relevant Context:**
- Do not set `Content-Type` header manually when using `FormData` — the browser
  sets it with the correct boundary automatically
- The Vite proxy config avoids needing to hardcode the backend URL in fetch calls

**Status:** [ ] pending

---

### Sub-Task 6 — Frontend: Results Rendering

**Intent:** Display all four outputs in a clean, readable UI once the API
response arrives, using appropriate renderers for each output type. Include a
dedicated refactor diff panel for the new fourth output.

**Expected Outcomes:**
- Explanation panel renders plain text in a readable layout
- Diagram panel renders Mermaid.js syntax as an actual diagram
- API Docs panel renders Markdown as formatted HTML
- Refactor panel renders the Markdown report (issues list + corrected code)
  with syntax-highlighted code blocks
- Each panel shows an error state if its `outputs.<type>.status === "error"`
- Skipped files are listed in a visible warning banner if `files_skipped`
  is non-empty
- If `ast_summary` is present, a collapsible info badge shows the detected
  classes, functions, and imports

**Todo List:**
1. Install rendering dependencies:
   `npm install mermaid react-markdown react-syntax-highlighter`
2. Create `frontend/src/components/ResultsPanel.jsx` that receives the full
   response JSON as a prop and renders all four sections
3. Create `frontend/src/components/ExplanationPanel.jsx` — renders
   `outputs.explanation.content` as a styled text block
4. Create `frontend/src/components/DiagramPanel.jsx` — on mount, call
   `mermaid.render('diagram', content)` and inject the returned SVG into a
   `div`; fall back to a `<pre>` block on Mermaid parse errors
5. Create `frontend/src/components/ApiDocsPanel.jsx` — render
   `outputs.api_docs.content` using `<ReactMarkdown>`
6. Create `frontend/src/components/RefactorPanel.jsx` — render
   `outputs.refactor.content` using `<ReactMarkdown>` with
   `react-syntax-highlighter` as the code block renderer so corrected code
   is syntax-highlighted
7. Add a `SkippedFilesWarning` component that renders a yellow warning box
   listing `response.files_skipped` when the array is non-empty
8. Add an `AstSummaryBadge` component that renders a collapsible info section
   showing `ast_summary` when it is non-null
9. Wire all panels into `App.jsx`: show `CodeInputForm` when no result,
   show `ResultsPanel` when result exists, with an "Analyze another" reset button

**Relevant Context:**
- `mermaid.initialize({ startOnLoad: false })` must be called once at app init
  before calling `mermaid.render`
- `react-markdown` renders Markdown strings as React elements with no
  `dangerouslySetInnerHTML` needed
- Pass the `SyntaxHighlighter` component as the `code` renderer in
  `ReactMarkdown`'s `components` prop for the RefactorPanel

**Status:** [ ] pending

---

### Sub-Task 7 — Integration Testing and Demo Polish

**Intent:** Verify the full end-to-end flow works for all three input types and
multiple languages, fix any integration issues, and prepare the demo.

**Expected Outcomes:**
- End-to-end flow works for: Python paste, JS single file, multi-file zip
- All four output panels render correctly for each test case
- AST summary badge appears for Python inputs and is absent for JS inputs
- Token-limit truncation warning appears when a large zip is submitted
- A demo script / set of sample input files is ready for the presentation
- `README.md` is updated with any final setup steps

**Todo List:**
1. Test paste input with a Python snippet (~50 lines) — verify all 4 outputs
   and that the AST summary badge is populated
2. Test single file upload with a JS/TS file — verify language detection and
   that `ast_summary` is null (badge absent)
3. Test zip upload with a small multi-file Python project — verify all 4 outputs
4. Test zip upload with a deliberately large repo to verify truncation warning
5. Fix any prompt output issues:
   - Mermaid: if the renderer rejects the syntax, tighten the diagram prompt
   - Refactor: if the corrected code block is missing fences, add a strip/wrap
     step in the backend before returning
6. Add a `samples/` folder with 2–3 ready-made input files for the demo
7. Update `README.md` with final env setup (`HF_API_TOKEN`), run instructions,
   and a screenshot

**Relevant Context:**
- If Mermaid rendering fails for a given LLM output, `DiagramPanel` should
  fall back to showing the raw syntax in a `<pre>` block rather than crashing
- Common Mermaid failure mode: LLM wraps output in triple-backtick fences
  despite the prompt — add a simple strip step in the backend before returning
- `huggingface_hub` free-tier rate limits may cause occasional 429 errors
  during testing; the `"error"` status on individual outputs handles this
  gracefully

**Status:** [ ] pending

---

## Team Split Suggestion

| Person | Sub-Tasks | Domain |
|---|---|---|
| **Person A** | 1 (scaffolding) → 2 (input handling) → 3 (AST parsing) → 4 (LLM orchestration) | Backend |
| **Person B** | 1 (scaffolding) → 5 (upload UI) → 6 (results rendering) | Frontend |
| **Person C** | 1 (scaffolding) → prompt tuning in Sub-Task 4 → 7 (integration + demo) | Full-stack / QA |

Person A and Person B can start Sub-Tasks 2 and 5 in parallel immediately
after Sub-Task 1 is complete. Person A can begin Sub-Task 3 (AST parsing)
as soon as Sub-Task 2 is done, since it is a self-contained backend module.
Person C begins prompt tuning once the orchestrator stub is wired in Sub-Task 4.

---

## Stretch Goals (if time permits)

- **SSE streaming:** Replace the blocking POST with Server-Sent Events so each
  output panel populates as its LLM call finishes. The response shape is
  already designed for this.
- **Smart entry-point detection:** Instead of concatenating all files, detect
  `main.py`, `index.js`, `app.py` etc. and prioritise those files first before
  truncating.
- **AST for other languages:** Extend the pre-pass to JS/TS using a
  tree-sitter binding or a simple regex-based extractor.
- **User file selection:** After zip upload, show a checklist of extracted
  files and let the user deselect files before submitting to the LLM.
- **Copy/export buttons:** Let users copy Mermaid syntax, download the API
  docs as a `.md` file, or download the refactored code directly.
- **Regenerate individual outputs:** Add a "Regenerate" button per panel that
  re-runs only that one LLM call.
