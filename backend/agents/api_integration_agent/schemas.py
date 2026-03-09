from typing import Literal
from dataclasses import dataclass
from pydantic import BaseModel


# ── Pydantic models — used by Chain 1 and with_structured_output() ──

class EndpointSummary(BaseModel):
    path: str
    method: str
    operation_id: str
    summary: str = ""
    path_params: list[str] = []
    query_params: list[str] = []
    request_body_schema: dict = {}
    response_200_schema: dict = {}


class SpecAnalysis(BaseModel):
    """
    Structured output of Chain 1.
    Everything the downstream chains need to know about the API.
    No free text — all typed fields.
    """
    auth_type: Literal["bearer", "api_key", "basic", "oauth2", "none", "other"] = "none"
    auth_location: Literal["header", "query", "cookie"] | None = None
    base_url: str
    pagination_style: Literal["cursor", "offset", "page", "none", "unknown"] = "unknown"
    endpoints: list[EndpointSummary]
    common_error_codes: list[int] = []


# ── Dataclasses — internal pipeline types, never go through LLM ──

@dataclass
class PipelineResult:
    """
    Final output of run_pipeline().
    Each field is a string of verified Python code ready to be written to a file.
    """
    client_stubs: str
    usage_examples: str
    contract_tests: str


@dataclass
class JobStatus:
    """
    Tracks an async pipeline job.
    FastAPI stores one of these per uploaded spec.
    """
    job_id: str
    status: Literal["pending", "running", "complete", "failed"]
    error_message: str | None = None
    result: PipelineResult | None = None