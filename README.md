# CloseCall — a voice-first month-end close agent for Alexa+

**Track:** Alexa+ (self-hosted MCP server, spec **2025-11-25**, Streamable HTTP) · **Mini challenge:** AWS Builder (Amazon Bedrock Converse tool-use planner)

"Alexa, what's blocking the October close?" CloseCall lets a CFO or controller run the month-end close by voice: hear what's blocked and who owns it, ask why an account is over budget, book an accrual, and approve it — with a spend policy that decides what can be auto-posted, what waits for the CFO, and what is refused. Every write lands in a hash-linked audit trail.

The demo company, **Harbor & Pine Outfitters**, is a fictional fixture seeded in `closecall/ledger.py`. Nothing touches a real ledger or moves money.

## Run it (no keys needed)

```bash
git clone https://github.com/icohangar-ops/closecall && cd closecall
python3 -m closecall.server          # Python 3.10+, stdlib only
# MCP endpoint: http://localhost:8787/mcp     Alexa+ simulator: http://localhost:8787/
python3 -m unittest tests/test_mcp.py
```

Optional Bedrock planner (AWS Builder mini challenge):

```bash
pip install boto3
export AWS_REGION=us-east-1 CLOSECALL_PLANNER=bedrock BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
# credentials via your normal AWS profile / env; never commit them
python3 -m closecall.server
```

Without credentials the host falls back to a deterministic intent router and shows `planner: rules (bedrock unavailable …)` in the tool trail.

## Connect any MCP client

```bash
curl -si -X POST localhost:8787/mcp -H 'Content-Type: application/json' \
 -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"me","version":"1"}}}'
# reuse the returned Mcp-Session-Id header on later calls
```

## Tools

| Tool | Kind | What it does |
|---|---|---|
| `close_status` | read | Checklist progress, blockers, owners |
| `top_variances` | read | Largest P&L variances vs budget |
| `variance_explain` | read | One account's variance with drivers |
| `cash_runway` | read | Balance, runway, 30-day projection |
| `accrual_propose` | write | ≤ $5k auto-posts; ≤ $50k waits for CFO; above is denied |
| `approve_entry` | write | CFO approves a pending entry by hash |
| `audit_trail` | read | Hash-linked journal of every action |

Resources: `closecall://policy`, `closecall://close-checklist`. Prompt: `morning_close_briefing`.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md), [FRICTION.md](FRICTION.md).

## License
MIT
