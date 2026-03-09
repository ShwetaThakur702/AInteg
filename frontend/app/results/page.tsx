"use client"

import { useSearchParams, useRouter } from "next/navigation"
import { useEffect, useState, Suspense } from "react"
import { createStatusEventSource } from "@/lib/api"
import ResultsPanel from "@/components/ResultsPanel"
import type { JobState } from "@/types/pipeline"

const EMPTY_STATE: JobState = {
  status: "queued",
  stage: null,
  progress: 0,
  error: null,
  spec_summary: null,
  output_files: [],
}

function ResultsContent() {
  const params = useSearchParams()
  const router = useRouter()
  const jobId = params.get("job")

  const [jobState, setJobState] = useState<JobState>(EMPTY_STATE)
  const [resolved, setResolved] = useState(false)

  useEffect(() => {
    if (!jobId) return

    // Poll status once to get final job state (including spec_summary + output_files)
    const es = createStatusEventSource(jobId)

    es.onmessage = (e) => {
      try {
        const data: JobState = JSON.parse(e.data)
        setJobState(data)

        if (data.status === "complete") {
          es.close()
          setResolved(true)
        } else if (data.status === "error") {
          es.close()
          setResolved(true)
        }
      } catch {
        // ignore
      }
    }

    es.onerror = () => {
      es.close()
      setResolved(true)
    }

    return () => es.close()
  }, [jobId])

  if (!jobId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-57px)] gap-4">
        <p className="font-mono text-sm" style={{ color: "var(--accent-red)" }}>
          ✗ No job ID found in URL.
        </p>
        <button
          onClick={() => router.push("/")}
          className="font-mono text-sm underline"
          style={{ color: "var(--accent-blue)" }}
        >
          ← Start over
        </button>
      </div>
    )
  }

  if (!resolved) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-57px)] gap-3">
        <span className="spin text-2xl" style={{ color: "var(--accent-blue)" }}>⟳</span>
        <p className="font-mono text-sm" style={{ color: "var(--text-muted)" }}>
          Loading results...
        </p>
      </div>
    )
  }

  if (jobState.status === "error") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-57px)] gap-4 px-4">
        <div
          className="rounded-lg px-6 py-5 max-w-lg w-full"
          style={{
            backgroundColor: "rgba(248,81,73,0.08)",
            border: "1px solid var(--accent-red)",
          }}
        >
          <p className="font-mono text-sm font-semibold mb-2" style={{ color: "var(--accent-red)" }}>
            ✗ Pipeline failed
          </p>
          <p className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
            {jobState.error}
          </p>
        </div>
        <button
          onClick={() => router.push("/")}
          className="font-mono text-sm underline"
          style={{ color: "var(--accent-blue)" }}
        >
          ← Try again
        </button>
      </div>
    )
  }

  return <ResultsPanel jobId={jobId} jobState={jobState} />
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[calc(100vh-57px)]">
          <span className="font-mono text-sm spin" style={{ color: "var(--text-muted)" }}>
            Loading...
          </span>
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  )
}
