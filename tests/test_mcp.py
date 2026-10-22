import os, subprocess, sys, time, unittest, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from closecall.client import MCPClient

PORT = 8799
class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen([sys.executable, "-m", "closecall.server"], env={**os.environ, "PORT": str(PORT)},
                                 cwd=os.path.dirname(os.path.dirname(__file__)))
        time.sleep(1.2)
    @classmethod
    def tearDownClass(cls): cls.p.terminate()
    def test_flow(self):
        c = MCPClient(f"http://127.0.0.1:{PORT}/mcp")
        init = c.connect()
        self.assertEqual(init["protocolVersion"], "2025-11-25")
        names = {t["name"] for t in c.list_tools()}
        self.assertIn("accrual_propose", names)
        self.assertEqual(c.call("accrual_propose", {"amount": 3200})["structuredContent"]["entry"]["state"], "posted")
        e = c.call("accrual_propose", {"amount": 18400})["structuredContent"]["entry"]
        self.assertEqual(e["state"], "pending_cfo_approval")
        self.assertFalse(c.call("approve_entry", {"hash": e["hash"]})["isError"])
        self.assertEqual(c.call("accrual_propose", {"amount": 90000})["structuredContent"]["entry"]["state"], "denied_over_limit")
    def test_no_session_rejected(self):
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/mcp", json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/list"}).encode(), {"Content-Type":"application/json"})
        with self.assertRaises(urllib.error.HTTPError) as cm: urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 404)
    def test_say(self):
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/say", json.dumps({"utterance": "why is freight over budget?"}).encode(), {"Content-Type":"application/json"})
        r = json.loads(urllib.request.urlopen(req).read())
        self.assertEqual(r["trail"][0]["tool"], "variance_explain")
if __name__ == "__main__": unittest.main()
