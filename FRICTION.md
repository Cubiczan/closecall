# Friction log

| # | Task | Steps | Expected | Actual | Severity | Workaround | Suggestion |
|---|---|---|---|---|---|---|---|
| 1 | Find the minimum MCP spec for Alexa+ | Read rules + modelcontextprotocol.io | One page listing the Alexa+-specific transport/auth expectations | Had to infer from the generic spec that Streamable HTTP + session header is what's expected | Medium | Implemented spec 2025-11-25 Streamable HTTP with session + protocol headers | Publish an "Alexa+ MCP conformance checklist" with a test harness |
| 2 | Test against a real Alexa+ host | Looked for a developer console to register a self-hosted MCP URL | Register URL, talk to Echo | No self-serve registration path found during the hackathon | High | Built a web simulator that is a real MCP client of the same endpoint | Offer a sandbox Alexa+ host that accepts an MCP URL |
| 3 | Bedrock as planner | Converse API with toolConfig | Tool schema reused 1:1 from MCP `inputSchema` | Could not run live: no AWS credentials on the build box once credit codes ran out | Medium | Planner code path implemented; falls back to rules and labels it in the UI | Provide a hosted Bedrock sandbox key for hackathon entrants |
| 4 | AWS credits | Requested via form | Code available until Oct 21 | Codes ran out Oct 7 | Low | Planner runs offline by default | Announce remaining supply on the resources page |
