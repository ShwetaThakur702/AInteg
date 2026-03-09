"""
agent.py
========
API Integration Agent — Pipeline Orchestrator

MOCK_MODE = True  → returns hardcoded data, no LLM calls
MOCK_MODE = False → calls real gpt-4o-mini
"""

import ast
import json
import subprocess
import tempfile
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from pydantic import SecretStr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openapi_spec_validator import validate

from agents.api_integration_agent.schemas import SpecAnalysis, PipelineResult
from agents.api_integration_agent.mock_data import (
    MOCK_RAW_SPEC, MOCK_SPEC_ANALYSIS, MOCK_CLIENT_STUBS,
    MOCK_USAGE_EXAMPLES, MOCK_CONTRACT_TESTS,
)

# Loads backend/.env regardless of where the script is run from
load_dotenv(Path(__file__).parent.parent.parent / ".env")

MOCK_MODE = False  # Using OpenRouter — real LLM calls enabled
MAX_RETRIES = 3


# ── LLM Initialization ───────────────────────────────────────

def get_llm() -> ChatOpenAI:
    # OpenRouter uses the standard OpenAI API format — no Azure identity needed.
    # AZURE_OPENAI_ENDPOINT = https://openrouter.ai/api/v1
    # AZURE_CLIENT_SECRET   = sk-or-v1-...
    # AZURE_OPENAI_DEPLOYMENT = openai/gpt-4o-mini
    return ChatOpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        api_key=SecretStr(os.environ["AZURE_CLIENT_SECRET"]),
        temperature=0.2,
    )


def test_llm_connection(llm: ChatOpenAI) -> bool:

    try:
        message = llm.invoke("Reply with exactly one word: ready")
        response = str(message.content)
        is_ready = len(response.strip()) > 0
        if is_ready:
            print(f"[llm] Connection verified. Response: '{response.strip()}'")
        return is_ready
    except Exception as e:
        print(f"[llm] Connection failed: {e}")
        return False


# ── Step 1: Parse raw spec bytes ─────────────────────────────

def parse_spec(raw_bytes: bytes) -> dict:
    """
    Input  : raw bytes of uploaded YAML or JSON file
    Output : Python dict of the full spec

    Tries JSON first, falls back to YAML.
    Validates against the OpenAPI/Swagger JSON Schema (auto-detects version).
    """
    if MOCK_MODE:
        print("[parse_spec] MOCK: returning Petstore spec dict")
        return MOCK_RAW_SPEC

    # ── Parse ────────────────────────────────────────
    try:
        spec = json.loads(raw_bytes)
        print("[parse_spec] Parsed as JSON")
    except json.JSONDecodeError:
        try:
            spec = yaml.safe_load(raw_bytes)
            print("[parse_spec] Parsed as YAML")
        except yaml.YAMLError as e:
            raise ValueError(f"Could not parse spec as JSON or YAML: {e}")

    if not isinstance(spec, dict):
        raise ValueError("Spec must be a JSON/YAML object at the root level")

    if "paths" not in spec:
        raise ValueError("Invalid spec: missing 'paths' key")

    # ── Validate against OpenAPI/Swagger schema ──────
    try:
        validate(spec)
    except Exception as e:
        raise ValueError(f"OpenAPI schema validation failed: {e}")

    print(f"[parse_spec] Validated successfully: {len(spec.get('paths', {}))} paths found")
    return spec


# ── Truncation Strategy ──────────────────────────────────────

def truncate_spec_for_llm(spec: dict, max_paths: int = 50, max_chars: int = 40000) -> str:
    """
    Produce a minimal spec string for LLM consumption.

    Strategy:
    1. Keep metadata (info, servers, auth) — always small
    2. Flatten deeply nested schemas to max 2 levels
    3. Cap number of paths
    4. Hard char limit as final safety net
    """

    def flatten_schema(obj, depth=0, max_depth=2):
        """Recursively truncate nested schemas beyond max_depth."""
        if not isinstance(obj, dict):
            return obj
        if depth >= max_depth:
            return {"type": "object", "_truncated": True}

        result = {}
        for key, value in obj.items():
            if isinstance(value, dict):
                result[key] = flatten_schema(value, depth + 1, max_depth)
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    result[key] = [flatten_schema(value[0], depth + 1, max_depth)]
                else:
                    result[key] = value[:3]
            else:
                result[key] = value
        return result

    # ── Build trimmed spec ───────────────────────────
    paths = spec.get("paths", {})
    components = spec.get("components", {})
    definitions = spec.get("definitions", {})  # Swagger 2.0

    # Cap paths
    if len(paths) > max_paths:
        paths = dict(list(paths.items())[:max_paths])
        print(f"[truncate] Capped paths: {len(spec['paths'])} → {max_paths}")

    # Flatten schemas in components/definitions
    flat_components = flatten_schema(components, depth=0, max_depth=3)
    flat_definitions = flatten_schema(definitions, depth=0, max_depth=3)

    # Flatten inline schemas in paths too
    flat_paths = flatten_schema(paths, depth=0, max_depth=4)

    trimmed = {
        "openapi": spec.get("openapi", ""),
        "swagger": spec.get("swagger", ""),
        "info": spec.get("info", {}),
        "servers": spec.get("servers", []),
        "host": spec.get("host", ""),
        "basePath": spec.get("basePath", ""),
        "schemes": spec.get("schemes", []),
        "securityDefinitions": flatten_schema(
            spec.get("securityDefinitions", {}), max_depth=2
        ),
        "components": flat_components,
        "definitions": flat_definitions,
        "paths": flat_paths,
    }

    # Remove empty keys to save tokens
    trimmed = {k: v for k, v in trimmed.items() if v}

    spec_str = json.dumps(trimmed, separators=(",", ":"))  # compact JSON

    # ── Hard char limit as safety net ────────────────
    if len(spec_str) > max_chars:
        trimmed.pop("components", None)
        trimmed.pop("definitions", None)
        spec_str = json.dumps(trimmed, separators=(",", ":"))
        print("[truncate] Dropped components/definitions to fit limit")

    if len(spec_str) > max_chars:
        path_items = list(flat_paths.items())
        while len(spec_str) > max_chars and path_items:
            path_items = path_items[:len(path_items) // 2]
            trimmed["paths"] = dict(path_items)
            spec_str = json.dumps(trimmed, separators=(",", ":"))
        print(f"[truncate] Reduced to {len(path_items)} paths to fit char limit")

    print(f"[truncate] Final spec size: {len(spec_str)} chars")
    return spec_str


# ── Step 2: Chain 1 — Analyse spec ──────────────────────────

def chain_1_analyse_spec(spec: dict, llm: ChatOpenAI | None = None) -> SpecAnalysis:

    if MOCK_MODE:
        print("[chain_1] MOCK: returning hardcoded SpecAnalysis")
        return MOCK_SPEC_ANALYSIS

    if llm is None:
        raise ValueError("[chain_1] LLM instance required when MOCK_MODE = False")

    spec_str = truncate_spec_for_llm(spec)

    structured_llm = llm.with_structured_output(SpecAnalysis, method="json_mode").bind(max_tokens=16000)

    prompt = f"""
You are an API analyst. Analyse the following OpenAPI spec and extract structured information.

You MUST populate every field for every endpoint. Do not skip any fields.

For each endpoint, extract:
- path: the URL path e.g. "/pets/{{petId}}"
- method: HTTP method in lowercase e.g. "get", "post"
- operation_id: the operationId value from the spec
- summary: the summary string, or empty string "" if missing
- path_params: list of path parameter names e.g. ["petId"], or [] if none
- query_params: list of query parameter names e.g. ["limit"], or [] if none
- request_body_schema: the JSON schema object of the request body, or {{}} if none
- response_200_schema: the JSON schema object of the 200 response, or {{}} if none

For the top-level fields:
- base_url: first entry in servers[]. If missing, infer from host + basePath.
- auth_type: one of "bearer", "api_key", "basic", "oauth2", "none", or "other". Map the spec's security scheme to the closest match. Use "other" if it doesn't fit standard types. Use "none" if no auth defined.
- auth_location: "header", "query", or "cookie". None if auth_type is "none".
- pagination_style: look for cursor/page/offset query params. Use "unknown" if unclear.
- common_error_codes: list of HTTP error codes appearing across multiple endpoints.

Note: Some schemas may be truncated. Generate the best analysis you can from the available structure.

OpenAPI Spec:
{spec_str}
"""

    print("[chain_1] Calling LLM for spec analysis...")
    result = structured_llm.invoke(prompt)
    analysis = SpecAnalysis.model_validate(
        result if isinstance(result, dict) else result.model_dump()
    )
    print(f"[chain_1] Analysis complete: {len(analysis.endpoints)} endpoints found")
    return analysis


# ── Step 3: Chain 2 — Generate client stubs ──────────────────

def chain_2_generate_stubs(
    spec: dict,
    analysis: SpecAnalysis,
    llm: ChatOpenAI | None = None,
    error_context: str = ""
) -> str:
    if MOCK_MODE:
        print("[chain_2] MOCK: returning hardcoded client stubs")
        return MOCK_CLIENT_STUBS

    if llm is None:
        raise ValueError("[chain_2] LLM instance required when MOCK_MODE = False")

    auth_patterns = {
        "bearer": 'headers={"Authorization": "Bearer <token>"}',
        "api_key": 'headers={"X-API-Key": "<token>"}',
        "basic": "auth=(<username>, <password>)",
        "oauth2": 'headers={"Authorization": "Bearer <oauth_token>"}',
        "other": 'headers={"Authorization": "<credentials>"}',
        "none": "no auth needed",
    }
    auth_pattern = auth_patterns.get(analysis.auth_type, "no auth needed")
    error_section = f"\nPrevious attempt failed — fix this error:\n{error_context}" if error_context else ""

    endpoint_list = "\n".join([
        f"- {e.method.upper()} {e.path} → function: {e.operation_id}()"
        f" path_params={e.path_params} query_params={e.query_params}"
        for e in analysis.endpoints
    ])

    prompt = f"""
You are a Python developer. Generate a complete Python file called client_stubs.py.

Requirements:
- Use httpx for all HTTP calls
- Base URL: {analysis.base_url}
- Auth type: {analysis.auth_type}, location: {analysis.auth_location}
- Auth pattern: {auth_pattern}
- Generate one function per endpoint listed below
- Use the operation_id as the exact Python function name
- Handle path params by formatting them into the URL
- Handle query params as optional keyword arguments defaulting to None
- Each function calls response.raise_for_status() before returning response.json()
- Include a get_client(token: str) function that returns an authenticated httpx.Client
- Add a docstring to every function
- Return ONLY the Python code, no markdown, no backticks, no explanation

Endpoints to generate:
{endpoint_list}
{error_section}
"""

    print("[chain_2] Calling LLM to generate client stubs...")
    response = llm.bind(max_tokens=8192).invoke(prompt)
    code = str(response.content).strip()

    if code.startswith("```"):
        lines = code.split("\n")
        code = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    return code

# ── Step 4: Chain 3 — Generate usage examples ────────────────

def chain_3_generate_examples(
    spec: dict,
    analysis: SpecAnalysis,
    stubs_code: str,
    llm: ChatOpenAI | None = None,
    error_context: str = ""
) -> str:
    if MOCK_MODE:
        print("[chain_3] MOCK: returning hardcoded usage examples")
        return MOCK_USAGE_EXAMPLES

    if llm is None:
        raise ValueError("[chain_3] LLM instance required when MOCK_MODE = False")

    error_section = f"\nPrevious attempt failed — fix this error:\n{error_context}" if error_context else ""

    prompt = f"""
You are a Python developer. Generate a complete Python file called usage_examples.py.

Requirements:
- Import and use functions from client_stubs.py
- The client stubs code is provided below — use the EXACT function names from it
- Show one example call per endpoint
- Use realistic sample data for request bodies
- Show how to instantiate the client with get_client(token)
- Include error handling for common HTTP errors (404, 401)
- Return ONLY the Python code, no markdown, no backticks, no explanation

Client stubs code:
{stubs_code}
{error_section}
"""

    print("[chain_3] Calling LLM to generate usage examples...")
    response = llm.bind(max_tokens=8192).invoke(prompt)
    code = str(response.content).strip()

    if code.startswith("```"):
        lines = code.split("\n")
        code = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    return code


# ── Step 5: Chain 4 — Generate contract tests ────────────────

def chain_4_generate_tests(
    spec: dict,
    analysis: SpecAnalysis,
    stubs_code: str,
    llm: ChatOpenAI | None = None,
    error_context: str = ""
) -> str:
    if MOCK_MODE:
        print("[chain_4] MOCK: returning hardcoded contract tests")
        return MOCK_CONTRACT_TESTS

    if llm is None:
        raise ValueError("[chain_4] LLM instance required when MOCK_MODE = False")

    error_section = f"\nPrevious attempt failed — fix this error:\n{error_context}" if error_context else ""

    endpoint_list = "\n".join([
        f"- {e.method.upper()} {e.path} → {e.operation_id}() "
        f"response schema: {e.response_200_schema}"
        for e in analysis.endpoints
    ])

    prompt = f"""
You are a Python developer. Generate a complete Python file called contract_tests.py.

Requirements:
- Use pytest for all tests
- Use httpx for HTTP calls
- Use Pydantic BaseModel to validate response schemas
- Generate one test per endpoint to check status code
- Generate one test per endpoint to validate response shape using Pydantic
- Use a pytest fixture called 'client' that returns an authenticated httpx.Client
- Base URL: {analysis.base_url}
- Auth type: {analysis.auth_type}
- These are PDCT tests — they verify the spec contract, not business logic
- Return ONLY the Python code, no markdown, no backticks, no explanation

Endpoints and their response schemas:
{endpoint_list}
{error_section}
"""

    print("[chain_4] Calling LLM to generate contract tests...")
    response = llm.bind(max_tokens=8192).invoke(prompt)
    code = str(response.content).strip()

    if code.startswith("```"):
        lines = code.split("\n")
        code = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    return code


# ── Step 6: Validate generated code ─────────────────────────

def validate_code(code: str, filename: str) -> tuple[bool, str]:

    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, f"SyntaxError in {filename}: {e}"

    if filename == "contract_tests.py":
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q", tmp_path],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode != 0:
                return False, f"pytest collection failed for {filename}:\n{result.stderr or result.stdout}"
        finally:
            os.unlink(tmp_path)

    return True, ""


# ── Step 7: Retry wrapper ────────────────────────────────────

def generate_with_retry(generate_fn, filename: str, max_retries: int = MAX_RETRIES, **kwargs) -> str:

    last_error = ""

    for attempt in range(1, max_retries + 1):
        print(f"[{generate_fn.__name__}] Attempt {attempt}/{max_retries}")

        code = generate_fn(error_context=last_error, **kwargs)
        valid, error = validate_code(code, filename=filename)

        if valid:
            print(f"[{generate_fn.__name__}] Validation passed on attempt {attempt}")
            return code

        print(f"[{generate_fn.__name__}] Validation failed: {error}")
        last_error = error

    raise RuntimeError(
        f"{generate_fn.__name__} failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    )


# ── Main pipeline entry point ────────────────────────────────

def run_pipeline(raw_bytes: bytes, llm: ChatOpenAI | None = None) -> PipelineResult:

    print("=" * 50)
    print("Pipeline started")

    spec = parse_spec(raw_bytes)
    print(f"Spec parsed: {len(spec.get('paths', {}))} endpoints found")

    analysis = chain_1_analyse_spec(spec, llm=llm)
    print(f"Analysis complete: {len(analysis.endpoints)} endpoints, auth={analysis.auth_type}")

    stubs = generate_with_retry(
        chain_2_generate_stubs,
        filename="client_stubs.py",
        spec=spec,
        analysis=analysis,
        llm=llm
    )

    examples = generate_with_retry(
        chain_3_generate_examples,
        filename="usage_examples.py",
        spec=spec,
        analysis=analysis,
        stubs_code=stubs,
        llm=llm
    )

    tests = generate_with_retry(
        chain_4_generate_tests,
        filename="contract_tests.py",
        spec=spec,
        analysis=analysis,
        stubs_code=stubs,
        llm=llm
    )

    print("Pipeline complete")
    print("=" * 50)

    return PipelineResult(
        client_stubs=stubs,
        usage_examples=examples,
        contract_tests=tests
    )


# ── Save results to disk ─────────────────────────────────────

def save_results(result: PipelineResult, output_dir: str | None = None) -> str:
    """
    Input  : PipelineResult + optional output directory path
    Output : path to the output directory

    Creates AGENT/output/<timestamp>/ if no path provided.
    """
    if output_dir is None:
        agent_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(agent_root, "output", timestamp)

    os.makedirs(output_dir, exist_ok=True)

    files = {
        "client_stubs.py":   result.client_stubs,
        "usage_examples.py": result.usage_examples,
        "contract_tests.py": result.contract_tests,
    }

    for filename, content in files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[save_results] Written: {filepath}")

    return output_dir


# ── Entry point ──────────────────────────────────────────────

if __name__ == "__main__":
    print("Initializing LLM...")
    llm = get_llm()

    if not test_llm_connection(llm):
        print("ERROR: LLM connection failed. Check backend/.env credentials.")
        exit(1)

    result = run_pipeline(b"mock input", llm=llm)
    output_path = save_results(result)
    print(f"\nFiles saved to: {output_path}")