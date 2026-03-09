// lib/memory.ts
// Phase 2: In-memory session store for the debug chat
// Built when pipeline completes — holds SpecAnalysis + code snippets

import type { JobState, SpecAnalysis, EndpointSummary } from "@/types/pipeline"

export interface GeneratedFiles {
  client_stubs: string
  usage_examples: string
  contract_tests: string
}

export interface CodeSnippets {
  stub: string
  example: string
  test: string
}

export interface SessionMemory {
  sessionId: string
  specSummary: SpecAnalysis
  codeSnippets: Record<string, CodeSnippets>
  chatHistory: Array<{ role: "user" | "assistant"; content: string }>
}

const sessions: Map<string, SessionMemory> = new Map()

function extractSnippet(code: string, keyword: string, lines = 8): string {
  const codeLines = code.split("\n")
  const idx = codeLines.findIndex((l) => l.includes(keyword))
  if (idx === -1) return ""
  return codeLines.slice(idx, idx + lines).join("\n")
}

function indexSnippets(
  endpoints: EndpointSummary[],
  files: GeneratedFiles
): Record<string, CodeSnippets> {
  const index: Record<string, CodeSnippets> = {}
  for (const ep of endpoints) {
    const key = `${ep.method.toUpperCase()} ${ep.path}`
    index[key] = {
      stub: extractSnippet(files.client_stubs, ep.operation_id),
      example: extractSnippet(files.usage_examples, ep.operation_id),
      test: extractSnippet(files.contract_tests, ep.operation_id),
    }
  }
  return index
}

export function buildMemory(jobState: JobState & { job_id: string }, files: GeneratedFiles): SessionMemory {
  const memory: SessionMemory = {
    sessionId: jobState.job_id,
    specSummary: jobState.spec_summary!,
    codeSnippets: indexSnippets(jobState.spec_summary!.endpoints, files),
    chatHistory: [],
  }
  sessions.set(jobState.job_id, memory)
  return memory
}

export function getSession(sessionId: string): SessionMemory | undefined {
  return sessions.get(sessionId)
}

export function clearSession(sessionId: string): void {
  sessions.delete(sessionId)
}
