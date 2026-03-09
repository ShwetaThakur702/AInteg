import SpecUploader from "@/components/SpecUploader"

export default function HomePage() {
  return (
    <div
      className="min-h-[calc(100vh-57px)] flex flex-col items-center justify-center px-4 py-16"
      style={{ backgroundColor: "var(--bg-base)" }}
    >
      {/* Hero */}
      <div className="text-center mb-10 max-w-lg">
        <div
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono font-medium mb-5"
          style={{
            backgroundColor: "var(--bg-elevated)",
            border: "1px solid var(--border)",
            color: "var(--accent-purple)",
          }}
        >
          <span
            className="w-2 h-2 rounded-full inline-block"
            style={{ backgroundColor: "var(--accent-green)" }}
          />
          4-chain LangChain pipeline · OpenRouter gpt-4o-mini
        </div>

        <h1
          className="text-4xl font-bold mb-4 leading-tight"
          style={{ color: "var(--text-primary)" }}
        >
          API Integration{" "}
          <span style={{ color: "var(--accent-blue)" }}>Agent</span>
        </h1>

        <p className="text-base leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Upload an OpenAPI / Swagger spec and automatically generate a Python
          httpx client, usage examples, and contract tests.
        </p>
      </div>

      {/* Uploader card */}
      <div
        className="w-full max-w-xl rounded-2xl p-6"
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border)",
          boxShadow: "var(--shadow-lg)",
        }}
      >
        <SpecUploader />
      </div>

      {/* What gets generated */}
      <div className="mt-10 grid grid-cols-3 gap-4 max-w-xl w-full">
        {[
          {
            icon: "🔌",
            title: "client_stubs.py",
            desc: "httpx client with auth and retry",
            color: "var(--accent-blue)",
          },
          {
            icon: "📖",
            title: "usage_examples.py",
            desc: "Ready-to-run examples per endpoint",
            color: "var(--accent-purple)",
          },
          {
            icon: "🧪",
            title: "contract_tests.py",
            desc: "pytest + Pydantic schema validation",
            color: "var(--accent-green)",
          },
        ].map((item) => (
          <div
            key={item.title}
            className="rounded-xl px-4 py-4 flex flex-col gap-2 transition-all"
            style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border)",
              boxShadow: "var(--shadow-sm)",
            }}
          >
            <span className="text-2xl">{item.icon}</span>
            <span className="font-mono text-xs font-bold" style={{ color: item.color }}>
              {item.title}
            </span>
            <span className="text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
              {item.desc}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
