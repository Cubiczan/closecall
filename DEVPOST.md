# Devpost fields — CloseCall

**Project name:** CloseCall
**Tagline:** Run the month-end close by voice — an Alexa+ MCP server that lets a CFO ask what's blocked, why numbers moved, and approve accruals under policy.

**Inspiration:** Close week at a mid-size company is a week of spreadsheets and status pings: who's blocked, why is freight over, can I book this accrual. CFOs ask those questions out loud all day. Alexa+ plus MCP finally makes it possible to answer them by voice — if the agent has hard guardrails on anything that writes to the books.

**What it does:** CloseCall is a self-hosted MCP server (spec 2025-11-25, Streamable HTTP) with seven tools: close_status, top_variances, variance_explain, cash_runway, accrual_propose, approve_entry and audit_trail, plus policy and checklist resources and a morning-briefing prompt. A web console simulates the Alexa+ experience (mic or text in, spoken answer and cards out) and is a real MCP client of the same endpoint. Accruals of $5k or less auto-post, accruals up to $50k wait for CFO approval ("Approve it" works across turns), and anything larger is refused. Every write goes to a hash-linked audit trail.

**How we built it:** Python stdlib only, so it runs with zero dependencies or keys. server.py implements JSON-RPC 2.0 over Streamable HTTP: initialize/version negotiation, Mcp-Session-Id sessions, the MCP-Protocol-Version header, 202 for notifications, 404 for unknown sessions, 405 on GET, and an Origin check. client.py is a minimal MCP client. host.py plans each utterance either through Amazon Bedrock Converse tool use (CLOSECALL_PLANNER=bedrock, with MCP inputSchemas passed straight in as Bedrock toolSpecs) or through a deterministic intent router offline. Integration tests start the server and exercise the full approve/deny flow.

**Challenges we ran into:** There's no self-serve way to register a self-hosted MCP URL with a real Alexa+ host, so we built the simulator as a true MCP client rather than a mock. AWS credit codes ran out on Oct 7, so the Bedrock planner is optional and the UI labels which planner answered. Keeping the model out of spend decisions meant putting the policy inside the tool, not the prompt.

**Accomplishments that we're proud of:** It's a spec-conformant MCP server with no dependencies. Policy enforcement is deterministic and can be audited. The approval state carries across turns ("Approve it"), and a voice UX can be demoed end to end in two minutes.

**What we learned:** MCP tool schemas map almost 1:1 onto Bedrock Converse toolSpecs. Voice answers need to be one or two sentences, with the detail moved to cards. The most important design choice for finance agents is which tools are allowed to write.

**What's next for CloseCall:** Connectors for NetSuite, QuickBooks and Xero; OAuth on the MCP endpoint; registering with Alexa+ when hosting opens up; AgentCore deployment; and multi-approver workflows (controller plus CFO).

**Built with:** python, model-context-protocol, alexa-plus, amazon-bedrock, amazon-nova, json-rpc, web-speech-api, html, javascript

**Track:** Alexa+ · **Mini challenge:** AWS Builder
**Repo:** https://github.com/icohangar-ops/closecall (public, MIT)

## Product feedback
- **Tools used:** MCP spec 2025-11-25 (server transport and session handling), the Alexa+ simulated-experience path (web console), Amazon Bedrock Converse API with tool use (planner, optional), and the Web Speech API.
- **What worked well:** The MCP spec is clear on JSON-RPC shapes and Streamable HTTP. Converse toolConfig accepts MCP JSON Schemas with no translation layer.
- **What needs work:** There's no Alexa+ sandbox host for registering a self-hosted MCP URL, and no conformance test harness. AWS credit codes ran out on Oct 7 even though the form stayed open until Oct 21.
- **Onboarding:** From zero to an MCP hello world took about 30 minutes using the spec. Getting a real Alexa+ device test wasn't possible.
- **Build again?** Yes. Voice is a natural interface for executives, and MCP makes the back end portable across Alexa+ and other hosts.

**Friction log:** see FRICTION.md (4 entries).
**Significant update note:** This is a new project, created Oct 21, 2026, during the submission period.
