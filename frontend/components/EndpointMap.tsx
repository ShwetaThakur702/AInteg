"use client"

import type { EndpointSummary } from "@/types/pipeline"

interface Props {
  endpoints: EndpointSummary[]
  onSelect?: (endpoint: EndpointSummary) => void
}

const METHOD_COLORS: Record<string, { bg: string; color: string }> = {
  GET:    { bg: "rgba(88,166,255,0.15)",  color: "#58a6ff" },
  POST:   { bg: "rgba(210,153,34,0.15)",  color: "#d29922" },
  PUT:    { bg: "rgba(88,166,255,0.10)",  color: "#79c0ff" },
  PATCH:  { bg: "rgba(210,153,34,0.10)",  color: "#e3b341" },
  DELETE: { bg: "rgba(248,81,73,0.15)",   color: "#f85149" },
}

function MethodBadge({ method }: { method: string }) {
  const m = method.toUpperCase()
  const style = METHOD_COLORS[m] ?? { bg: "rgba(125,133,144,0.2)", color: "#7d8590" }
  return (
    <span
      className="font-mono text-xs px-2 py-0.5 rounded shrink-0"
      style={{
        backgroundColor: style.bg,
        color: style.color,
        minWidth: "56px",
        textAlign: "center",
        border: `1px solid ${style.color}33`,
      }}
    >
      {m}
    </span>
  )
}

export default function EndpointMap({ endpoints, onSelect }: Props) {
  if (!endpoints || endpoints.length === 0) {
    return (
      <p className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
        No endpoints found.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-1">
      {endpoints.map((ep, i) => (
        <button
          key={i}
          onClick={() => onSelect?.(ep)}
          className="flex items-center gap-2 w-full rounded px-2 py-1.5 text-left transition-colors group"
          style={{ backgroundColor: "transparent" }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--bg-elevated)"
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent"
          }}
        >
          <MethodBadge method={ep.method} />
          <span
            className="font-mono text-xs truncate"
            style={{ color: "var(--text-code)" }}
          >
            {ep.path}
          </span>
          {ep.summary && (
            <span
              className="text-xs truncate hidden group-hover:block ml-auto"
              style={{ color: "var(--text-muted)" }}
            >
              {ep.summary}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}
