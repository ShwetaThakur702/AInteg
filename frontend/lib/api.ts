// lib/api.ts
// Typed fetch wrappers for the FastAPI backend

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function runPipeline(input: File | string): Promise<{ job_id: string }> {
  const form = new FormData()
  if (typeof input === "string") {
    form.append("url", input)
  } else {
    form.append("file", input)
  }

  const res = await fetch(`${API_BASE}/api/run-pipeline`, {
    method: "POST",
    body: form,
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Pipeline start failed: ${text}`)
  }

  return res.json()
}

export function createStatusEventSource(jobId: string): EventSource {
  return new EventSource(`${API_BASE}/api/pipeline-status/${jobId}`)
}

export function getDownloadUrl(jobId: string, filename: string): string {
  return `${API_BASE}/api/results/${jobId}/${filename}`
}

export async function checkHealth(): Promise<{ status: string; mock_mode: boolean }> {
  const res = await fetch(`${API_BASE}/api/health`)
  return res.json()
}
