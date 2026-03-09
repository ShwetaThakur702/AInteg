# API Integration Agent — What's Left

**Current date:** 2026-03-09
**Phase 1 deadline:** March 15, 2026

---

## Phase 1 — Core Pipeline (Due March 15)

### Already Done

| Area | What's Built |
|---|---|
| Backend | `main.py` — FastAPI with 4 routes (run-pipeline, pipeline-status SSE, results download, health) |
| Backend | `agent.py` — 4-chain LangChain pipeline (spec analysis → stubs → examples → tests) |
| Backend | `schemas.py` — Pydantic models: `SpecAnalysis`, `EndpointSummary`, `PipelineResult`, `JobStatus` |
| Backend | `mock_data.py` — Petstore mock for MOCK_MODE |
| Backend | `.env` — OpenRouter credentials (gpt-4o-mini via OpenAI-compatible endpoint) |
| Backend | `requirements.txt` |
| Backend | Output folders named `YYYY-MM-DD_HH-MM-SS` (datetime format) |
| Frontend | `layout.tsx` — light mode, IBM Plex Sans + JetBrains Mono fonts, white header |
| Frontend | `page.tsx` — home page with SpecUploader card and output file previews |
| Frontend | `pipeline/page.tsx` — SSE-driven live chain progress |
| Frontend | `results/page.tsx` — loads final job state, shows ResultsPanel |
| Frontend | `SpecUploader.tsx` — file upload, URL input, and paste-spec modes |
| Frontend | `PipelineProgress.tsx` — animated chain status rows, progress bar |
| Frontend | `ResultsPanel.tsx` — download cards, API summary, endpoint map, debug chat trigger |
| Frontend | `EndpointMap.tsx` — clickable endpoint list with HTTP method badges |
| Frontend | `FilePreviewModal.tsx` — preview generated .py files with syntax highlighting (👁 button) |
| Frontend | `DebugChat.tsx` — chat panel scaffold (Phase 2 placeholder response) |
| Frontend | `ChatMessage.tsx` — message bubbles with markdown + code blocks |
| Frontend | `CodeBlock.tsx` — syntax highlighting (oneLight theme) + copy button |
| Frontend | `lib/api.ts` — `runPipeline`, `createStatusEventSource`, `getDownloadUrl`, `checkHealth` |
| Frontend | `lib/memory.ts` — `SessionMemory` type + `buildMemory`, `getSession`, `clearSession` |
| Frontend | `lib/mcp_client.ts` — 5 MCP tool definitions (not yet wired to API route) |
| Frontend | `types/pipeline.ts` — `JobState`, `SpecAnalysis`, `EndpointSummary` TypeScript types |
| CLI | `test_pipeline.py` — submit spec, poll SSE, download 3 files from terminal |

---

### Still To Do — Phase 1

#### Testing Checklist (March 13–14)

- [ ] Petstore spec end-to-end — all 3 files download and parse cleanly
- [ ] Large spec (>100 endpoints) — verify 50-path truncation kicks in correctly
- [ ] Swagger 2.0 spec — verify Chain 1 handles older format
- [ ] URL input with raw GitHub JSON URL
- [ ] Pasted spec (textarea mode) — submit and confirm pipeline runs
- [ ] SSE stream shows correct stage at each chain transition in browser
- [ ] All 3 generated files pass `ast.parse()`
- [ ] `contract_tests.py` passes `pytest --collect-only`
- [ ] Edge: spec with 0 endpoints — does not crash, returns empty output
- [ ] Edge: spec with no auth defined — auth_type set to "none"
- [ ] Edge: unreachable URL — timeout error surfaces cleanly in UI
- [ ] Edge: invalid JSON/YAML uploaded — error shown before pipeline starts
- [ ] CORS — Next.js :3000 → FastAPI :8000 with no preflight errors
- [ ] File preview modal (👁) — loads and renders syntax-highlighted content
- [ ] End-to-end demo run with a real production spec

#### Minor Gaps

- [ ] Old UUID-named output folders in `output/` — clean up: `rm -rf output/*/` (keep only datetime folders)
- [ ] `next.config.js` exists but may need `rewrites` if deploying frontend + backend to same origin
- [ ] No `.gitignore` at project root — `.env`, `output/`, `.venv/`, `node_modules/` should be excluded
- [ ] No `README.md` run instructions for new contributors (exists but may be outdated)

---

## Phase 2 — Interactive Debug Chat (Post March 15)

### What's Scaffolded (Code Exists, Not Wired)

| File | Status |
|---|---|
| `frontend/components/DebugChat.tsx` | UI built — sends placeholder response, not real MCP |
| `frontend/lib/memory.ts` | `buildMemory()` written — not called from results page yet |
| `frontend/lib/mcp_client.ts` | 5 tool definitions written — not connected to any API route |

### What Still Needs to Be Built

#### 1. Next.js Chat API Route
**File:** `frontend/app/api/chat/route.ts`
Receives `{ message, sessionId }`, calls OpenRouter with MCP tools, streams tokens back to client.

```typescript
// POST /api/chat
// - load SessionMemory by sessionId
// - build messages array with system prompt
// - call LLM with tool_choice + tools array
// - dispatch tool calls to mcp_client.callTool()
// - stream final response using ReadableStream
```

#### 2. Wire buildMemory() on Pipeline Completion
**File:** `frontend/app/results/page.tsx` (line ~38, inside `status === "complete"` branch)
After pipeline completes and files are fetched, call `buildMemory(jobState, generatedFiles)` so the session is ready for chat.

```typescript
// After fetching all 3 file contents:
buildMemory({ ...jobState, job_id: jobId }, {
  client_stubs: stubsText,
  usage_examples: examplesText,
  contract_tests: testsText,
})
```

#### 3. Wire DebugChat to Real API
**File:** `frontend/components/DebugChat.tsx` (line ~50, inside `handleSend`)
Replace the `setTimeout` placeholder with a real streaming fetch to `/api/chat`.

```typescript
const response = await fetch("/api/chat", {
  method: "POST",
  body: JSON.stringify({ message: text, sessionId: jobId }),
  headers: { "Content-Type": "application/json" },
})
// Stream response tokens into assistant message
```

#### 4. Streaming Token Rendering
`ChatMessage.tsx` currently renders full content. Add incremental token append so response streams character-by-character as it arrives from the LLM.

#### 5. Quick-Reply Chips
After each assistant message, show 2–3 contextual chips:
- "Still getting the error"
- "Different endpoint"
- "What does this status code mean?"

Clicking a chip pre-fills and sends the input.

#### 6. Tool Call Trace (Dev Mode)
Grey text under each assistant message showing which MCP tools were called:
`[fetched: get_auth_config · get_code_snippet POST /users]`
Toggle with a header button.

#### 7. Typing Indicator During MCP Tool Calls
Show `⟳ thinking...` while tool calls are in-flight, before tokens start streaming.

---

## Phase 2 Build Order

1. `app/api/chat/route.ts` — streaming LLM + MCP tool dispatch
2. Wire `buildMemory()` in results page on completion
3. Replace placeholder in `DebugChat.tsx` with real streaming fetch
4. Add streaming token rendering to `ChatMessage.tsx`
5. Add quick-reply chips after each assistant message
6. Add tool call trace toggle (dev mode)
7. Polish typing indicator + keep-alive handling

---

## Known Issues / Tech Debt

| Issue | Where | Fix |
|---|---|---|
| In-memory `job_store` resets on backend restart | `main.py` | Acceptable for demo; use Redis for production |
| `max_tokens=16000` in Chain 1 | `agent.py` | Works for gpt-4o-mini; may need adjustment for other models |
| `MOCK_MODE = False` hardcoded | `agent.py` | Add env var `MOCK_MODE=true` override for testing without API key |
| `chatHistory` unbounded growth | `memory.ts` | Slice to last 10 turns before each LLM call in chat route |
| Old UUID output folders | `output/` | Run `rm -rf output/[0-9a-f]*-*/` to clean up |
| No input validation on spec "paths" key | `main.py` | Currently validated by `parse_spec`; could be stricter |

---

## Run Commands (Quick Reference)

```bash
# Backend
cd backend
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm run dev   # http://localhost:3000

# CLI test
python3 test_pipeline.py https://petstore3.swagger.io/api/v3/openapi.json
python3 test_pipeline.py path/to/spec.yaml

# Kill stuck backend port
lsof -ti:8000 | xargs kill -9
```
