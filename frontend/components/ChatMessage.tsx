"use client"

import CodeBlock from "./CodeBlock"

interface Message {
  role: "user" | "assistant"
  content: string
}

interface Props {
  message: Message
}

// Detect ```lang\ncode\n``` blocks in content
function parseContent(content: string): Array<{ type: "text" | "code"; value: string; lang?: string }> {
  const parts: Array<{ type: "text" | "code"; value: string; lang?: string }> = []
  const codeBlockRegex = /```(\w+)?\n?([\s\S]*?)```/g
  let lastIndex = 0
  let match

  while ((match = codeBlockRegex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: "text", value: content.slice(lastIndex, match.index) })
    }
    parts.push({ type: "code", lang: match[1] || "python", value: match[2].trim() })
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < content.length) {
    parts.push({ type: "text", value: content.slice(lastIndex) })
  }

  return parts
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user"
  const parts = parseContent(message.content)

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} fade-in`}
    >
      <div
        className="max-w-[85%] rounded-lg overflow-hidden"
        style={{
          border: isUser ? "1px solid var(--accent-blue)33" : "1px solid var(--border)",
          backgroundColor: isUser ? "rgba(88,166,255,0.08)" : "var(--bg-surface)",
          borderLeft: !isUser ? "3px solid var(--accent-blue)" : undefined,
        }}
      >
        {/* Role label */}
        <div
          className="px-3 py-1.5 text-xs font-mono border-b"
          style={{
            color: isUser ? "var(--accent-blue)" : "var(--text-muted)",
            borderColor: "var(--border)",
            backgroundColor: "var(--bg-elevated)",
          }}
        >
          {isUser ? "you" : "agent"}
        </div>

        {/* Content */}
        <div className="px-3 py-2.5">
          {parts.map((part, i) =>
            part.type === "code" ? (
              <CodeBlock key={i} code={part.value} language={part.lang} />
            ) : (
              <p
                key={i}
                className="text-sm leading-relaxed whitespace-pre-wrap"
                style={{ color: "var(--text-primary)" }}
              >
                {part.value}
              </p>
            )
          )}
        </div>
      </div>
    </div>
  )
}
