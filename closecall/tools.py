"""MCP tools. Every tool returns {content:[text], structuredContent, isError}."""
from . import ledger as L

def _ok(text, data):
    return {"content": [{"type": "text", "text": text}], "structuredContent": data, "isError": False}

def _err(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}

def _money(n):
    return f"${n:,.0f}"

def close_status(args):
    open_ = [t for t in L.TASKS if t["status"] != "done"]
    done = len(L.TASKS) - len(open_)
    speech = f"The {L.PERIOD} close is {done} of {len(L.TASKS)} tasks done. " + " ".join(
        f"{t['name']} is blocked: {t['blocker']}, owner {t['owner']}." for t in open_)
    return _ok(speech, {"period": L.PERIOD, "done": done, "total": len(L.TASKS), "open": open_})

def variance_explain(args):
    acct = (args.get("account") or "").strip().title()
    if acct not in L.PNL:
        return _err(f"Unknown account '{acct}'. Try one of: {', '.join(L.PNL)}")
    a, b, p = L.PNL[acct]
    dv, pct = a - b, (a - b) / b * 100
    drivers = L.DRIVERS.get(acct, [])
    speech = (f"{acct} came in at {_money(a)}, {_money(abs(dv))} {'over' if dv>0 else 'under'} budget, "
              f"{abs(pct):.0f} percent. Main drivers: " + "; ".join(drivers) + ".")
    return _ok(speech, {"account": acct, "actual": a, "budget": b, "prior": p, "variance": dv,
                        "variance_pct": round(pct, 1), "drivers": drivers})

def top_variances(args):
    n = int(args.get("limit", 3))
    rows = sorted(((k, a - b, (a - b) / b * 100) for k, (a, b, _) in L.PNL.items()), key=lambda r: -abs(r[2]))[:n]
    speech = "Biggest variances vs budget: " + "; ".join(f"{k} {'+' if d>0 else '-'}{abs(p):.0f}% ({_money(abs(d))})" for k, d, p in rows) + "."
    return _ok(speech, {"rows": [{"account": k, "variance": d, "variance_pct": round(p, 1)} for k, d, p in rows]})

def accrual_propose(args):
    try:
        amount = float(args["amount"])
    except (KeyError, ValueError, TypeError):
        return _err("amount is required")
    acct = (args.get("account") or "Freight").title()
    memo = args.get("memo") or f"{L.PERIOD} {acct.lower()} accrual"
    if amount <= L.POLICY["auto_approve_limit"]:
        state = "posted"
    elif amount <= L.POLICY["cfo_approval_limit"]:
        state = "pending_cfo_approval"
    else:
        state = "denied_over_limit"
    entry = L.append_journal({"type": "accrual", "account": acct, "amount": amount, "memo": memo, "state": state})
    speech = {
        "posted": f"Posted a {_money(amount)} {acct} accrual under the auto-approve limit.",
        "pending_cfo_approval": f"Drafted a {_money(amount)} {acct} accrual. It is over {_money(L.POLICY['auto_approve_limit'])}, so it is waiting for CFO approval.",
        "denied_over_limit": f"I can't book {_money(amount)}. That is above the {_money(L.POLICY['cfo_approval_limit'])} policy ceiling; it needs the controller's manual entry.",
    }[state]
    return _ok(speech, {"entry": entry})

def approve(args):
    h = args.get("hash")
    for e in L._JOURNAL:
        if e["hash"] == h and e["state"] == "pending_cfo_approval":
            e["state"] = "posted"
            L.append_journal({"type": "approval", "ref": h, "state": "approved", "by": args.get("by", "CFO")})
            return _ok(f"Approved and posted entry {h}.", {"ref": h, "state": "posted"})
    return _err(f"No pending entry {h}.")

def cash_runway(args):
    c = L.CASH
    net30 = c["balance"] + c["ar_due_30d"] - c["ap_due_30d"]
    months = c["balance"] / c["monthly_burn"]
    speech = (f"Cash is {_money(c['balance'])}, about {months:.1f} months of runway at the current burn. "
              f"After 30 days of collections and payables you land near {_money(net30)}.")
    return _ok(speech, {**c, "runway_months": round(months, 1), "projected_30d": net30})

def audit_trail(args):
    j = L.journal()
    return _ok(f"{len(j)} journal entries this session.", {"entries": j})

def _schema(props, req=()):
    return {"type": "object", "properties": props, "required": list(req), "additionalProperties": False}

TOOLS = {
    "close_status": (close_status, "What is still open or blocked in this month's close.", _schema({}), True),
    "top_variances": (top_variances, "Largest P&L variances vs budget.", _schema({"limit": {"type": "integer", "minimum": 1, "maximum": 6}}), True),
    "variance_explain": (variance_explain, "Explain one account's variance vs budget with drivers.", _schema({"account": {"type": "string", "enum": list(L.PNL)}}, ["account"]), True),
    "accrual_propose": (accrual_propose, "Propose an accrual. Policy decides post / hold for CFO / deny.", _schema({"amount": {"type": "number"}, "account": {"type": "string"}, "memo": {"type": "string"}}, ["amount"]), False),
    "approve_entry": (approve, "CFO approves a pending journal entry by hash.", _schema({"hash": {"type": "string"}, "by": {"type": "string"}}, ["hash"]), False),
    "cash_runway": (cash_runway, "Cash balance, runway, and 30-day projection.", _schema({}), True),
    "audit_trail": (audit_trail, "Hash-linked journal of every action this session.", _schema({}), True),
}

def list_tools():
    return [{"name": n, "title": n.replace("_", " ").title(), "description": d, "inputSchema": s,
             "annotations": {"readOnlyHint": ro, "destructiveHint": False}} for n, (_, d, s, ro) in TOOLS.items()]

def call_tool(name, args):
    if name not in TOOLS:
        return None
    return TOOLS[name][0](args or {})
