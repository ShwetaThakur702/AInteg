// lib/mcp_client.ts
// Phase 2: MCP tool definitions for the debug chat
// LLM calls these tools to fetch exactly the context it needs

import type { SessionMemory } from "./memory"

export interface McpTool {
  name: string
  description: string
  handler: (args: Record<string, unknown>, memory: SessionMemory) => unknown
}

export const MCP_TOOLS: McpTool[] = [
  {
    name: "get_endpoint_info",
    description: "Get spec details for a specific API endpoint",
    handler: ({ method, path }, memory) =>
      memory.specSummary.endpoints.find(
        (e) => e.method.toUpperCase() === String(method).toUpperCase() && e.path === path
      ) ?? null,
  },
  {
    name: "get_auth_config",
    description: "Get authentication type and location for this API",
    handler: (_args, memory) => ({
      auth_type: memory.specSummary.auth_type,
      auth_location: memory.specSummary.auth_location,
    }),
  },
  {
    name: "get_code_snippet",
    description: "Get generated stub / example / test for a specific endpoint",
    handler: ({ method, path, type }, memory) => {
      const key = `${String(method).toUpperCase()} ${path}`
      const snippets = memory.codeSnippets[key]
      if (!snippets) return null
      return snippets[type as keyof typeof snippets] ?? null
    },
  },
  {
    name: "get_common_errors",
    description: "Get documented error codes from the spec",
    handler: (_args, memory) => memory.specSummary.common_error_codes,
  },
  {
    name: "get_chat_history",
    description: "Get recent conversation turns for context",
    handler: ({ last_n }, memory) =>
      memory.chatHistory.slice(-(Number(last_n) || 10)),
  },
]

export function callTool(
  toolName: string,
  args: Record<string, unknown>,
  memory: SessionMemory
): unknown {
  const tool = MCP_TOOLS.find((t) => t.name === toolName)
  if (!tool) throw new Error(`Unknown MCP tool: ${toolName}`)
  return tool.handler(args, memory)
}
