"""Alexa+ simulator host: utterance -> plan -> MCP tools/call -> speech.

Planner: Amazon Bedrock Converse with tool use when CLOSECALL_PLANNER=bedrock and AWS
credentials are present; otherwise a deterministic intent router so the demo runs offline.
"""
import os, re
from .client import MCPClient

def rule_plan(u: str, last_pending=None):
    u = u.lower()
    m = re.search(r"\$?\s*([\d,]+(?:\.\d+)?)\s*(k\b)?", u)
    amt = (float(m.group(1).replace(",", "")) * (1000 if m.group(2) else 1)) if m else None
    if "approve" in u and last_pending: return [("approve_entry", {"hash": last_pending, "by": "CFO"})]
    if "accru" in u or "book" in u:
        acct = next((a for a in ["Freight", "Software", "Marketing", "Payroll", "Cogs"] if a.lower() in u), "Freight")
        return [("accrual_propose", {"amount": amt or 0, "account": acct})]
    for a in ["freight", "cogs", "software", "marketing", "payroll", "revenue"]:
        if a in u and ("why" in u or "explain" in u or "variance" in u or "over" in u):
            return [("variance_explain", {"account": "COGS" if a == "cogs" else a.title()})]
    if "variance" in u or "over budget" in u: return [("top_variances", {"limit": 3})]
    if "cash" in u or "runway" in u: return [("cash_runway", {})]
    if "audit" in u or "journal" in u: return [("audit_trail", {})]
    if "brief" in u or "morning" in u: return [("close_status", {}), ("top_variances", {"limit": 3}), ("cash_runway", {})]
    return [("close_status", {})]

def bedrock_plan(u, tools):
    import boto3
    br = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    model = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
    spec = [{"toolSpec": {"name": t["name"], "description": t["description"], "inputSchema": {"json": t["inputSchema"]}}} for t in tools]
    r = br.converse(modelId=model, messages=[{"role": "user", "content": [{"text": u}]}],
                    system=[{"text": "You are a CFO's voice assistant for month-end close. Call the tools needed."}],
                    toolConfig={"tools": spec})
    return [(c["toolUse"]["name"], c["toolUse"]["input"]) for c in r["output"]["message"]["content"] if "toolUse" in c]

class Host:
    def __init__(self, url):
        self.url, self.client, self.pending = url, None, None
    def _c(self):
        if not self.client:
            self.client = MCPClient(self.url); self.client.connect()
        return self.client
    def say(self, utterance):
        c = self._c()
        planner = "rules"
        plan = None
        if os.environ.get("CLOSECALL_PLANNER") == "bedrock":
            try: plan, planner = bedrock_plan(utterance, c.list_tools()), "bedrock"
            except Exception as e: planner = f"rules (bedrock unavailable: {type(e).__name__})"
        plan = plan or rule_plan(utterance, self.pending)
        trail, speech, cards = [], [], []
        for name, args in plan:
            out = c.call(name, args)
            trail.append({"tool": name, "args": args, "isError": out.get("isError", False)})
            speech.append(out["content"][0]["text"])
            sc = out.get("structuredContent") or {}
            cards.append({"tool": name, "data": sc})
            e = sc.get("entry")
            if e and e.get("state") == "pending_cfo_approval": self.pending = e["hash"]
            if name == "approve_entry" and not out.get("isError"): self.pending = None
        return {"utterance": utterance, "speech": " ".join(speech), "trail": trail, "cards": cards,
                "planner": planner, "session": c.sid}
