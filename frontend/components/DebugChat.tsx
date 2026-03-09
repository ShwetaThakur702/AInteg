"use client"

import { useState, useRef, useEffect } from "react"
import ChatMessage from "./ChatMessage"

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

interface Message {
  role: "user" | "assistant"
  content: string
  toolCalls?: string[]
  quickReplies?: string[]
  streaming?: boolean
}

interface Props {
  jobId: string
  prefilledMessage?: string
  onClose?: () => void
}

export default function DebugChat({ jobId, prefilledMessage, onClose }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Files generated! Paste your error and tell me which endpoint — I'll diagnose it using the spec and generated code.",
      quickReplies: [
        "How do I authenticate?",
        "Show me an example call",
        "What endpoints are available?",
      ],
    },
  ])
  const [input, setInput] = useState(prefilledMessage ?? "")
  const [loading, setLoading] = useState(false)
  const [showTrace, setShowTrace] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (prefilledMessage) setInput(prefilledMessage)
  }, [prefilledMessage])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = async (text?: string) => {
    const message = (text ?? input).trim()
    if (!message || loading) return

    setMessages((prev) => [...prev, { role: "user", content: message }])
    setInput("")
    setLoading(true)

    // Add streaming placeholder for assistant
    setMessages((prev) => [...prev, { role: "assistant", content: "", streaming: true }])

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_id: jobId,
          message,
          history: messages
            .filter((m) => !m.streaming)
            .map((m) => ({ role: m.role, content: m.content })),
        }),
      })

      if (!res.ok) {
        const errText = await res.text()
        throw new Error(errText)
      }

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      let accumulated = ""
      let toolCalls: string[] = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() ?? ""

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === "trace") {
              toolCalls = data.tools
              setMessages((prev) => {
                const updated = [...prev]
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  toolCalls,
                }
                return updated
              })
            } else if (data.type === "token") {
              accumulated += data.content
              setMessages((prev) => {
                const updated = [...prev]
                updated[updated.length - 1] = {
                  role: "assistant",
                  content: accumulated,
                  streaming: true,
                  toolCalls,
                }
                return updated
              })
            } else if (data.type === "done") {
              setMessages((prev) => {
                const updated = [...prev]
                updated[updated.length - 1] = {
                  role: "assistant",
                  content: accumulated,
                  streaming: false,
                  toolCalls,
                  quickReplies: data.quick_replies ?? [],
                }
                return updated
              })
            }
          } catch {
            // ignore malformed SSE line
          }
        }
      }
    } catch (e) {
      setMessages((prev) => {
        const updated = [...prev]
        updated[updated.length - 1] = {
          role: "assistant",
          content: `Error: ${e instanceof Error ? e.message : "Connection failed"}. Make sure the backend is running on port 8000.`,
          streaming: false,
        }
        return updated
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="flex flex-col h-full slide-in"
      style={{ backgroundColor: "var(--bg-surface)" }}
    >
      {/* ── Header ─────────────────────────────────────────── */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b shrink-0"
        style={{ borderColor: "var(--border)", backgroundColor: "var(--bg-elevated)" }}
      >
        <div className="flex items-center gap-3">
          <div>
            <span
              className="font-mono text-sm font-semibold"
              style={{ color: "var(--text-primary)" }}
            >
              Debug Chat
            </span>
            <span
              className="ml-2 text-xs font-mono px-1.5 py-0.5 rounded"
              style={{
                backgroundColor: "rgba(22,163,74,0.12)",
                color: "var(--accent-green)",
                border: "1px solid rgba(22,163,74,0.25)",
              }}
            >
              live · MCP
            </span>
          </div>

          {/* Tool trace toggle */}
          <button
            onClick={() => setShowTrace((t) => !t)}
            title="Toggle tool call trace"
            className="text-xs font-mono px-2 py-0.5 rounded transition-all"
            style={{
              backgroundColor: showTrace ? "rgba(124,58,237,0.12)" : "transparent",
              color: showTrace ? "var(--accent-blue)" : "var(--text-muted)",
              border: "1px solid var(--border)",
            }}
          >
            {showTrace ? "tools ✓" : "tools"}
          </button>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="w-6 h-6 flex items-center justify-center rounded font-mono text-sm"
            style={{
              color: "var(--text-muted)",
              border: "1px solid var(--border)",
            }}
          >
            ✕
          </button>
        )}
      </div>

      {/* ── Messages ───────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-4">
        {messages.map((msg, i) => (
          <div key={i} className="flex flex-col gap-1.5">
            <ChatMessage message={msg} />

            {/* Tool call trace (dev mode) */}
            {showTrace &&
              msg.role === "assistant" &&
              msg.toolCalls &&
              msg.toolCalls.length > 0 && (
                <div
                  className="text-xs font-mono px-3 py-1.5 rounded ml-1"
                  style={{
                    backgroundColor: "rgba(124,58,237,0.06)",
                    border: "1px solid var(--border)",
                    color: "var(--text-muted)",
                  }}
                >
                  fetched: {msg.toolCalls.join(" · ")}
                </div>
              )}

            {/* Quick-reply chips — only after last assistant message */}
            {msg.role === "assistant" &&
              !msg.streaming &&
              msg.quickReplies &&
              msg.quickReplies.length > 0 &&
              i === messages.length - 1 && (
                <div className="flex flex-wrap gap-1.5 ml-1">
                  {msg.quickReplies.map((r, ri) => (
                    <button
                      key={ri}
                      onClick={() => handleSend(r)}
                      disabled={loading}
                      className="text-xs font-mono px-2.5 py-1 rounded-full transition-all"
                      style={{
                        backgroundColor: "rgba(124,58,237,0.08)",
                        border: "1px solid var(--border)",
                        color: "var(--accent-blue)",
                        cursor: loading ? "not-allowed" : "pointer",
                      }}
                      onMouseEnter={(e) => {
                        if (!loading) {
                          ;(e.currentTarget as HTMLButtonElement).style.backgroundColor =
                            "rgba(124,58,237,0.18)"
                          ;(e.currentTarget as HTMLButtonElement).style.borderColor =
                            "var(--accent-blue)"
                        }
                      }}
                      onMouseLeave={(e) => {
                        ;(e.currentTarget as HTMLButtonElement).style.backgroundColor =
                          "rgba(124,58,237,0.08)"
                        ;(e.currentTarget as HTMLButtonElement).style.borderColor =
                          "var(--border)"
                      }}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              )}
          </div>
        ))}

        {/* Typing indicator while waiting for first token */}
        {loading && messages[messages.length - 1]?.content === "" && (
          <div className="flex justify-start">
            <div
              className="rounded px-3 py-2 text-sm font-mono flex items-center gap-2"
              style={{
                backgroundColor: "var(--bg-elevated)",
                color: "var(--text-muted)",
                border: "1px solid var(--border)",
              }}
            >
              <span className="spin" style={{ color: "var(--accent-blue)" }}>
                ⟳
              </span>
              <span>thinking...</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── Input ──────────────────────────────────────────── */}
      <div
        className="px-4 py-3 border-t flex gap-2 shrink-0"
        style={{ borderColor: "var(--border)", backgroundColor: "var(--bg-elevated)" }}
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
          placeholder="Paste your error here... (e.g. Getting 401 on POST /users)"
          rows={2}
          className="flex-1 rounded px-3 py-2 font-mono text-sm resize-none outline-none"
          style={{
            backgroundColor: "var(--bg-base)",
            border: "1px solid var(--border)",
            color: "var(--text-primary)",
          }}
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          className="px-3 py-2 rounded font-mono text-sm font-semibold self-end transition-all"
          style={{
            backgroundColor:
              input.trim() && !loading ? "var(--accent-blue)" : "var(--bg-base)",
            color: input.trim() && !loading ? "#ffffff" : "var(--text-muted)",
            cursor: input.trim() && !loading ? "pointer" : "not-allowed",
            border: "1px solid var(--border)",
            boxShadow:
              input.trim() && !loading
                ? "0 2px 8px rgba(124,58,237,0.3)"
                : "none",
          }}
        >
          →
        </button>
      </div>
    </div>
  )
}
