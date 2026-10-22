"""Self-hosted MCP server (spec 2025-11-25, Streamable HTTP) + Alexa+ simulator host.

POST /mcp      JSON-RPC 2.0 MCP endpoint (initialize, tools/*, resources/*, prompts/*, ping)
GET  /mcp      405 (no server-initiated SSE stream; allowed by the spec)
DELETE /mcp    end session
POST /api/say  Alexa+ simulator: utterance -> planner -> MCP client -> spoken reply + card
GET  /         web console
"""
import json, os, uuid, pathlib
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from . import PROTOCOL_VERSION, tools, ledger
from .host import Host

WEB = pathlib.Path(__file__).resolve().parent.parent / "web"
SESSIONS = set()
SERVER_INFO = {"name": "closecall", "title": "CloseCall month-end close", "version": "0.1.0"}

RESOURCES = [{"uri": "closecall://policy", "name": "policy", "mimeType": "application/json", "description": "Spend / accrual approval policy"},
             {"uri": "closecall://close-checklist", "name": "close-checklist", "mimeType": "application/json", "description": "October close checklist"}]
PROMPTS = [{"name": "morning_close_briefing", "description": "Daily close stand-up for the CFO"}]

def handle_rpc(msg, session):
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    def res(r): return {"jsonrpc": "2.0", "id": mid, "result": r}
    def err(c, m): return {"jsonrpc": "2.0", "id": mid, "error": {"code": c, "message": m}}
    if method == "initialize":
        return res({"protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}, "resources": {}, "prompts": {}},
                    "serverInfo": SERVER_INFO,
                    "instructions": "Voice-first month-end close assistant. Write tools are policy-gated."})
    if mid is None:  # notifications (e.g. notifications/initialized)
        return None
    if method == "ping": return res({})
    if method == "tools/list": return res({"tools": tools.list_tools()})
    if method == "tools/call":
        out = tools.call_tool(params.get("name"), params.get("arguments"))
        return err(-32602, f"Unknown tool {params.get('name')}") if out is None else res(out)
    if method == "resources/list": return res({"resources": RESOURCES})
    if method == "resources/read":
        uri = params.get("uri")
        data = {"closecall://policy": ledger.POLICY, "closecall://close-checklist": ledger.TASKS}.get(uri)
        if data is None: return err(-32002, "Resource not found")
        return res({"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(data)}]})
    if method == "prompts/list": return res({"prompts": PROMPTS})
    if method == "prompts/get":
        return res({"messages": [{"role": "user", "content": {"type": "text", "text": "Give me the close status, top variances and cash runway."}}]})
    return err(-32601, f"Method not found: {method}")

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body=b"", ctype="application/json", headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for k, v in (headers or {}).items(): self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def _json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")
    def do_GET(self):
        if self.path == "/mcp": return self._send(405, b"", headers={"Allow": "POST, DELETE"})
        f = WEB / ("index.html" if self.path in ("/", "") else self.path.lstrip("/"))
        if f.is_file() and WEB in f.resolve().parents:
            return self._send(200, f.read_bytes(), "text/html" if f.suffix == ".html" else "text/plain")
        self._send(404, b"not found", "text/plain")
    def do_DELETE(self):
        SESSIONS.discard(self.headers.get("Mcp-Session-Id")); self._send(200)
    def do_POST(self):
        if self.path == "/mcp":
            origin = self.headers.get("Origin")
            if origin and not origin.startswith(("http://localhost", "http://127.0.0.1")):
                return self._send(403, b'{"error":"origin not allowed"}')
            try: msg = self._json()
            except Exception: return self._send(400, json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}).encode())
            sid = self.headers.get("Mcp-Session-Id")
            hdrs = {"MCP-Protocol-Version": PROTOCOL_VERSION}
            if msg.get("method") == "initialize":
                sid = uuid.uuid4().hex; SESSIONS.add(sid); hdrs["Mcp-Session-Id"] = sid
            elif sid not in SESSIONS:
                return self._send(404, b'{"error":"unknown session"}')
            out = handle_rpc(msg, sid)
            if out is None: return self._send(202, b"", headers=hdrs)
            return self._send(200, json.dumps(out).encode(), headers=hdrs)
        if self.path == "/api/say":
            body = self._json()
            return self._send(200, json.dumps(HOST.say(body.get("utterance", ""))).encode())
        if self.path == "/api/reset":
            ledger.reset(); return self._send(200, b"{}")
        self._send(404, b"{}")

HOST = None

def main():
    global HOST
    port = int(os.environ.get("PORT", 8787))
    HOST = Host(f"http://127.0.0.1:{port}/mcp")
    srv = ThreadingHTTPServer(("0.0.0.0", port), H)
    print(f"CloseCall MCP server on http://localhost:{port}/mcp  (protocol {PROTOCOL_VERSION})  console: http://localhost:{port}/", flush=True)
    srv.serve_forever()

if __name__ == "__main__":
    main()
