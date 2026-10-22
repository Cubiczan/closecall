"""Minimal MCP Streamable-HTTP client (stdlib)."""
import json, urllib.request
from . import PROTOCOL_VERSION

class MCPClient:
    def __init__(self, url):
        self.url, self.sid, self.n = url, None, 0
    def _post(self, msg):
        h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.sid: h["Mcp-Session-Id"] = self.sid; h["MCP-Protocol-Version"] = PROTOCOL_VERSION
        req = urllib.request.Request(self.url, json.dumps(msg).encode(), h)
        with urllib.request.urlopen(req, timeout=10) as r:
            self.sid = r.headers.get("Mcp-Session-Id") or self.sid
            raw = r.read()
            return json.loads(raw) if raw else None
    def rpc(self, method, params=None):
        self.n += 1
        out = self._post({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}})
        if "error" in out: raise RuntimeError(out["error"])
        return out["result"]
    def connect(self):
        r = self.rpc("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                    "clientInfo": {"name": "alexa-plus-sim", "version": "0.1"}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return r
    def list_tools(self): return self.rpc("tools/list")["tools"]
    def call(self, name, args=None): return self.rpc("tools/call", {"name": name, "arguments": args or {}})
