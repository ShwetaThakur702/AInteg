import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import HeaderNav from "@/components/HeaderNav"

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter",
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
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen font-sans" style={{ backgroundColor: "var(--bg-base)", color: "var(--text-primary)" }}>
        <HeaderNav />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  )
}
