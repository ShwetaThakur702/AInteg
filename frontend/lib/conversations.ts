export interface ConversationEntry {
  jobId: string
  label: string        // e.g. "petstore3.swagger.io" from base_url
  source: string       // original filename or URL
  timestamp: number    // Date.now()
  endpointCount: number
  authType: string
}

const KEY = "aia_convos"
const MAX = 5

export function saveConversation(entry: ConversationEntry): void {
  if (typeof window === "undefined") return
  const prev = getConversations().filter((e) => e.jobId !== entry.jobId)
  localStorage.setItem(KEY, JSON.stringify([entry, ...prev].slice(0, MAX)))
}

export function getConversations(): ConversationEntry[] {
  if (typeof window === "undefined") return []
  try { return JSON.parse(localStorage.getItem(KEY) ?? "[]") }
  catch { return [] }
}
