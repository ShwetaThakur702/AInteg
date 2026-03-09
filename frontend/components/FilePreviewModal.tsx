"use client"

import { useEffect, useState, useCallback } from "react"
import { getDownloadUrl } from "@/lib/api"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism"

interface Props {
  jobId: string
  filename: string
  onClose: () => void
}

export default function FilePreviewModal({ jobId, filename, onClose }: Props) {
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [copied, setCopied] = useState(false)

  // Close on Escape key
  const handleKey = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") onClose()
  }, [onClose])

  useEffect(() => {
    document.addEventListener("keydown", handleKey)
    document.body.style.overflow = "hidden"
    return () => {
      document.removeEventListener("keydown", handleKey)
      document.body.style.overflow = ""
    }
  }, [handleKey])

  // Fetch file content
  useEffect(() => {
    const url = getDownloadUrl(jobId, filename)
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.text()
      })
      .then((text) => { setContent(text); setLoading(false) })
      .catch((e) => { setError(e.message); setLoading(false) })
  }, [jobId, filename])

  const handleCopy = async () => {
    if (!content) return
    await navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const lineCount = content?.split("\n").length ?? 0

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-in"
      style={{ backgroundColor: "rgba(30,10,60,0.55)", backdropFilter: "blur(6px)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div
        className="modal-in flex flex-col rounded-xl overflow-hidden w-full"
        style={{
          maxWidth: "860px",
          maxHeight: "88vh",
          backgroundColor: "var(--bg-base)",
          border: "1px solid var(--border)",
          boxShadow: "0 24px 64px rgba(124,58,237,0.2), 0 0 0 1px rgba(124,58,237,0.12)",
        }}
      >
        {/* ── Header ────────────────────────────────────────── */}
        <div
          className="flex items-center justify-between px-5 py-3.5 shrink-0"
          style={{
            backgroundColor: "var(--bg-surface)",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <div className="flex items-center gap-3">
            <span style={{ color: "var(--accent-purple)" }}>📄</span>
            <span className="font-mono text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
              {filename}
            </span>
            {content && (
              <span
                className="font-mono text-xs px-2 py-0.5 rounded"
                style={{
                  backgroundColor: "rgba(124,106,247,0.12)",
                  color: "var(--text-muted)",
                  border: "1px solid var(--border)",
                }}
              >
                {lineCount} lines
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Copy button */}
            <button
              onClick={handleCopy}
              disabled={!content}
              className="font-mono text-xs px-3 py-1.5 rounded transition-all"
              style={{
                backgroundColor: copied ? "rgba(74,222,128,0.15)" : "var(--bg-base)",
                color: copied ? "var(--accent-green)" : "var(--text-muted)",
                border: `1px solid ${copied ? "var(--accent-green)" : "var(--border)"}`,
              }}
            >
              {copied ? "Copied ✓" : "Copy"}
            </button>

            {/* Download button */}
            <a
              href={getDownloadUrl(jobId, filename)}
              download={filename}
              className="font-mono text-xs px-3 py-1.5 rounded transition-all no-underline"
              style={{
                backgroundColor: "rgba(124,106,247,0.12)",
                color: "var(--accent-blue)",
                border: "1px solid var(--border)",
              }}
            >
              ↓ Download
            </a>

            {/* Close button */}
            <button
              onClick={onClose}
              className="w-7 h-7 flex items-center justify-center rounded transition-colors font-mono text-sm"
              style={{
                backgroundColor: "var(--bg-base)",
                color: "var(--text-muted)",
                border: "1px solid var(--border)",
              }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* ── Content ───────────────────────────────────────── */}
        <div className="flex-1 overflow-auto">
          {loading && (
            <div className="flex items-center justify-center h-48 gap-3">
              <span className="spin" style={{ color: "var(--accent-blue)" }}>⟳</span>
              <span className="font-mono text-sm" style={{ color: "var(--text-muted)" }}>
                Loading {filename}...
              </span>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-48">
              <span className="font-mono text-sm" style={{ color: "var(--accent-red)" }}>
                ✗ Could not load file: {error}
              </span>
            </div>
          )}

          {content && (
            <SyntaxHighlighter
              language="python"
              style={oneLight}
              showLineNumbers
              lineNumberStyle={{
                color: "var(--border)",
                fontSize: "11px",
                minWidth: "3em",
                paddingRight: "1em",
              }}
              customStyle={{
                margin: 0,
                padding: "16px 20px",
                fontSize: "12.5px",
                lineHeight: "1.65",
                backgroundColor: "transparent",
                borderRadius: 0,
              }}
              wrapLongLines={false}
            >
              {content}
            </SyntaxHighlighter>
          )}
        </div>

        {/* ── Footer hint ───────────────────────────────────── */}
        <div
          className="px-5 py-2 shrink-0 flex items-center justify-between"
          style={{
            borderTop: "1px solid var(--border)",
            backgroundColor: "var(--bg-elevated)",
          }}
        >
          <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
            python · read-only preview
          </span>
          <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
            esc to close
          </span>
        </div>
      </div>
    </div>
  )
}
