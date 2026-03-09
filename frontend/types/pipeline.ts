// types/pipeline.ts
// Aligned to backend schemas.py — source of truth is Python

export type ChainStage = "chain_1" | "chain_2" | "chain_3" | "chain_4" | "validation"
export type JobStatus = "queued" | "running" | "complete" | "error"

export interface EndpointSummary {
  path: string
  method: string
  operation_id: string
  summary: string
  path_params: string[]
  query_params: string[]
  request_body_schema: Record<string, unknown>
  response_200_schema: Record<string, unknown>
}

export interface SpecAnalysis {
  base_url: string
  auth_type: "bearer" | "api_key" | "basic" | "oauth2" | "none" | "other"
  auth_location: "header" | "query" | "cookie" | null
  pagination_style: "cursor" | "offset" | "page" | "none" | "unknown"
  endpoints: EndpointSummary[]
  common_error_codes: number[]
}

export interface JobState {
  status: JobStatus
  stage: ChainStage | null
  progress: number
  error: string | null
  spec_summary: SpecAnalysis | null
  output_files: string[]
}
