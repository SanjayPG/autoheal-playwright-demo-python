"""
Lightweight proxy that translates Ollama API format to a simple /chat API.

This allows the autoheal library's LOCAL_MODEL provider to work with any
LLM server that exposes a simple POST /chat endpoint accepting:
    Request:  {"message": "..."}
    Response: {"response": "..."}

Usage:
    python -m config.local_llm_proxy

Configure via environment variables:
    LOCAL_LLM_CHAT_URL   - The upstream /chat endpoint URL (required)
    LOCAL_LLM_PROXY_PORT - Port for the proxy to listen on (default: 11434)
"""

import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

from dotenv import load_dotenv

load_dotenv()

CHAT_URL = os.getenv("LOCAL_LLM_CHAT_URL", "")
PROXY_PORT = int(os.getenv("LOCAL_LLM_PROXY_PORT", "11434"))


class OllamaProxyHandler(BaseHTTPRequestHandler):
    """Translates Ollama /api/chat requests to simple /chat POST requests."""

    def do_GET(self):
        """Handle GET requests - Ollama version/tags endpoints."""
        if self.path == "/" or self.path == "/api/version":
            self._send_json({"version": "local-llm-proxy"})
        elif self.path == "/api/tags":
            self._send_json({"models": [{"name": "local-model", "size": 0}]})
        else:
            self._send_json({"status": "ok"})

    def do_POST(self):
        """Translate Ollama /api/chat to upstream /chat."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        # Build a single prompt from the messages array (system + user)
        messages = data.get("messages", [])
        parts = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                parts.append(content)
            elif role == "user":
                parts.append(content)
        message_text = "\n\n".join(parts)

        if not message_text:
            # Fallback: try 'prompt' field (used by /api/generate)
            message_text = data.get("prompt", "")

        if not message_text:
            self._send_json({"error": "No message found in request"}, status=400)
            return

        # Forward to the upstream /chat endpoint
        try:
            req = Request(
                CHAT_URL,
                data=json.dumps({"message": message_text}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=120) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
        except URLError as e:
            self._send_json(
                {"error": f"Upstream request failed: {e}"}, status=502
            )
            return
        except Exception as e:
            self._send_json({"error": str(e)}, status=500)
            return

        response_text = resp_data.get("response", "")
        model_name = data.get("model", "local-model")

        # Return in Ollama streaming format: newline-delimited JSON lines.
        # The autoheal OllamaProvider iterates line-by-line, parsing each as
        # a JSON object and extracting message.content until done=true.
        content_line = json.dumps({
            "model": model_name,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "message": {"role": "assistant", "content": response_text},
            "done": False,
        })
        done_line = json.dumps({
            "model": model_name,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "message": {"role": "assistant", "content": ""},
            "done": True,
            "total_duration": 0,
            "eval_count": len(response_text.split()),
        })
        streaming_body = content_line + "\n" + done_line + "\n"

        body_bytes = streaming_body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)
        self.wfile.flush()

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format, *args):
        """Log all requests when DEBUG is set, otherwise only errors."""
        if os.getenv("LOCAL_LLM_PROXY_DEBUG"):
            super().log_message(format, *args)
        elif args and "200" not in str(args[0]):
            super().log_message(format, *args)


def main():
    if not CHAT_URL:
        print("ERROR: LOCAL_LLM_CHAT_URL environment variable is required.")
        print("Example: LOCAL_LLM_CHAT_URL=https://your-server.com/chat")
        sys.exit(1)

    print(f"Local LLM Proxy starting...")
    print(f"  Upstream:  {CHAT_URL}")
    print(f"  Listening: http://localhost:{PROXY_PORT}")
    print(f"  Ollama API available at http://localhost:{PROXY_PORT}/api/chat")
    print()

    server = HTTPServer(("127.0.0.1", PROXY_PORT), OllamaProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
