# Demo script (≈2:15)
1. Terminal: start server, `initialize` returns protocol 2025-11-25 + Mcp-Session-Id; `tools/list`; tests pass.
2. Console: "Give me my morning close briefing" → close_status + top_variances + cash_runway.
3. "Why is freight over budget?" → variance_explain with drivers.
4. "Accrue $3,200 for freight" → auto-posted under $5k.
5. "Book a $18,400 freight accrual…" → held for CFO. "Approve it" → posted.
6. "Book a $90,000 freight accrual" → denied by policy.
7. "Show the audit trail" → hash-linked entries.
