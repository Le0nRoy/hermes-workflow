"""Local, synthetic API fixture. No persistence or external services."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

VARIANTS = ("clean", "api-zero", "api-bool", "api-duplicate")


def make_server(variant="clean"):
    if variant not in VARIANTS:
        raise ValueError(variant)
    orders = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if urlsplit(self.path).path != "/orders":
                return self.reply(404, {"error": "not_found"})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            except (ValueError, UnicodeDecodeError):
                return self.reply(400, {"error": "invalid_json"})
            if not isinstance(body, dict):
                return self.reply(422, {"error": "invalid_order"})
            key, quantity = body.get("id"), body.get("quantity")
            integer = isinstance(quantity, int) if variant == "api-bool" else type(quantity) is int
            lower = 0 if variant == "api-zero" else 1
            if not isinstance(key, str) or not key.strip() or not integer or not lower <= quantity <= 10:
                return self.reply(422, {"error": "invalid_order"})
            if key in orders and variant != "api-duplicate":
                return self.reply(409, {"error": "duplicate"})
            orders[key] = {"id": key, "quantity": quantity}
            return self.reply(201, orders[key])

        def do_GET(self):
            path = urlsplit(self.path).path
            key = path.removeprefix("/orders/")
            if path.startswith("/orders/") and key in orders:
                return self.reply(200, orders[key])
            return self.reply(404, {"error": "not_found"})

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=VARIANTS, default="clean")
    args = parser.parse_args()
    with make_server(args.variant) as server:
        print(f"http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
