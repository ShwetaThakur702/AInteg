"use client"

import { useSearchParams, useRouter } from "next/navigation"
import { Suspense, useState } from "react"
import PipelineProgress from "@/components/PipelineProgress"

function PipelineContent() {
  const params = useSearchParams()
  const router = useRouter()
  const jobId = params.get("job")
  const [showStopConfirm, setShowStopConfirm] = useState(false)
  const [pipelineStatus, setPipelineStatus] = useState<string>("queued")

  // We expose a status setter so PipelineProgress can inform us — but since
  // PipelineProgress manages its own state, we use a simple approach:
  // treat "running" and "queued" as interruptible. We read the status via
  // a callback prop if we had one, but for now we always show confirmation
  // when the user tries to leave (safe default).
  const isInterruptible = pipelineStatus === "running" || pipelineStatus === "queued"

  const handleHomeClick = () => {
    if (isInterruptible) {
      setShowStopConfirm(true)
    } else {
      router.push("/")
    }
  }

  const handleStopConfirm = () => {
    setShowStopConfirm(false)
    router.push("/")
  }

  const handleKeepWaiting = () => {
    setShowStopConfirm(false)
  }

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
          ← Go back
        </button>
      </div>
    )
  }

  return (
    <>
      {/* Stop confirmation modal */}
      {showStopConfirm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          style={{ backdropFilter: "blur(6px)", backgroundColor: "rgba(0,0,0,0.35)" }}
        >
          <div
            className="rounded-2xl px-8 py-6 flex flex-col gap-4 max-w-sm w-full mx-4"
            style={{
              backgroundColor: "#ffffff",
              border: "1px solid var(--border)",
              boxShadow: "0 24px 64px rgba(0,0,0,0.18)",
            }}
          >
            <div>
              <h2 className="font-mono font-semibold text-base mb-1" style={{ color: "var(--text-primary)" }}>
                Stop this pipeline?
              </h2>
              <p className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                The generation is still running.<br />
                Files will not be saved.
              </p>
            </div>
            <div className="flex items-center gap-3 mt-1">
              <button
                onClick={handleKeepWaiting}
                className="flex-1 py-2 rounded-lg font-mono text-sm font-medium transition-all"
                style={{
                  backgroundColor: "var(--bg-elevated)",
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--accent-blue)"
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border)"
                }}
              >
                Keep waiting
              </button>
              <button
                onClick={handleStopConfirm}
                className="flex-1 py-2 rounded-lg font-mono text-sm font-semibold transition-all"
                style={{
                  backgroundColor: "var(--accent-red)",
                  border: "1px solid var(--accent-red)",
                  color: "#ffffff",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.opacity = "0.88"
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.opacity = "1"
                }}
              >
                Stop &amp; go home
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-57px)] px-4 py-16">
        {/* Top nav bar */}
        <div className="w-full max-w-xl flex items-center justify-between mb-4">
          <button
            onClick={handleHomeClick}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-mono text-xs transition-all"
            style={{
              backgroundColor: "var(--bg-elevated)",
              border: "1px solid var(--border)",
              color: "var(--text-muted)",
            }}
            onMouseEnter={(e) => {
              const b = e.currentTarget as HTMLButtonElement
              b.style.borderColor = "var(--accent-blue)"
              b.style.color = "var(--accent-blue)"
            }}
            onMouseLeave={(e) => {
              const b = e.currentTarget as HTMLButtonElement
              b.style.borderColor = "var(--border)"
              b.style.color = "var(--text-muted)"
            }}
          >
            ← Home
          </button>
          <span
            className="font-mono text-xs px-2.5 py-1 rounded-lg"
            style={{
              backgroundColor: "var(--bg-elevated)",
              border: "1px solid var(--border)",
              color: "var(--text-muted)",
            }}
          >
            job: {jobId.slice(0, 8)}
          </span>
        </div>

        {/* Title */}
        <div className="w-full max-w-xl mb-6">
          <h1 className="font-mono text-lg font-semibold mb-1" style={{ color: "var(--text-primary)" }}>
            Analysing your API spec...
          </h1>
          <p className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
            The pipeline runs 4 LangChain chains in sequence. This usually takes 30–90 seconds.
          </p>
        </div>

        <PipelineProgress jobId={jobId} />

        {/* Stop & start over danger button at bottom */}
        <button
          onClick={() => setShowStopConfirm(true)}
          className="mt-8 flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-xs font-semibold transition-all"
          style={{
            backgroundColor: "rgba(220,38,38,0.08)",
            border: "1px solid rgba(220,38,38,0.3)",
            color: "var(--accent-red)",
          }}
          onMouseEnter={(e) => {
            const b = e.currentTarget as HTMLButtonElement
            b.style.backgroundColor = "rgba(220,38,38,0.16)"
            b.style.borderColor = "var(--accent-red)"
          }}
          onMouseLeave={(e) => {
            const b = e.currentTarget as HTMLButtonElement
            b.style.backgroundColor = "rgba(220,38,38,0.08)"
            b.style.borderColor = "rgba(220,38,38,0.3)"
          }}
        >
          ⛔ Stop &amp; start over
        </button>
      </div>
    </>
  )
}

export default function PipelinePage() {
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
      <PipelineContent />
    </Suspense>
  )
}
