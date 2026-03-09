# API Integration Agent

Upload an OpenAPI / Swagger spec → get a Python httpx client, usage examples, and contract tests.

**Stack:** Python · FastAPI · LangChain · Azure OpenAI · Next.js 14 · TypeScript · Tailwind

---

## Quick Start

### Backend

```bash
cd backend/

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server (runs in MOCK_MODE by default — no LLM calls)
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend/
npm install
npm run dev    # http://localhost:3000
```

---

## Configuration

### MOCK_MODE (default: on)

By default, `backend/agents/api_integration_agent/agent.py` has `MOCK_MODE = True`.
This returns hardcoded Petstore data — no Azure OpenAI calls needed.

To use the real LLM:
1. Set `MOCK_MODE = False` in `backend/agents/api_integration_agent/agent.py`
2. Fill in valid credentials in `backend/.env`

### backend/.env

```
AZURE_CLIENT_SECRET=...
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_TOKEN_SCOPE=https://cognitiveservices.azure.com/.default
```

---

## Project Structure

```
API_integration_agent/
├── backend/
│   ├── main.py                                  # FastAPI server (3 routes + health)
│   ├── .env                                     # Azure OpenAI credentials
│   ├── test_llm_init.py                         # LLM connectivity smoke test
│   ├── requirements.txt
│   └── agents/
│       └── api_integration_agent/
│           ├── __init__.py
│           ├── agent.py                         # 4-chain LangChain pipeline
│           ├── schemas.py                       # Pydantic models
│           └── mock_data.py                     # MOCK_MODE hardcoded outputs
│
├── frontend/
│   ├── package.json
│   ├── app/
│   │   ├── layout.tsx                           # Dark IDE theme, fonts
│   │   ├── page.tsx                             # Step 1: Upload / URL input
│   │   ├── pipeline/page.tsx                   # Step 2: Live SSE progress
│   │   └── results/page.tsx                    # Step 3: Downloads + debug chat
│   ├── components/
│   │   ├── SpecUploader.tsx                     # Drag-drop + URL toggle
│   │   ├── PipelineProgress.tsx                 # SSE chain status display
│   │   ├── ResultsPanel.tsx                     # Download cards + layout
│   │   ├── EndpointMap.tsx                      # Clickable endpoint list
│   │   ├── DebugChat.tsx                        # Phase 2: AI debug chat
│   │   ├── ChatMessage.tsx                      # Styled message with code blocks
│   │   └── CodeBlock.tsx                        # Syntax highlight + copy button
│   ├── lib/
│   │   ├── api.ts                               # FastAPI fetch wrappers
│   │   ├── memory.ts                            # Phase 2: session memory store
│   │   └── mcp_client.ts                        # Phase 2: MCP tool definitions
│   └── types/
│       └── pipeline.ts                          # Shared TypeScript types
│
├── output/                                      # Generated files per job_id/
├── plan.md
└── README.md
```

---

## API Routes

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/run-pipeline` | Upload spec file or pass URL → returns `job_id` |
| `GET`  | `/api/pipeline-status/{job_id}` | SSE stream of live chain progress |
| `GET`  | `/api/results/{job_id}/{filename}` | Download a generated `.py` file |
| `GET`  | `/api/health` | Health check |

---

## Pages

| URL | Description |
|---|---|
| `/` | Upload OpenAPI spec or paste URL |
| `/pipeline?job=<id>` | Live chain progress via SSE |
| `/results?job=<id>` | Download files + endpoint map + debug chat |

---

Environment variables are stored in `backend/.env`.
Azure OpenAI keys may not be valid during development — use MOCK_MODE = True.
