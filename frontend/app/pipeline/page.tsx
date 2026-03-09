"use client"

import { useSearchParams, useRouter } from "next/navigation"
import { Suspense } from "react"
import PipelineProgress from "@/components/PipelineProgress"

function PipelineContent() {
  const params = useSearchParams()
  const router = useRouter()
  const jobId = params.get("job")

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
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-57px)] px-4 py-16">
      <div className="w-full max-w-xl mb-6">
        <h1 className="font-mono text-lg font-semibold mb-1" style={{ color: "var(--text-primary)" }}>
          Analysing your API spec...
        </h1>
        <p className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
          The pipeline runs 4 LangChain chains in sequence. This usually takes 30–90 seconds.
        </p>
      </div>

      <PipelineProgress jobId={jobId} />

      <button
        onClick={() => router.push("/")}
        className="mt-8 font-mono text-xs"
        style={{ color: "var(--text-muted)" }}
      >
        ← Cancel and start over
      </button>
    </div>
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
