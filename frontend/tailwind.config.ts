import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "bg-base":       "#ffffff",
        "bg-surface":    "#faf6ff",
        "bg-elevated":   "#f1e9ff",
        border:          "#ddd0f8",
        "accent-blue":   "#7c3aed",
        "accent-purple": "#9333ea",
        "accent-green":  "#16a34a",
        "accent-red":    "#dc2626",
        "accent-orange": "#ea580c",
        "text-primary":  "#1e0a3c",
        "text-muted":    "#7c6d9a",
        "text-code":     "#7c3aed",
      },
      fontFamily: {
        sans: ["var(--font-ibm-plex-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      animation: {
        spin: "spin 1s linear infinite",
        "pulse-slow": "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
}

export default config
