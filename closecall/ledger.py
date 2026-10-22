"""Seeded books for a demo company (fictional: Harbor & Pine Outfitters)."""
import hashlib, json, time

COMPANY = "Harbor & Pine Outfitters (demo fixture)"
PERIOD = "2026-10"

TASKS = [
    {"id": "T1", "name": "Bank reconciliation - operating", "owner": "Priya", "status": "done"},
    {"id": "T2", "name": "Bank reconciliation - payroll", "owner": "Priya", "status": "open", "blocker": "Missing statement page 3 from First Coastal"},
    {"id": "T3", "name": "AP cutoff review", "owner": "Marcus", "status": "open", "blocker": "Three invoices received after Oct 31 not yet coded"},
    {"id": "T4", "name": "Revenue recognition - wholesale", "owner": "Dana", "status": "done"},
    {"id": "T5", "name": "Freight accrual", "owner": "Marcus", "status": "open", "blocker": "Carrier invoice not received"},
    {"id": "T6", "name": "Fixed asset depreciation run", "owner": "Dana", "status": "done"},
]

# account: (actual, budget, prior)
PNL = {
    "Revenue":            (1_284_000, 1_250_000, 1_190_000),
    "COGS":               (  742_000,   700_000,   680_000),
    "Freight":            (   61_500,    42_000,    40_100),
    "Payroll":            (  238_000,   240_000,   236_500),
    "Software":           (   18_900,    15_000,    14_800),
    "Marketing":          (   44_000,    55_000,    51_200),
}

DRIVERS = {
    "Freight": ["Expedited air on the Lakeview order (+$11.2k)", "Fuel surcharge up 9% vs September", "Carrier invoice for week 4 still accrued at estimate"],
    "COGS": ["Wholesale mix shift toward lower-margin bundles", "Cotton input cost +4%"],
    "Software": ["Annual analytics renewal billed in October instead of amortized"],
    "Marketing": ["Paused paid social for two weeks"],
    "Revenue": ["Lakeview wholesale order shipped early"],
    "Payroll": ["Within 1% of plan"],
}

CASH = {"balance": 912_000, "monthly_burn": 148_000, "ar_due_30d": 410_000, "ap_due_30d": 365_000}

POLICY = {"auto_approve_limit": 5_000, "cfo_approval_limit": 50_000}

_JOURNAL = []

def journal():
    return list(_JOURNAL)

def append_journal(entry: dict) -> dict:
    prev = _JOURNAL[-1]["hash"] if _JOURNAL else "0" * 16
    body = {**entry, "prev": prev, "ts": int(time.time())}
    body["hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]
    _JOURNAL.append(body)
    return body

def reset():
    _JOURNAL.clear()
