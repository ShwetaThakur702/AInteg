import type { Metadata } from "next"
import { IBM_Plex_Sans, JetBrains_Mono } from "next/font/google"
import "./globals.css"

const ibmPlexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-plex-sans",
  display: "swap",
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-jetbrains-mono",
  display: "swap",
})

export const metadata: Metadata = {
  title: "API Integration Agent",
  description: "Upload an OpenAPI spec and generate Python client code automatically",
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${ibmPlexSans.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen font-sans" style={{ backgroundColor: "var(--bg-base)", color: "var(--text-primary)" }}>

        {/* Nav */}
        <header
          className="border-b flex items-center justify-between px-6 py-3"
          style={{
            borderColor: "var(--border)",
            backgroundColor: "#ffffff",
            boxShadow: "0 1px 0 var(--border)",
          }}
        >
          <div className="flex items-center gap-3">
            {/* Logo pill */}
            <div
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
              style={{ backgroundColor: "var(--bg-elevated)", border: "1px solid var(--border)" }}
            >
              <span style={{ color: "var(--accent-blue)", fontSize: "16px" }}>⬡</span>
              <span className="font-mono text-sm font-bold" style={{ color: "var(--text-primary)" }}>
                API Integration Agent
              </span>
            </div>
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

          <div className="flex items-center gap-2">
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
          </div>
        </header>

        <main className="flex-1">{children}</main>
      </body>
    </html>
  )
}
