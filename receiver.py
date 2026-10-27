"""Local receiver: CI report POST karta hai, yeh test-report.json save karta hai."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

OUTPUT_FILE = "test-report.json"


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            report = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"invalid json")
            return

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Report received: {report.get('overall_status')} "
              f"({report.get('commit_sha', '')[:7]}) -> {OUTPUT_FILE}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"saved")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"receiver running")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Receiver listening on http://localhost:8000/report")
    server.serve_forever()