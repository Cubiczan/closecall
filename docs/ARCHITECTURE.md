# Architecture

```
 Voice / text (Web Speech API)          Alexa+ simulator (web/index.html)
            │  utterance                           ▲ speech + cards + tool trail
            ▼                                      │
   POST /api/say ──► Host (closecall/host.py) ─────┘
                     │  planner: Amazon Bedrock Converse tool-use (CLOSECALL_PLANNER=bedrock)
                     │           or deterministic intent router (offline)
                     ▼
              MCPClient (closecall/client.py)  — JSON-RPC 2.0 over Streamable HTTP
                     │  initialize → notifications/initialized → tools/call …
                     ▼   Mcp-Session-Id + MCP-Protocol-Version: 2025-11-25
   POST /mcp ──► MCP server (closecall/server.py)
                     │  tools/list · tools/call · resources/* · prompts/* · ping
                     ▼
              Tools (closecall/tools.py) ──► policy gate ──► hash-linked journal (closecall/ledger.py)
```

* The same `/mcp` endpoint can be pointed at by Alexa+ or any MCP host; the web simulator is just one client.
* Origin header is validated (DNS-rebinding guard per spec); unknown sessions get 404; notifications get 202; GET /mcp returns 405 (no server-initiated stream).
* Write tools carry `readOnlyHint: false` annotations. Policy limits live in `closecall://policy`.
