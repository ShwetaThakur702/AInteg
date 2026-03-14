"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { getConversations } from "@/lib/conversations"
import type { ConversationEntry } from "@/lib/conversations"

function timeAgo(timestamp: number): string {
  const diffMs = Date.now() - timestamp
  const diffSecs = Math.floor(diffMs / 1000)
  if (diffSecs < 60) return `${diffSecs}s ago`
  const diffMins = Math.floor(diffSecs / 60)
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

export default function HeaderNav() {
  const router = useRouter()
  const [historyOpen, setHistoryOpen] = useState(false)
  const [conversations, setConversations] = useState<ConversationEntry[]>([])
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setConversations(getConversations())
  }, [historyOpen])

  useEffect(() => {
    if (!historyOpen) return
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setHistoryOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [historyOpen])

  return (
    <header
      className="border-b flex items-center justify-between px-6 py-3"
      style={{
        borderColor: "var(--border)",
        backgroundColor: "#ffffff",
        boxShadow: "0 1px 0 var(--border)",
      }}
    >
      {/* Left side: logo + version */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all"
          style={{ backgroundColor: "var(--bg-elevated)", border: "1px solid var(--border)" }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--accent-blue)"
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border)"
          }}
        >
          <span style={{ color: "var(--accent-blue)", fontSize: "16px" }}>⬡</span>
          <span className="font-mono text-sm font-bold" style={{ color: "var(--text-primary)" }}>
            API Integration Agent
          </span>
        </button>
        <span
          className="text-xs px-2 py-0.5 rounded-full font-mono font-medium"
          style={{
            backgroundColor: "var(--accent-blue)",
            color: "#fff",
          }}
        >
          v1.0
        </span>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Tech badges */}
        {["FastAPI", "LangChain", "OpenRouter"].map((t) => (
          <span
            key={t}
            className="text-xs px-2 py-1 rounded-md font-mono"
            style={{
              backgroundColor: "var(--bg-elevated)",
              color: "var(--text-muted)",
              border: "1px solid var(--border)",
            }}
          >
            {t}
          </span>
        ))}

        {/* History button + dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setHistoryOpen((o) => !o)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-mono text-xs transition-all"
            style={{
              backgroundColor: historyOpen ? "var(--bg-elevated)" : "var(--bg-base)",
              border: `1px solid ${historyOpen ? "var(--accent-blue)" : "var(--border)"}`,
              color: historyOpen ? "var(--accent-blue)" : "var(--text-muted)",
            }}
          >
            <span style={{ fontSize: "13px" }}>🕐</span>
            <span>History</span>
            {conversations.length > 0 && (
              <span
                className="inline-flex items-center justify-center rounded-full font-mono text-xs"
                style={{
                  backgroundColor: "var(--accent-blue)",
                  color: "#fff",
                  minWidth: "18px",
                  height: "18px",
                  fontSize: "10px",
                  padding: "0 4px",
                }}
              >
                {conversations.length}
              </span>
            )}
          </button>

          {historyOpen && (
            <div
              className="absolute right-0 top-full mt-2 rounded-xl overflow-hidden z-50"
              style={{
                minWidth: "320px",
                backgroundColor: "#ffffff",
                border: "1px solid var(--border)",
                boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
              }}
            >
              <div
                className="px-4 py-2.5 border-b"
                style={{ borderColor: "var(--border)", backgroundColor: "var(--bg-surface)" }}
              >
                <span className="font-mono text-xs font-semibold" style={{ color: "var(--text-muted)" }}>
                  Recent Runs
                </span>
              </div>

              {conversations.length === 0 ? (
                <div className="px-4 py-6 text-center">
                  <p className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                    No previous runs yet
                  </p>
                </div>
              ) : (
                <div className="flex flex-col">
                  {conversations.map((entry) => (
                    <button
                      key={entry.jobId}
                      onClick={() => {
                        setHistoryOpen(false)
                        router.push(`/results?job=${entry.jobId}`)
                      }}
                      className="flex items-start gap-3 px-4 py-3 text-left transition-all border-b last:border-b-0"
                      style={{ borderColor: "var(--border)" }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--bg-surface)"
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent"
                      }}
                    >
                      <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                        <span className="font-mono text-sm font-semibold truncate" style={{ color: "var(--text-primary)" }}>
                          {entry.label}
                        </span>
                        <div className="flex items-center gap-2">
                          <span
                            className="text-xs px-1.5 py-0.5 rounded font-mono"
                            style={{
                              backgroundColor: "var(--bg-elevated)",
                              color: "var(--text-muted)",
                              border: "1px solid var(--border)",
                            }}
                          >
                            {entry.endpointCount} endpoints
                          </span>
                          <span
                            className="text-xs px-1.5 py-0.5 rounded font-mono"
                            style={{
                              backgroundColor: "var(--bg-elevated)",
                              color: "var(--text-muted)",
                              border: "1px solid var(--border)",
                            }}
                          >
                            {entry.authType}
                          </span>
                        </div>
                      </div>
                      <span className="font-mono text-xs shrink-0 mt-0.5" style={{ color: "var(--text-muted)" }}>
                        {timeAgo(entry.timestamp)}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* New Run button */}
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-mono text-xs font-semibold transition-all"
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
          <span>+</span>
          <span>New Run</span>
        </button>
      </div>
    </header>
  )
}
