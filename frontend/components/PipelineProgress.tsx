"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { createStatusEventSource } from "@/lib/api"
import type { JobState, ChainStage } from "@/types/pipeline"

interface Props {
  jobId: string
}

const STAGES: { key: ChainStage | "complete"; label: string; progress: number }[] = [
  { key: "chain_1",    label: "Chain 1 · Spec Analysis",   progress: 10  },
  { key: "chain_2",    label: "Chain 2 · Client Stubs",     progress: 30  },
  { key: "chain_3",    label: "Chain 3 · Usage Examples",   progress: 55  },
  { key: "chain_4",    label: "Chain 4 · Contract Tests",   progress: 75  },
  { key: "validation", label: "Validation · AST + pytest",  progress: 90  },
  { key: "complete",   label: "Complete",                   progress: 100 },
]

type StageState = "pending" | "running" | "done" | "error"

function stageStateFor(stage: ChainStage | null, status: string, key: string): StageState {
  if (status === "error") {
    const currentIdx = STAGES.findIndex((s) => s.key === stage)
    const thisIdx    = STAGES.findIndex((s) => s.key === key)
    if (thisIdx === currentIdx) return "error"
    if (thisIdx < currentIdx)  return "done"
    return "pending"
  }
  if (status === "complete") {
    if (key === "complete") return "done"
    return "done"
  }
  const currentIdx = STAGES.findIndex((s) => s.key === stage)
  const thisIdx    = STAGES.findIndex((s) => s.key === key)
  if (thisIdx < currentIdx)  return "done"
  if (thisIdx === currentIdx) return "running"
  return "pending"
}

function StageIcon({ state }: { state: StageState }) {
  if (state === "done")    return <span style={{ color: "var(--accent-green)" }}>✓</span>
  if (state === "running") return <span className="spin" style={{ color: "var(--accent-orange)" }}>⟳</span>
  if (state === "error")   return <span style={{ color: "var(--accent-red)" }}>✗</span>
  return <span style={{ color: "var(--text-muted)" }}>○</span>
}

function StageLabel({ state, label }: { state: StageState; label: string }) {
  const color =
    state === "done"    ? "var(--accent-green)"  :
    state === "running" ? "var(--text-primary)"  :
    state === "error"   ? "var(--accent-red)"    :
                          "var(--text-muted)"
  return (
    <span className="font-mono text-sm" style={{ color }}>
      {label}
    </span>
  )
}

function StateTag({ state }: { state: StageState }) {
  const map = {
    done:    { label: "done",    color: "var(--accent-green)"  },
    running: { label: "running", color: "var(--accent-orange)" },
    error:   { label: "error",   color: "var(--accent-red)"    },
    pending: { label: "pending", color: "var(--text-muted)"    },
  }
  const { label, color } = map[state]
  return (
    <span className="ml-auto font-mono text-xs" style={{ color }}>
      {label}
    </span>
  )
}

export default function PipelineProgress({ jobId }: Props) {
  const router = useRouter()
  const [jobState, setJobState] = useState<JobState>({
    status: "queued",
    stage: null,
    progress: 0,
    error: null,
    spec_summary: null,
    output_files: [],
  })

  useEffect(() => {
    const es = createStatusEventSource(jobId)

    es.onmessage = (e) => {
      try {
        const data: JobState = JSON.parse(e.data)
        setJobState(data)
        if (data.status === "complete") {
          es.close()
          setTimeout(() => router.push(`/results?job=${jobId}`), 600)
        }
        if (data.status === "error") {
          es.close()
        }
      } catch {
        // ignore parse errors
      }
    }

    es.onerror = () => {
      es.close()
      setJobState((prev) => ({
        ...prev,
        status: "error",
        error: "Connection to backend lost. Is the server running?",
      }))
    }

    return () => es.close()
  }, [jobId, router])

  const displayStages = STAGES.filter((s) => s.key !== "complete")
  const progressPct = jobState.progress

  return (
    <div
      className="w-full max-w-xl mx-auto rounded-lg overflow-hidden"
      style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-surface)" }}
    >
      {/* Header */}
      <div
        className="px-5 py-4 border-b"
        style={{ borderColor: "var(--border)", backgroundColor: "var(--bg-elevated)" }}
      >
        <h2 className="font-mono text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
          {jobState.status === "error"
            ? "✗ Pipeline failed"
            : jobState.status === "complete"
            ? "✓ Pipeline complete"
            : "⟳ Running pipeline..."}
        </h2>
        <p className="text-xs mt-0.5 font-mono" style={{ color: "var(--text-muted)" }}>
          job: {jobId.slice(0, 8)}
        </p>
      </div>

      {/* Stage list */}
      <div className="px-5 py-4 flex flex-col gap-3">
        {displayStages.map((s) => {
          const state = stageStateFor(jobState.stage, jobState.status, s.key)
          return (
            <div key={s.key} className="flex items-center gap-3">
              <StageIcon state={state} />
              <StageLabel state={state} label={s.label} />
              <StateTag state={state} />
            </div>
          )
        })}
      </div>

      {/* Progress bar */}
      <div className="px-5 pb-5">
        <div
          className="w-full rounded-full overflow-hidden"
          style={{ height: "6px", backgroundColor: "var(--bg-elevated)" }}
        >
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${progressPct}%`,
              backgroundColor:
                jobState.status === "error"
                  ? "var(--accent-red)"
                  : jobState.status === "complete"
                  ? "var(--accent-green)"
                  : "var(--accent-blue)",
            }}
          />
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
            {jobState.stage ? jobState.stage.replace("_", " ") : "queued"}
          </span>
          <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
            {progressPct}%
          </span>
        </div>
      </div>

      {/* Error message */}
      {jobState.status === "error" && jobState.error && (
        <div
          className="mx-5 mb-5 rounded px-3 py-2 text-xs font-mono"
          style={{
            backgroundColor: "rgba(248,81,73,0.1)",
            border: "1px solid var(--accent-red)",
            color: "var(--accent-red)",
          }}
        >
          {jobState.error}
        </div>
      )}
    </div>
  )
}
