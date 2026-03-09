"use client"

import { useState } from "react"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism"

interface Props {
  code: string
  language?: string
}

export default function CodeBlock({ code, language = "python" }: Props) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div
      className="rounded-xl overflow-hidden my-2"
      style={{
        border: "1px solid var(--border)",
        backgroundColor: "var(--bg-surface)",
        boxShadow: "var(--shadow-sm)",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-3 py-2"
        style={{
          backgroundColor: "var(--bg-elevated)",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <span className="font-mono text-xs font-medium" style={{ color: "var(--text-muted)" }}>
          {language}
        </span>
        <button
          onClick={handleCopy}
          className="font-mono text-xs font-medium transition-colors px-2 py-0.5 rounded"
          style={{
            color: copied ? "var(--accent-green)" : "var(--accent-blue)",
            backgroundColor: copied ? "rgba(22,163,74,0.1)" : "transparent",
          }}
        >
          {copied ? "Copied ✓" : "Copy"}
        </button>
      </div>

      <SyntaxHighlighter
        language={language}
        style={oneLight}
        customStyle={{
          margin: 0,
          padding: "12px 16px",
          fontSize: "12px",
          lineHeight: "1.65",
          backgroundColor: "var(--bg-surface)",
          borderRadius: 0,
        }}
        wrapLongLines={false}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  )
}
