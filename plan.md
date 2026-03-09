# Agent 1: API Integration Agent — End-to-End Plan

**Deadline:** March 15, 2026 (Phase 1 core) · Post-deadline (Phase 2 chat)
**Status:** All 4 chains wired. Migrating to Next.js + FastAPI.
**Stack:** Python · FastAPI · LangChain · Azure OpenAI (gpt-4o-mini) · Next.js 14 · TypeScript · Tailwind · httpx · Pydantic v2 · pytest · MCP (Phase 2)

> **Streamlit is fully removed.** The frontend is Next.js from the start.
> FastAPI replaces `app.py` as the backend server.
> The pipeline logic in `agent.py` and `schemas.py` is **unchanged**.

---

## Full Project Structure

```
AGENT/
├── backend/
│   ├── main.py                              # FastAPI app — replaces app.py
│   ├── .env                                 # Azure OpenAI credentials (unchanged)
│   ├── test_llm_init.py                     # LLM smoke test (unchanged)
│   └── agents/
│       └── api_integration_agent/
│           ├── __init__.py
│           ├── agent.py                     # 4-chain pipeline (UNCHANGED)
│           ├── schemas.py                   # Pydantic models (UNCHANGED)
│           └── mock_data.py                 # MOCK_MODE outputs (UNCHANGED)
│
└── frontend/
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.ts
    ├── app/
    │   ├── layout.tsx                       # Root layout, fonts, global styles
    │   ├── page.tsx                         # Step 1: Upload / URL input
    │   ├── pipeline/
    │   │   └── page.tsx                     # Step 2: Live chain progress
    │   └── results/
    │       └── page.tsx                     # Step 3: Downloads + debug chat
    ├── components/
    │   ├── SpecUploader.tsx                 # File drop zone + URL input toggle
    │   ├── PipelineProgress.tsx             # SSE-driven live chain status
    │   ├── ResultsPanel.tsx                 # Download cards + endpoint map
    │   ├── EndpointMap.tsx                  # Clickable endpoint list
    │   ├── DebugChat.tsx                    # Phase 2: chat panel
    │   ├── ChatMessage.tsx                  # Message with code blocks
    │   └── CodeBlock.tsx                    # Syntax highlight + copy button
    ├── lib/
    │   ├── api.ts                           # Typed fetch wrappers for FastAPI
    │   ├── memory.ts                        # Phase 2: in-memory session store
    │   └── mcp_client.ts                    # Phase 2: MCP tool call wrapper
    └── types/
        └── pipeline.ts                      # Shared TypeScript types
```

**Run commands:**
```bash
# Backend (from backend/)
uvicorn main:app --reload --port 8000

# Frontend (from frontend/)
npm run dev        # http://localhost:3000
```

---

## Architecture Overview

### Request Flow

```
[Next.js Frontend :3000]
        │
        │  POST /api/run-pipeline        multipart: file or url string
        │  GET  /api/pipeline-status/{job_id}   SSE stream
        │  GET  /api/results/{job_id}/{filename} download
        │
        ▼
[FastAPI Backend :8000 — main.py]
        │
        ▼
[agent.py — 4-chain LangChain pipeline — background task]
        │
        ▼
[Azure OpenAI — gpt-4o-mini]
        │
        ▼
[output/{job_id}/ — 3 generated .py files on disk]
```

The frontend **never calls Azure OpenAI directly**. All LLM orchestration stays in Python.

---

### Backend: FastAPI Routes (`main.py`)

```python
from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid, json, asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"]
)

# In-memory job store — fine for single-user demo scope
job_store: dict[str, dict] = {}

# --- Route 1: Accept spec, kick off pipeline as background task ---
@app.post("/api/run-pipeline")
async def run_pipeline(
    background_tasks: BackgroundTasks,
    file: UploadFile | None = None,
    url: str | None = None
) -> dict:
    job_id = str(uuid.uuid4())
    job_store[job_id] = {
        "status": "queued", "stage": None,
        "progress": 0, "error": None,
        "spec_summary": None, "output_files": []
    }
    background_tasks.add_task(execute_pipeline, job_id, file, url)
    return {"job_id": job_id}

# --- Route 2: SSE stream — frontend polls this for live chain progress ---
@app.get("/api/pipeline-status/{job_id}")
async def pipeline_status(job_id: str):
    async def event_stream():
        while True:
            job = job_store.get(job_id, {})
            yield f"data: {json.dumps(job)}\n\n"
            if job.get("status") in ("complete", "error"):
                break
            yield ": ping\n\n"            # keep-alive — prevents browser timeout
            await asyncio.sleep(0.5)
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# --- Route 3: Download a generated file ---
@app.get("/api/results/{job_id}/{filename}")
async def get_result(job_id: str, filename: str):
    path = OUTPUT_DIR / job_id / filename
    return FileResponse(path, filename=filename)
```

### Pipeline Execution (`execute_pipeline`)

```python
async def execute_pipeline(job_id: str, file: UploadFile | None, url: str | None):
    def update(stage: str, progress: int):
        job_store[job_id].update({"stage": stage, "progress": progress, "status": "running"})

    try:
        # Load spec
        if file:
            raw = await file.read()
            spec = yaml.safe_load(raw) if file.filename.endswith(".yaml") else json.loads(raw)
        elif url:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10, follow_redirects=True)
                resp.raise_for_status()
                ct = resp.headers.get("content-type", "")
                spec = yaml.safe_load(resp.text) if "yaml" in ct else resp.json()
        else:
            raise ValueError("No input provided")

        if not isinstance(spec, dict) or "paths" not in spec:
            raise ValueError("Invalid OpenAPI spec — missing 'paths'")

        update("chain_1", 10)
        spec_analysis = run_chain_1(spec)
        job_store[job_id]["spec_summary"] = spec_analysis.model_dump()  # stored for Phase 2 memory

        update("chain_2", 30)
        client_stubs = run_chain_2(spec_analysis)

        update("chain_3", 55)
        usage_examples = run_chain_3(spec_analysis, client_stubs)

        update("chain_4", 75)
        contract_tests = run_chain_4(spec_analysis, client_stubs)

        update("validation", 90)
        validate_outputs(job_id, client_stubs, usage_examples, contract_tests)

        job_store[job_id].update({
            "status": "complete", "progress": 100,
            "output_files": ["client_stubs.py", "usage_examples.py", "contract_tests.py"]
        })

    except Exception as e:
        job_store[job_id].update({"status": "error", "error": str(e)})
```

---

### Pipeline: 4-Chain Sequence (agent.py — Unchanged)

```
[OpenAPI Spec]
        │
        ▼
┌──────────────────┐
│   Chain 1        │  with_structured_output(SpecAnalysis, method="json_mode")
│   Spec Analysis  │  Truncated: max 50 paths / 80,000 chars
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Chain 2        │  llm.invoke() + fence stripping + retry ×3
│   client_stubs   │  httpx-based Python client
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Chain 3        │  llm.invoke() + retry ×3
│   usage_examples │  usage_examples.py
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Chain 4        │  llm.invoke() + retry ×3
│   contract_tests │  pytest + Pydantic
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Validation     │  ast.parse() + pytest --collect-only
│                  │  Retry loop on failure
└────────┬─────────┘
         ▼
[3 .py files → output/{job_id}/]
```

---

## Frontend: Page by Page

### Page 1 — `/` (Spec Input)

User uploads a file or pastes a URL. On submit, calls `POST /api/run-pipeline`, receives `job_id`, navigates to `/pipeline?job=<job_id>`.

```typescript
// lib/api.ts
export async function runPipeline(input: File | string): Promise<{ job_id: string }> {
  const form = new FormData()
  if (typeof input === "string") form.append("url", input)
  else form.append("file", input)
  const res = await fetch("http://localhost:8000/api/run-pipeline", {
    method: "POST", body: form
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
```

**`SpecUploader.tsx` behaviour:**
- Drag-and-drop zone accepts `.json` / `.yaml` only
- Toggle button switches between "Upload file" and "Paste URL" modes
- URL input validates on blur before enabling submit
- File type badge shown on successful drop

---

### Page 2 — `/pipeline` (Live Progress)

Opens SSE connection to `/api/pipeline-status/{job_id}`. Each event updates the chain status display. On `status: complete`, navigates to `/results?job=<job_id>`.

```
┌─────────────────────────────────────────┐
│  Analysing your API spec...             │
│                                         │
│  ✓  Chain 1: Spec Analysis    done      │
│  ⟳  Chain 2: Client Stubs     running   │
│  ○  Chain 3: Usage Examples   pending   │
│  ○  Chain 4: Contract Tests   pending   │
│  ○  Validation                pending   │
│                                         │
│  ████████████░░░░░░░░  40%              │
└─────────────────────────────────────────┘
```

```typescript
// components/PipelineProgress.tsx
useEffect(() => {
  const es = new EventSource(`http://localhost:8000/api/pipeline-status/${jobId}`)
  es.onmessage = (e) => {
    const data: JobState = JSON.parse(e.data)
    setJobState(data)
    if (data.status === "complete") { es.close(); router.push(`/results?job=${jobId}`) }
    if (data.status === "error")    { es.close(); setError(data.error) }
  }
  return () => es.close()
}, [jobId])
```

**Stage → progress mapping:**
| Stage | Progress |
|---|---|
| `chain_1` | 10% |
| `chain_2` | 30% |
| `chain_3` | 55% |
| `chain_4` | 75% |
| `validation` | 90% |
| `complete` | 100% |

---

### Page 3 — `/results` (Downloads + Debug Chat)

```
┌────────────────────────────────────────────────────────────────────┐
│  API Integration Agent                          session: abc123    │
├──────────────────────────┬─────────────────────────────────────────┤
│                          │                                         │
│  RESULTS                 │  DEBUG CHAT                             │
│                          │                                         │
│  ✓ client_stubs.py       │  ┌─────────────────────────────────┐   │
│    [↓ Download]          │  │ 🤖 Files generated!              │   │
│                          │  │    Need help integrating?        │   │
│  ✓ usage_examples.py     │  │                                  │   │
│    [↓ Download]          │  │  [Yes, debug with me]  [No]      │   │
│                          │  └─────────────────────────────────┘   │
│  ✓ contract_tests.py     │                                         │
│    [↓ Download]          │  (chat expands on Yes)                 │
│                          │                                         │
│  ── Endpoints ──         │                                         │
│  POST   /users      →    │                                         │
│  GET    /users/{id} →    │                                         │
│  DELETE /users/{id} →    │                                         │
│  ...                     │                                         │
│                          │                                         │
└──────────────────────────┴─────────────────────────────────────────┘
```

Clicking an endpoint in the left panel pre-fills chat input:
`"I'm getting an error on POST /users"`

---

## UI Design System

**Aesthetic: Terminal-meets-IDE. Dark, dense, precise. Feels like a dev tool.**

### Colours
```css
:root {
  --bg-base:       #0d1117;   /* GitHub dark */
  --bg-surface:    #161b22;   /* Cards, panels */
  --bg-elevated:   #21262d;   /* Inputs, hover states */
  --border:        #30363d;   /* Dividers */
  --accent-blue:   #58a6ff;   /* Active states, links, progress fill */
  --accent-green:  #3fb950;   /* Success, ✓ */
  --accent-red:    #f85149;   /* Errors */
  --accent-orange: #d29922;   /* In-progress / running */
  --text-primary:  #e6edf3;
  --text-muted:    #7d8590;
  --text-code:     #79c0ff;
}
```

### Typography
```typescript
// app/layout.tsx
import { IBM_Plex_Sans, JetBrains_Mono } from 'next/font/google'
// IBM Plex Sans — prose, labels, buttons
// JetBrains Mono — code blocks, monospace UI elements, endpoint paths
```

### Component Patterns

**Chain status row:**
- Idle: `○` grey · Running: `⟳` spinning orange · Done: `✓` green · Error: `✗` red

**Download card:**
```
┌──────────────────────────────────┐
│ 📄 client_stubs.py               │
│    httpx client · 12 endpoints   │
│                        [↓ .py]   │
└──────────────────────────────────┘
```
Border turns green on hover. Downloads via `GET /api/results/{job_id}/{filename}`.

**HTTP method badge:** `POST` orange · `GET` blue · `DELETE` red · `PATCH` yellow — monospace font, fixed width.

**Code blocks (chat responses):**
- `react-syntax-highlighter` with `github-dark` theme
- Language label top-left, "Copy" button top-right (turns "Copied ✓" for 2s)
- Background `#161b22`, border `#30363d`

---

## Schema Design (Python — Unchanged)

```python
# schemas.py
class EndpointSummary(BaseModel):
    method: str
    path: str
    summary: str
    path_params: list[str]
    query_params: list[str]
    request_body: bool
    response_200_schema: dict | None

class SpecAnalysis(BaseModel):
    base_url: str
    auth_type: str          # "bearer" | "api_key" | "basic" | "none"
    auth_location: str      # "header" | "query" | "none"
    endpoints: list[EndpointSummary]
    pagination_style: str   # "cursor" | "offset" | "none"
    common_errors: list[str]

@dataclass
class PipelineResult:
    client_stubs: str
    usage_examples: str
    contract_tests: str
    job_id: str

@dataclass
class JobStatus:
    stage: str
    progress: int
    error: str | None
```

**Rule:** Never mix `@dataclass` and `BaseModel` on the same class.

---

## TypeScript Types (Frontend)

```typescript
// types/pipeline.ts
export type ChainStage = "chain_1" | "chain_2" | "chain_3" | "chain_4" | "validation"
export type JobStatus  = "queued" | "running" | "complete" | "error"

export interface JobState {
  status: JobStatus
  stage: ChainStage | null
  progress: number
  error: string | null
  spec_summary: SpecAnalysis | null
  output_files: string[]
}

export interface EndpointSummary {
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE"
  path: string
  summary: string
  path_params: string[]
  query_params: string[]
  request_body: boolean
}

export interface SpecAnalysis {
  base_url: string
  auth_type: "bearer" | "api_key" | "basic" | "none"
  auth_location: "header" | "query" | "none"
  endpoints: EndpointSummary[]
  pagination_style: "cursor" | "offset" | "none"
  common_errors: string[]
}
```

---

## Chain Implementation (Python — Unchanged)

```python
# Chain 1 — structured output
chain_1 = llm.with_structured_output(SpecAnalysis, method="json_mode")

def truncate_spec(spec: dict, max_paths=50, max_chars=80_000) -> dict:
    paths = dict(list(spec.get("paths", {}).items())[:max_paths])
    truncated = {**spec, "paths": paths}
    raw = json.dumps(truncated)
    return json.loads(raw[:max_chars]) if len(raw) > max_chars else truncated

# Chains 2, 3, 4 — free-form code generation
def invoke_with_retry(llm, prompt: str, context: str = "", max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            result = llm.invoke(prompt + context)
            code = strip_markdown_fences(result.content)
            ast.parse(code)
            return code
        except SyntaxError as e:
            context = f"\n\n# Attempt {attempt+1} failed: {e}\n# Fix the above."
    raise ValueError("Failed after 3 attempts")

def strip_markdown_fences(text: str) -> str:
    return re.sub(r"^```(?:python)?\n?|```$", "", text.strip(), flags=re.MULTILINE).strip()

# Validation
def validate_outputs(job_id: str, stubs: str, examples: str, tests: str):
    out = OUTPUT_DIR / job_id
    out.mkdir(parents=True, exist_ok=True)
    for name, code in [("client_stubs.py", stubs), ("usage_examples.py", examples), ("contract_tests.py", tests)]:
        ast.parse(code)
        (out / name).write_text(code)
    result = subprocess.run(["python", "-m", "pytest", "--collect-only", str(out / "contract_tests.py")],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"contract_tests.py failed collection:\n{result.stdout}")
```

---

## Azure OpenAI Configuration (Unchanged)

```python
from azure.identity import ClientSecretCredential
from pydantic import SecretStr
from langchain_openai import AzureChatOpenAI

credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)
token = credential.get_token("https://cognitiveservices.azure.com/.default")

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=SecretStr(token.token),
    api_version="2024-08-01-preview",   # required for json_schema response format
    azure_deployment="gpt-4o-mini",
    temperature=0.1
)
```

---

## Remaining Work — Phase 1 (by March 15)

### March 9–12 — Core Migration

| Task | Notes |
|---|---|
| Write `main.py` with 3 FastAPI routes | Replaces `app.py` |
| Wire pipeline background task with `job_store` updates | Enables SSE stream |
| Add SSE keep-alive ping (`": ping\n\n"` every 15s) | Prevents browser timeout on long runs |
| Init Next.js project in `frontend/` | TypeScript, Tailwind, `next/font` |
| Build `SpecUploader.tsx` | File drop + URL toggle |
| Build `PipelineProgress.tsx` | SSE consumer, animated chain steps |
| Build `ResultsPanel.tsx` + `EndpointMap.tsx` | Downloads + endpoint list |
| Add CORS middleware to FastAPI | `allow_origins=["http://localhost:3000"]` |

### March 13–14 — Testing

- [ ] Petstore spec end-to-end — all 3 files download and parse cleanly
- [ ] Large spec (>100 endpoints) — verify truncation kicks in
- [ ] Swagger 2.0 spec — verify Chain 1 handles it
- [ ] URL input with raw GitHub JSON URL
- [ ] SSE stream updates UI at every chain transition
- [ ] All 3 files pass `ast.parse()`
- [ ] `contract_tests.py` passes `pytest --collect-only`
- [ ] Edge: spec with 0 endpoints
- [ ] Edge: spec with no auth defined
- [ ] Edge: unreachable URL (timeout, non-200)
- [ ] CORS — Next.js → FastAPI with no errors
- [ ] End-to-end demo run

### March 15 — Buffer
- Final polish, edge case fixes, mentor demo

---

---

# Phase 2: Interactive Debug Chatbot (Post March 15)

## What This Is

After the 3 files are delivered, the user sees:

> **"Need help integrating this API? I can debug errors with you."**

They click Yes. A chat panel opens. They paste their error. The LLM — orchestrated by MCP — diagnoses the problem using the already-computed spec context from `memory.ts`. No re-uploading. No re-running the pipeline.

---

## Why MCP (Not a Plain Chat Loop)

A naive chat loop would re-send the entire spec + 3 generated files on every message. For a 50-endpoint API that's ~2,000 lines of context per turn — expensive and context-window risky.

MCP acts as a **surgical context broker**. The LLM calls named tools to fetch exactly what it needs for this specific error:

```
User pastes: "Getting 401 on POST /users"
        │
        │  LLM decides: I need auth config + the stub for this endpoint
        │
        ├── Tool: get_auth_config()
        │   → { auth_type: "bearer", auth_location: "header" }
        │
        └── Tool: get_code_snippet("POST", "/users", "stub")
            → "async def create_user(self, body: dict) -> httpx.Response: ..."
        │
        ▼
  Diagnosis: "Bearer token missing from Authorization header.
              Fix: headers={'Authorization': f'Bearer {token}'}"
```

---

## Memory Design (`memory.ts`)

Built once when pipeline completes. Stores the `SpecAnalysis` (already computed) and a **snippet index** (key lines per endpoint). Never stores the 3 full files — too large for per-turn context.

```typescript
// lib/memory.ts

interface SessionMemory {
  sessionId: string

  // Chain 1 output — already computed, lightweight JSON
  specSummary: SpecAnalysis

  // Snippet index: key = "METHOD /path", value = 3–8 line excerpts from each file
  // Built by extracting the relevant function/test per endpoint from generated files
  codeSnippets: Record<string, {
    stub:    string    // ~3–5 lines from client_stubs.py
    example: string    // ~2–3 lines from usage_examples.py
    test:    string    // ~5–8 lines from contract_tests.py
  }>

  chatHistory: Array<{ role: "user" | "assistant"; content: string }>
}

export function buildMemory(jobState: JobState, generatedFiles: GeneratedFiles): SessionMemory {
  return {
    sessionId: jobState.job_id,
    specSummary: jobState.spec_summary!,
    codeSnippets: indexSnippets(jobState.spec_summary!.endpoints, generatedFiles),
    chatHistory: []
  }
}
```

**Why no database:** Sessions are ephemeral — one browser session, one integration task. If cross-session persistence becomes a requirement later, this key structure maps directly to Redis with no changes to tool handlers.

---

## MCP Tool Definitions

```typescript
// lib/mcp_client.ts — 5 tools, all read-only, all return small objects

[
  {
    name: "get_endpoint_info",
    description: "Get spec details for a specific API endpoint",
    handler: ({ method, path }) =>
      memory.specSummary.endpoints.find(e => e.method === method && e.path === path)
  },
  {
    name: "get_auth_config",
    description: "Get authentication type and location for this API",
    handler: () => ({
      auth_type:     memory.specSummary.auth_type,
      auth_location: memory.specSummary.auth_location
    })
  },
  {
    name: "get_code_snippet",
    description: "Get generated stub / example / test for a specific endpoint",
    handler: ({ method, path, type }) =>
      memory.codeSnippets[`${method} ${path}`]?.[type] ?? null
  },
  {
    name: "get_common_errors",
    description: "Get documented error codes from the spec",
    handler: () => memory.specSummary.common_errors
  },
  {
    name: "get_chat_history",
    description: "Get recent conversation turns for context",
    handler: ({ last_n }) => memory.chatHistory.slice(-last_n)
  }
]
```

---

## Chat API Route

```typescript
// app/api/chat/route.ts

export async function POST(req: Request) {
  const { message, sessionId } = await req.json()
  const memory = getSession(sessionId)
  memory.chatHistory.push({ role: "user", content: message })

  // Calls Azure OpenAI with MCP tools — LLM decides which to invoke
  const stream = await callLLMWithMCPStream(message, memory, MCP_TOOLS, CHAT_SYSTEM_PROMPT)

  memory.chatHistory.push({ role: "assistant", content: await collectStream(stream) })

  return new StreamingTextResponse(stream)    // streams tokens to frontend
}
```

## System Prompt

```
You are an API integration debugger. The user generated integration code for a
3rd-party API using an automated pipeline and is now hitting errors.

Tools available:
- get_endpoint_info(method, path)          spec details for that endpoint
- get_auth_config()                        auth type and location
- get_code_snippet(method, path, type)     stub / example / test snippet
- get_common_errors()                      documented error codes
- get_chat_history(last_n)                 recent conversation

Rules:
1. Always call get_endpoint_info first when an endpoint is mentioned.
2. For any 4xx error, call get_auth_config before diagnosing.
3. Always include a corrected code snippet in your response.
4. Name the exact line to change — not just the concept.
5. Keep responses under 200 words. One root cause. One fix.
6. Never tell the user to re-upload files or re-run the pipeline.
```

---

## Conversation Flow

```
Pipeline complete → files downloadable
        │
        ▼
  Slim banner: "Still stuck? Debug with AI →"
        │ User clicks
        ▼
  Chat panel slides in (right side, no page navigation)
  "Paste your error and tell me which endpoint."
        │ User pastes error
        ▼
  MCP orchestration — tool calls run, LLM synthesises
        │
        ▼
  Streaming response:
    root cause (1–2 sentences)
    fixed code block (syntax highlighted, copy button)
    what to verify next
        │
        ▼
  Quick-reply chips:
    "Still getting the error" · "Different endpoint" · "What's 429 here?"
        │
        ▼
  Continues — chatHistory carried in memory across turns
```

---

## Phase 2 Key UX Moments

1. **Pipeline → chat transition** — slim bar at bottom of results: *"Still stuck? Debug with AI →"*. Non-intrusive, always visible. Clicks open chat panel without navigating away.

2. **Error paste** — textarea auto-expands. On submit, the raw error displays in a styled block (red left-border, monospace font) before the LLM response renders below it.

3. **Streaming response** — tokens stream in as they arrive. Code blocks render as they complete.

4. **Tool call trace** (dev mode toggle) — grey text under each response: `[fetched: get_auth_config · get_code_snippet POST /users]`. Shows the LLM is reasoning from spec data, not guessing.

5. **Endpoint shortcuts** — clicking any endpoint in the left panel pre-fills chat: `"I'm hitting an error on POST /users"`.

6. **Quick-reply chips** — 2–3 contextual suggestions after each response to keep the conversation moving without blank-box friction.

---

## Phase 2 Build Order

1. Set up MCP server — 5 tools, wired to `memory.ts`
2. Build `app/api/chat/route.ts` — streaming, MCP tool dispatch
3. Build `DebugChat.tsx` — message list, streaming text, code blocks
4. Build `ChatMessage.tsx` — left-border accent bars, syntax highlight, copy button
5. Wire `buildMemory()` call on pipeline completion (triggered from `/results` page load)
6. Wire "Yes" → chat panel slide-in (CSS transition, no navigation)
7. Add tool call trace (dev mode toggle in header)
8. Add quick-reply chips after each assistant message
9. Polish — typing indicator during MCP tool calls, keep-alive handling

---

## Common Failure Modes & Fixes

| Failure | Cause | Fix |
|---|---|---|
| `OpenAIContextOverflowError` | Spec too large | Truncate to 50 paths / 80,000 chars |
| `ItemNotFound` / double-import | Stale `__pycache__` | Delete `__pycache__`, use full module paths |
| Markdown fences in LLM output | Model wraps code in ` ```python ` | Strip with regex before `ast.parse()` |
| Chain 1 wrong schema | `json_mode` without field hints in prompt | Include all field names in system prompt |
| Contract tests fail collection | Missing `import pytest` in generated file | Add explicit instruction to Chain 4 prompt |
| URL fetch fails | Redirect or wrong content-type | `follow_redirects=True`, detect YAML by both content-type and file extension |
| SSE drops on long pipeline | Browser 30s timeout | Keep-alive ping: `yield ": ping\n\n"` every 15s |
| CORS error | FastAPI missing CORS config | `CORSMiddleware(allow_origins=["http://localhost:3000"])` |
| Chat context grows too large | chatHistory unbounded | Slice to last 10 turns before each LLM call |

---

## Import Hygiene (Python)

```python
# ALWAYS full module paths
from agents.api_integration_agent.schemas import SpecAnalysis, EndpointSummary
from agents.api_integration_agent.mock_data import MOCK_SPEC_ANALYSIS

# NEVER relative imports — breaks under uvicorn module loading
# from .schemas import SpecAnalysis  ← don't do this
```

Clear `__pycache__` on `ItemNotFound` or type mismatch:
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
```
/