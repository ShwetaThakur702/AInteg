"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { getDownloadUrl } from "@/lib/api"
import EndpointMap from "./EndpointMap"
import DebugChat from "./DebugChat"
import FilePreviewModal from "./FilePreviewModal"
import type { JobState, EndpointSummary } from "@/types/pipeline"

interface Props {
  jobId: string
  jobState: JobState
}

const FILE_META: Record<string, { desc: string; icon: string }> = {
  "client_stubs.py":   { desc: "httpx client · auth + retry",       icon: "🔌" },
  "usage_examples.py": { desc: "Usage examples per endpoint",        icon: "📖" },
  "contract_tests.py": { desc: "pytest · Pydantic schema validation", icon: "🧪" },
}

function DownloadCard({
  filename,
  jobId,
  endpointCount,
  onPreview,
}: {
  filename: string
  jobId: string
  endpointCount: number
  onPreview: () => void
}) {
  const [hovered, setHovered] = useState(false)
  const meta = FILE_META[filename] ?? { desc: "Generated Python file", icon: "📄" }

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="flex items-center gap-3 rounded-xl px-4 py-3 transition-all"
      style={{
        backgroundColor: "var(--bg-elevated)",
        border: `1px solid ${hovered ? "var(--accent-blue)" : "var(--border)"}`,
        boxShadow: hovered ? "0 0 0 1px rgba(124,106,247,0.2), 0 4px 16px rgba(0,0,0,0.3)" : "none",
      }}
    >
      {/* Icon */}
      <span className="text-xl shrink-0">{meta.icon}</span>

      {/* Info */}
      <div className="flex flex-col gap-0.5 flex-1 min-w-0">
        <span className="font-mono text-sm font-semibold truncate" style={{ color: "var(--text-primary)" }}>
          {filename}
        </span>
        <span className="text-xs truncate" style={{ color: "var(--text-muted)" }}>
          {meta.desc} · {endpointCount} endpoints
        </span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Eye — preview */}
        <button
          onClick={onPreview}
          title="Preview file"
          className="w-8 h-8 flex items-center justify-center rounded-lg transition-all text-sm"
          style={{
            backgroundColor: "rgba(124,106,247,0.12)",
            border: "1px solid var(--border)",
            color: "var(--accent-blue)",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "rgba(124,106,247,0.25)"
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = "var(--accent-blue)"
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "rgba(124,106,247,0.12)"
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border)"
          }}
        >
          👁
        </button>

        {/* Download */}
        <a
          href={getDownloadUrl(jobId, filename)}
          download={filename}
          title="Download file"
          className="font-mono text-xs px-2.5 py-1.5 rounded-lg transition-all no-underline"
          style={{
            backgroundColor: hovered ? "rgba(74,222,128,0.15)" : "var(--bg-base)",
            color: hovered ? "var(--accent-green)" : "var(--text-muted)",
            border: `1px solid ${hovered ? "var(--accent-green)" : "var(--border)"}`,
          }}
        >
          ↓ .py
        </a>
      </div>
    </div>
  )
}

function InfoRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-baseline gap-2">
      <span className="text-xs font-mono w-28 shrink-0" style={{ color: "var(--text-muted)" }}>
        {label}
      </span>
      <span
        className={`text-xs truncate ${mono ? "font-mono" : ""}`}
        style={{ color: "var(--text-code)" }}
      >
        {value}
      </span>
    </div>
  )
}

export default function ResultsPanel({ jobId, jobState }: Props) {
  const router = useRouter()
  const [chatOpen, setChatOpen]           = useState(false)
  const [prefilledMessage, setPrefilledMessage] = useState("")
  const [previewFile, setPreviewFile]     = useState<string | null>(null)

  const endpoints    = jobState.spec_summary?.endpoints ?? []
  const outputFiles  = jobState.output_files ?? []
  const endpointCount = endpoints.length

  const handleEndpointSelect = (ep: EndpointSummary) => {
    setPrefilledMessage(`I'm getting an error on ${ep.method.toUpperCase()} ${ep.path}`)
    setChatOpen(true)
  }

  return (
    <>
      {/* ── File preview modal ─────────────────────────────── */}
      {previewFile && (
        <FilePreviewModal
          jobId={jobId}
          filename={previewFile}
          onClose={() => setPreviewFile(null)}
        />
      )}

      <div className="flex h-[calc(100vh-57px)]">
        {/* ── Left panel ─────────────────────────────────────── */}
        <div
          className="flex flex-col overflow-y-auto"
          style={{
            width: chatOpen ? "45%" : "100%",
            transition: "width 0.3s ease",
            borderRight: chatOpen ? `1px solid var(--border)` : undefined,
          }}
        >
          {/* Header */}
          <div
            className="px-6 py-4 border-b shrink-0"
            style={{ borderColor: "var(--border)", backgroundColor: "var(--bg-surface)" }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {/* Home button */}
                <button
                  onClick={() => router.push("/")}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-mono text-xs transition-all"
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
                <div>
                  <h1 className="font-mono font-semibold" style={{ color: "var(--text-primary)" }}>
                    Results
                  </h1>
                  <p className="text-xs font-mono mt-0.5" style={{ color: "var(--text-muted)" }}>
                    session: {jobId.slice(0, 8)}
                  </p>
                </div>
              </div>
              <span
                className="text-xs font-mono px-2.5 py-1 rounded-lg"
                style={{
                  backgroundColor: "rgba(74,222,128,0.12)",
                  color: "var(--accent-green)",
                  border: "1px solid rgba(74,222,128,0.25)",
                }}
              >
                ✓ complete
              </span>
            </div>
          </div>

          <div className="px-6 py-5 flex flex-col gap-6">
            {/* AI Debug Assistant banner */}
            {!chatOpen ? (
              <div
                className="flex items-center justify-between rounded-xl px-4 py-3"
                style={{
                  background: "linear-gradient(135deg, rgba(124,58,237,0.12), rgba(147,51,234,0.08))",
                  border: "1px solid rgba(124,58,237,0.3)",
                }}
              >
                <div className="flex flex-col gap-0.5">
                  <span
                    className="font-mono font-semibold text-sm"
                    style={{ color: "var(--accent-blue)" }}
                  >
                    ✨ AI Debug Assistant
                  </span>
                  <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                    Diagnose errors using your spec &amp; generated code
                  </span>
                </div>
                <button
                  onClick={() => setChatOpen(true)}
                  className="px-3 py-1.5 rounded-lg font-mono text-xs font-semibold transition-all shrink-0 ml-4"
                  style={{
                    backgroundColor: "var(--accent-blue)",
                    color: "#ffffff",
                    border: "1px solid var(--accent-blue)",
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--accent-purple)"
                    ;(e.currentTarget as HTMLButtonElement).style.borderColor = "var(--accent-purple)"
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--accent-blue)"
                    ;(e.currentTarget as HTMLButtonElement).style.borderColor = "var(--accent-blue)"
                  }}
                >
                  Open →
                </button>
              </div>
            ) : (
              <div
                className="flex items-center justify-between rounded-xl px-4 py-2"
                style={{
                  background: "linear-gradient(135deg, rgba(124,58,237,0.12), rgba(147,51,234,0.08))",
                  border: "1px solid rgba(124,58,237,0.3)",
                }}
              >
                <span
                  className="font-mono font-semibold text-sm"
                  style={{ color: "var(--accent-blue)" }}
                >
                  ✨ AI Debug Assistant · <span style={{ color: "var(--accent-green)" }}>live</span>
                </span>
                <button
                  onClick={() => { setChatOpen(false); setPrefilledMessage("") }}
                  className="px-3 py-1 rounded-lg font-mono text-xs transition-all"
                  style={{
                    backgroundColor: "transparent",
                    border: "1px solid rgba(124,58,237,0.3)",
                    color: "var(--text-muted)",
                  }}
                  onMouseEnter={(e) => {
                    const b = e.currentTarget as HTMLButtonElement
                    b.style.borderColor = "var(--accent-blue)"
                    b.style.color = "var(--accent-blue)"
                  }}
                  onMouseLeave={(e) => {
                    const b = e.currentTarget as HTMLButtonElement
                    b.style.borderColor = "rgba(124,58,237,0.3)"
                    b.style.color = "var(--text-muted)"
                  }}
                >
                  ✕ Close
                </button>
              </div>
            )}

            {/* Generated files */}
            <section>
              <h2
                className="text-xs font-mono font-semibold uppercase tracking-widest mb-3"
                style={{ color: "var(--text-muted)" }}
              >
                Generated Files
              </h2>
              <div className="flex flex-col gap-2.5">
                {outputFiles.length > 0 ? (
                  outputFiles.map((f) => (
                    <DownloadCard
                      key={f}
                      filename={f}
                      jobId={jobId}
                      endpointCount={endpointCount}
                      onPreview={() => setPreviewFile(f)}
                    />
                  ))
                ) : (
                  <p className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
                    No files available.
                  </p>
                )}
              </div>
            </section>

            {/* API summary */}
            {jobState.spec_summary && (
              <section>
                <h2
                  className="text-xs font-mono font-semibold uppercase tracking-widest mb-3"
                  style={{ color: "var(--text-muted)" }}
                >
                  API Summary
                </h2>
                <div
                  className="rounded-xl px-4 py-3 flex flex-col gap-2"
                  style={{
                    backgroundColor: "var(--bg-elevated)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <InfoRow label="Base URL"   value={jobState.spec_summary.base_url} mono />
                  <InfoRow label="Auth"        value={jobState.spec_summary.auth_type} />
                  <InfoRow label="Location"    value={jobState.spec_summary.auth_location ?? "none"} />
                  <InfoRow label="Pagination"  value={jobState.spec_summary.pagination_style} />
                  <InfoRow label="Endpoints"   value={String(endpointCount)} />
                </div>
              </section>
            )}

            {/* Endpoint map */}
            {endpoints.length > 0 && (
              <section>
                <h2
                  className="text-xs font-mono font-semibold uppercase tracking-widest mb-3"
                  style={{ color: "var(--text-muted)" }}
                >
                  Endpoints · click to debug
                </h2>
                <div
                  className="rounded-xl px-3 py-2"
                  style={{
                    backgroundColor: "var(--bg-elevated)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <EndpointMap endpoints={endpoints} onSelect={handleEndpointSelect} />
                </div>
              </section>
            )}
          </div>
        </div>

        {/* ── Right panel — debug chat ───────────────────────── */}
        {chatOpen && (
          <div className="flex-1 flex flex-col" style={{ minWidth: 0 }}>
            <DebugChat
              jobId={jobId}
              prefilledMessage={prefilledMessage}
              onClose={() => { setChatOpen(false); setPrefilledMessage("") }}
            />
          </div>
        )}
      </div>
    </>
  )
}
