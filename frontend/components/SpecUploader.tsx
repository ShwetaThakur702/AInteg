"use client"

import { useState, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { runPipeline } from "@/lib/api"

type InputMode = "file" | "url" | "paste"

const MODES: { id: InputMode; label: string; icon: string }[] = [
  { id: "file",  label: "Upload File", icon: "↑" },
  { id: "url",   label: "Paste URL",   icon: "⛓" },
  { id: "paste", label: "Paste Spec",  icon: "✎" },
]

export default function SpecUploader() {
  const router = useRouter()
  const [mode, setMode] = useState<InputMode>("file")
  const [dragging, setDragging] = useState(false)
  const [droppedFile, setDroppedFile] = useState<File | null>(null)
  const [url, setUrl] = useState("")
  const [urlError, setUrlError] = useState("")
  const [pastedSpec, setPastedSpec] = useState("")
  const [pasteError, setPasteError] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const reset = (nextMode: InputMode) => {
    setMode(nextMode)
    setDroppedFile(null)
    setUrl("")
    setUrlError("")
    setPastedSpec("")
    setPasteError("")
    setError("")
  }

  // ── Drag handlers ─────────────────────────────────────────

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => setDragging(false), [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (!file) return
    const valid = /\.(json|yaml|yml)$/.test(file.name)
    if (!valid) { setError("Only .json, .yaml, or .yml files are accepted"); return }
    setDroppedFile(file)
    setError("")
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setDroppedFile(file)
    setError("")
  }

  // ── URL validation ────────────────────────────────────────

  const validateUrl = (val: string) => {
    if (!val) { setUrlError("URL is required"); return false }
    if (!val.startsWith("http://") && !val.startsWith("https://")) {
      setUrlError("URL must start with http:// or https://")
      return false
    }
    setUrlError("")
    return true
  }

  // ── Paste spec validation ─────────────────────────────────

  const validatePaste = (val: string) => {
    if (!val.trim()) { setPasteError("Spec content is required"); return false }
    try {
      const parsed = JSON.parse(val)
      if (!parsed.paths) { setPasteError("Missing 'paths' key — not a valid OpenAPI spec"); return false }
    } catch {
      // Try as YAML — basic check
      if (!val.includes("paths:")) { setPasteError("Doesn't look like a valid OpenAPI spec"); return false }
    }
    setPasteError("")
    return true
  }

  // ── Submit ─────────────────────────────────────────────────

  const handleSubmit = async () => {
    setError("")
    let input: File | string

    if (mode === "file") {
      if (!droppedFile) { setError("Please upload a file"); return }
      input = droppedFile
    } else if (mode === "url") {
      if (!validateUrl(url)) return
      input = url
    } else {
      if (!validatePaste(pastedSpec)) return
      // Convert pasted text to a File object
      const blob = new Blob([pastedSpec], { type: "application/json" })
      input = new File([blob], "pasted_spec.json", { type: "application/json" })
    }

    setLoading(true)
    try {
      const { job_id } = await runPipeline(input)
      router.push(`/pipeline?job=${job_id}`)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start pipeline")
      setLoading(false)
    }
  }

  const canSubmit =
    !loading &&
    (mode === "file" ? !!droppedFile : mode === "url" ? !!url : !!pastedSpec.trim())

  const fileExt = droppedFile?.name.split(".").pop()?.toUpperCase()

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col gap-4">

      {/* Mode toggle */}
      <div
        className="flex rounded-lg overflow-hidden"
        style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-surface)" }}
      >
        {MODES.map((m, i) => (
          <button
            key={m.id}
            onClick={() => reset(m.id)}
            className="flex-1 py-2.5 text-sm font-mono transition-colors"
            style={{
              backgroundColor: mode === m.id ? "var(--bg-elevated)" : "transparent",
              color: mode === m.id ? "var(--text-primary)" : "var(--text-muted)",
              borderRight: i < MODES.length - 1 ? "1px solid var(--border)" : undefined,
              fontWeight: mode === m.id ? 600 : 400,
            }}
          >
            {m.icon} {m.label}
          </button>
        ))}
      </div>

      {/* ── File drop zone ──────────────────────────────────── */}
      {mode === "file" && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-all select-none"
          style={{
            borderColor: dragging
              ? "var(--accent-blue)"
              : droppedFile
              ? "var(--accent-green)"
              : "var(--border)",
            backgroundColor: dragging
              ? "rgba(124,58,237,0.06)"
              : "var(--bg-base)",
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.yaml,.yml"
            className="hidden"
            onChange={handleFileSelect}
          />
          {droppedFile ? (
            <div className="flex flex-col items-center gap-2">
              <div className="flex items-center gap-2">
                <span
                  className="font-mono text-xs px-2 py-0.5 rounded font-semibold"
                  style={{ backgroundColor: "var(--accent-green)", color: "#000" }}
                >
                  {fileExt}
                </span>
                <span className="font-mono text-sm" style={{ color: "var(--accent-green)" }}>
                  {droppedFile.name}
                </span>
              </div>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                {(droppedFile.size / 1024).toFixed(1)} KB · Click to change
              </span>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <span className="text-3xl opacity-60">📄</span>
              <p className="font-mono text-sm" style={{ color: "var(--text-primary)" }}>
                Drop your OpenAPI spec here
              </p>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                .json · .yaml · .yml &nbsp;·&nbsp; or click to browse
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── URL input ───────────────────────────────────────── */}
      {mode === "url" && (
        <div className="flex flex-col gap-1.5">
          <input
            type="url"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setUrlError("") }}
            onBlur={() => url && validateUrl(url)}
            placeholder="https://petstore3.swagger.io/api/v3/openapi.json"
            className="w-full rounded-lg px-3 py-3 font-mono text-sm outline-none transition-colors"
            style={{
              backgroundColor: "var(--bg-surface)",
              border: `1px solid ${urlError ? "var(--accent-red)" : "var(--border)"}`,
              color: "var(--text-primary)",
            }}
          />
          {urlError && (
            <span className="text-xs font-mono px-1" style={{ color: "var(--accent-red)" }}>
              {urlError}
            </span>
          )}
          <p className="text-xs px-1" style={{ color: "var(--text-muted)" }}>
            Paste a direct URL to a JSON or YAML OpenAPI spec. Raw GitHub URLs work too.
          </p>
        </div>
      )}

      {/* ── Paste spec textarea ─────────────────────────────── */}
      {mode === "paste" && (
        <div className="flex flex-col gap-1.5">
          <textarea
            value={pastedSpec}
            onChange={(e) => { setPastedSpec(e.target.value); setPasteError("") }}
            onBlur={() => pastedSpec.trim() && validatePaste(pastedSpec)}
            placeholder={`Paste your OpenAPI spec here (JSON or YAML)...\n\n{\n  "openapi": "3.0.0",\n  "paths": { ... }\n}`}
            rows={12}
            className="w-full rounded-lg px-3 py-3 font-mono text-xs outline-none resize-y transition-colors"
            style={{
              backgroundColor: "var(--bg-surface)",
              border: `1px solid ${pasteError ? "var(--accent-red)" : "var(--border)"}`,
              color: "var(--text-primary)",
              lineHeight: "1.6",
              minHeight: "220px",
            }}
          />
          <div className="flex items-center justify-between px-1">
            {pasteError ? (
              <span className="text-xs font-mono" style={{ color: "var(--accent-red)" }}>
                {pasteError}
              </span>
            ) : (
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                JSON or YAML · must contain a &quot;paths&quot; key
              </span>
            )}
            <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
              {pastedSpec.length.toLocaleString()} chars
            </span>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div
          className="rounded-lg px-3 py-2.5 text-sm font-mono"
          style={{
            backgroundColor: "rgba(248,81,73,0.08)",
            border: "1px solid var(--accent-red)",
            color: "var(--accent-red)",
          }}
        >
          ✗ {error}
        </div>
      )}

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        className="w-full py-3 rounded-lg font-mono font-semibold text-sm transition-all"
        style={{
          backgroundColor: canSubmit ? "var(--accent-blue)" : "var(--bg-elevated)",
          color: canSubmit ? "#ffffff" : "var(--text-muted)",
          cursor: canSubmit ? "pointer" : "not-allowed",
          border: canSubmit ? "none" : "1px solid var(--border)",
          boxShadow: canSubmit ? "0 4px 14px rgba(124,58,237,0.35)" : "none",
        }}
      >
        {loading ? "⟳  Starting pipeline..." : "→  Generate Integration Code"}
      </button>
    </div>
  )
}
