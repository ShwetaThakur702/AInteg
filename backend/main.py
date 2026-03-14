"""
main.py
=======
FastAPI server for the API Integration Agent.

Routes:
  POST /api/run-pipeline          — accept spec file or URL, start background job
  GET  /api/pipeline-status/{id}  — SSE stream of job progress
  GET  /api/results/{id}/{file}   — download a generated .py file
"""

import asyncio
import json
import uuid
import os
import sys
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

# Load backend/.env
load_dotenv(Path(__file__).parent / ".env")

# Add backend/ to sys.path so absolute imports work under uvicorn
sys.path.insert(0, str(Path(__file__).parent))

from agents.api_integration_agent.agent import (
    get_llm,
    parse_spec,
    chain_1_analyse_spec,
    chain_2_generate_stubs,
    chain_3_generate_examples,
    chain_4_generate_tests,
    generate_with_retry,
    MOCK_MODE,
)

# Output directory — project root / output /
OUTPUT_DIR = Path(__file__).parent.parent / "output"

app = FastAPI(title="API Integration Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# In-memory job store
job_store: dict[str, dict] = {}

# Thread pool for sync LLM calls
_executor = ThreadPoolExecutor(max_workers=4)


# ── Helpers ───────────────────────────────────────────────────

def _update(job_id: str, stage: str, progress: int) -> None:
    job_store[job_id].update({"stage": stage, "progress": progress, "status": "running"})

def _datetime_dir() -> str:
    """Return a sortable datetime string for the output folder name."""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# ── Route 1: Start pipeline ───────────────────────────────────

@app.post("/api/run-pipeline")
async def run_pipeline_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile | None = None,
    url: str | None = Form(default=None),
) -> dict:
    raw_bytes: bytes | None = None
    filename: str | None = None
    if file and file.filename:
        raw_bytes = await file.read()
        filename = file.filename

    job_id = str(uuid.uuid4())
    output_dir_name = _datetime_dir()          # e.g. 2026-03-09_14-30-25

    job_store[job_id] = {
        "status": "queued",
        "stage": None,
        "progress": 0,
        "error": None,
        "spec_summary": None,
        "output_files": [],
        "output_dir": output_dir_name,         # stored so download route can find it
    }
    background_tasks.add_task(execute_pipeline, job_id, output_dir_name, raw_bytes, filename, url)
    return {"job_id": job_id}


# ── Route 2: SSE live progress stream ────────────────────────

@app.get("/api/pipeline-status/{job_id}")
async def pipeline_status(job_id: str):
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_stream():
        ping_counter = 0
        while True:
            job = job_store.get(job_id, {})
            yield f"data: {json.dumps(job)}\n\n"
            if job.get("status") in ("complete", "error"):
                break
            ping_counter += 1
            if ping_counter % 30 == 0:
                yield ": ping\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Route 3: Download a generated file ───────────────────────

@app.get("/api/results/{job_id}/{filename}")
async def get_result(job_id: str, filename: str):
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Use the datetime-named folder stored at job creation
    out_dir_name = job.get("output_dir", job_id)
    path = OUTPUT_DIR / out_dir_name / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(path), filename=filename)


# ── Route 4: Health check ─────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "mock_mode": MOCK_MODE}


# ── Pipeline execution ────────────────────────────────────────

async def execute_pipeline(
    job_id: str,
    output_dir_name: str,
    raw_bytes: bytes | None,
    filename: str | None,
    url: str | None,
) -> None:
    loop = asyncio.get_event_loop()

    try:
        # ── Load spec ──────────────────────────────────────────
        if raw_bytes is not None:
            spec_bytes = raw_bytes
        elif url:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                spec_bytes = resp.content
        else:
            raise ValueError("No input provided — supply a file or URL")

        spec: dict = await loop.run_in_executor(_executor, parse_spec, spec_bytes)

        # ── Save input spec immediately ────────────────────────
        out_dir = OUTPUT_DIR / output_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)

        ext = "json"
        if filename and (filename.endswith(".yaml") or filename.endswith(".yml")):
            ext = "yaml"
        elif url and ("yaml" in url or "yml" in url):
            ext = "yaml"
        spec_filename = f"input_spec.{ext}"
        (out_dir / spec_filename).write_bytes(spec_bytes)
        job_store[job_id]["spec_file"] = spec_filename

        # ── Get LLM ────────────────────────────────────────────
        llm = None
        if not MOCK_MODE:
            try:
                llm = await loop.run_in_executor(_executor, get_llm)
            except Exception as e:
                print(f"[main] LLM init failed ({e}), falling back to MOCK_MODE")
                llm = None

        # ── Chain 1 — Spec Analysis ────────────────────────────
        _update(job_id, "chain_1", 10)
        spec_analysis = await loop.run_in_executor(
            _executor, chain_1_analyse_spec, spec, llm
        )
        job_store[job_id]["spec_summary"] = spec_analysis.model_dump()

        # ── Chain 2 — Client Stubs ─────────────────────────────
        _update(job_id, "chain_2", 30)
        stubs = await loop.run_in_executor(
            _executor,
            lambda: generate_with_retry(
                chain_2_generate_stubs, "client_stubs.py",
                spec=spec, analysis=spec_analysis, llm=llm,
            ),
        )

        # ── Chain 3 — Usage Examples ───────────────────────────
        _update(job_id, "chain_3", 55)
        examples = await loop.run_in_executor(
            _executor,
            lambda: generate_with_retry(
                chain_3_generate_examples, "usage_examples.py",
                spec=spec, analysis=spec_analysis, stubs_code=stubs, llm=llm,
            ),
        )

        # ── Chain 4 — Contract Tests ───────────────────────────
        _update(job_id, "chain_4", 75)
        tests = await loop.run_in_executor(
            _executor,
            lambda: generate_with_retry(
                chain_4_generate_tests, "contract_tests.py",
                spec=spec, analysis=spec_analysis, stubs_code=stubs, llm=llm,
            ),
        )

        # ── Write generated files ──────────────────────────────
        _update(job_id, "validation", 90)
        for name, code in [
            ("client_stubs.py",   stubs),
            ("usage_examples.py", examples),
            ("contract_tests.py", tests),
        ]:
            (out_dir / name).write_text(code, encoding="utf-8")

        # ── Save metadata ──────────────────────────────────────
        meta = {
            "job_id": job_id,
            "output_dir": output_dir_name,
            "created_at": datetime.datetime.now().isoformat(),
            "source": filename or url or "unknown",
            "spec_file": spec_filename,
            "base_url": spec_analysis.base_url,
            "endpoints": len(spec_analysis.endpoints),
            "auth_type": spec_analysis.auth_type,
            "output_files": ["client_stubs.py", "usage_examples.py", "contract_tests.py"],
        }
        (out_dir / "job_info.json").write_text(json.dumps(meta, indent=2))

        job_store[job_id].update({
            "status": "complete",
            "progress": 100,
            "output_files": ["client_stubs.py", "usage_examples.py", "contract_tests.py"],
        })

    except Exception as e:
        job_store[job_id].update({"status": "error", "error": str(e)})


# ── Phase 2: Debug Chat ───────────────────────────────────────

def _build_system_prompt(spec_summary: dict, stubs: str, examples: str, tests: str) -> str:
    """Build a system prompt that embeds the full API context in memory:
    - spec summary (base URL, auth, all endpoints)
    - all 3 generated files (complete content)
    - conversation history is appended by the caller
    The LLM has everything it needs without calling any tools.
    Tools are kept for structured lookups (exact schema, fuzzy endpoint search).
    """
    endpoints = spec_summary.get("endpoints", [])
    ep_lines = "\n".join(
        f"  {ep.get('method','?').upper():6} {ep.get('path','')}  — {ep.get('summary','')}"
        for ep in endpoints
    )
    common_errors = ", ".join(str(e) for e in spec_summary.get("common_error_codes", [])) or "none documented"

    # Truncate each file to fit — keep as much as possible within reason
    def _trim(code: str, max_chars: int = 8000) -> str:
        if len(code) <= max_chars:
            return code
        return code[:max_chars] + f"\n... [truncated — {len(code) - max_chars} chars omitted]"

    return f"""\
You are an API integration debugger. The user processed an OpenAPI spec through a 4-chain pipeline \
that generated three Python files. You have the FULL content of all three files below — no need to \
call tools to look up generated code. Use the code directly to diagnose and fix errors.

== API SPEC SUMMARY ==
Base URL:    {spec_summary.get("base_url", "unknown")}
Auth type:   {spec_summary.get("auth_type", "none")}
Auth location: {spec_summary.get("auth_location", "none")}
Pagination:  {spec_summary.get("pagination_style", "none")}
Endpoints ({len(endpoints)} total):
{ep_lines or "  (none)"}
Common error codes: {common_errors}
== END SPEC SUMMARY ==

== client_stubs.py (generated httpx client) ==
{_trim(stubs) if stubs else "(file not available)"}
== END client_stubs.py ==

== usage_examples.py (generated usage examples) ==
{_trim(examples) if examples else "(file not available)"}
== END usage_examples.py ==

== contract_tests.py (generated contract tests) ==
{_trim(tests) if tests else "(file not available)"}
== END contract_tests.py ==

Rules:
1. You have the full generated code above — reference exact line numbers and function names.
2. When the user pastes an error, identify the exact function/line in the code above that caused it.
3. Always show the corrected code in a ```python block with the specific fix.
4. Keep responses concise: one root cause, one fix, exact line to change.
5. Never tell the user to re-upload files or re-run the pipeline.
6. Use get_endpoint_info tool only if you need the raw OpenAPI schema for a specific endpoint.

End every response with exactly this line (2-3 short follow-up questions, max 7 words each):
SUGGESTIONS: "suggestion 1" | "suggestion 2" | "suggestion 3"\
"""


class ChatHistoryItem(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    job_id: str
    message: str
    history: list[ChatHistoryItem] = []


def _run_chat(
    message: str,
    history: list[ChatHistoryItem],
    spec_summary: dict,
    stubs: str,
    examples: str,
    tests: str,
) -> tuple[str, list[str]]:
    """Synchronous tool-calling loop. Returns (final_answer, tool_names_used)."""

    # ── Define tools as closures over spec_summary + file contents ──

    @tool
    def get_endpoint_info(method: str, path: str) -> str:
        """Get spec details for a specific API endpoint including params and response schema."""
        endpoints = spec_summary.get("endpoints", [])
        for ep in endpoints:
            if ep.get("method", "").upper() == method.upper() and ep.get("path") == path:
                return json.dumps(ep, indent=2)
        # fuzzy match on path fragment
        fuzzy = [ep for ep in endpoints if path in ep.get("path", "")]
        if fuzzy:
            return json.dumps(fuzzy[0], indent=2)
        return f"Endpoint {method} {path} not found in spec."

    # get_endpoint_info is the only tool needed — full file content is already in the system prompt.
    # It's kept for fetching the raw OpenAPI schema (request body schema, response schema)
    # which is too verbose to embed in the prompt for every endpoint.
    tools_list = [get_endpoint_info]

    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools_list)

    # System prompt embeds: spec summary + all 3 generated files + conversation history
    msgs: list = [SystemMessage(content=_build_system_prompt(spec_summary, stubs, examples, tests))]
    for h in history[-10:]:
        if h.role == "user":
            msgs.append(HumanMessage(content=h.content))
        else:
            msgs.append(AIMessage(content=h.content))
    msgs.append(HumanMessage(content=message))

    tool_names_used: list[str] = []

    # Tool-calling loop (max 4 iterations)
    for _ in range(4):
        response = llm_with_tools.invoke(msgs)
        if not response.tool_calls:
            break
        msgs.append(response)
        for tc in response.tool_calls:
            tool_names_used.append(tc["name"])
            tool_fn = next((t for t in tools_list if t.name == tc["name"]), None)
            result = tool_fn.invoke(tc["args"]) if tool_fn else "Tool not found."
            msgs.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    return response.content, tool_names_used


# ── Route 5: Chat ─────────────────────────────────────────────

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    job = job_store.get(req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    spec_summary = job.get("spec_summary")
    if not spec_summary:
        raise HTTPException(status_code=400, detail="Pipeline not complete — spec_summary not available")

    out_dir = OUTPUT_DIR / job.get("output_dir", req.job_id)

    def _read(name: str) -> str:
        p = out_dir / name
        return p.read_text(encoding="utf-8") if p.exists() else ""

    stubs    = _read("client_stubs.py")
    examples = _read("usage_examples.py")
    tests    = _read("contract_tests.py")

    loop = asyncio.get_event_loop()
    try:
        final_content, tool_names = await loop.run_in_executor(
            _executor,
            lambda: _run_chat(req.message, req.history, spec_summary, stubs, examples, tests),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Parse SUGGESTIONS line from end of response
    quick_replies: list[str] = []
    lines = final_content.strip().split("\n")
    if lines and lines[-1].startswith("SUGGESTIONS:"):
        sug_line = lines[-1][len("SUGGESTIONS:"):].strip()
        quick_replies = [s.strip().strip('"').strip("'") for s in sug_line.split("|") if s.strip()]
        final_content = "\n".join(lines[:-1]).strip()

    async def stream():
        # Tool trace first
        if tool_names:
            yield f"data: {json.dumps({'type': 'trace', 'tools': tool_names})}\n\n"

        # Stream content in small chunks to simulate typing
        chunk_size = 4
        for i in range(0, len(final_content), chunk_size):
            chunk = final_content[i:i + chunk_size]
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            await asyncio.sleep(0.015)

        yield f"data: {json.dumps({'type': 'done', 'quick_replies': quick_replies})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
