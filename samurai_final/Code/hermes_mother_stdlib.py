#!/usr/bin/env python3
"""
Hermes Mother Engine — Stdlib HTTP Server (fallback when FastAPI unavailable)
Run: python Code/hermes_mother.py
Ports: 8000 (humanizer API), 11434 proxies to Ollama
"""
import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime
from typing import Dict, Any

# Completion cache
COMPLETIONS_CACHE = {}

# Templates for fallback
TEMPLATES = {
    "technical_completion": {
        "defaults": {
            "___": "strict allowlist validation",
            "injection": "prompt injection attacks",
            "validation": "input sanitization"
        }
    },
    "security_assessment": {
        "defaults": {
            "___": "least privilege IAM roles",
            "policy": "restrictive policies",
            "VPC": "network segmentation"
        }
    },
    "creative_prompt": {
        "defaults": {
            "___": "purple flower fields",
            "sunset": "golden sunset",
            "neon": "neon rim lighting"
        }
    },
    "code_completion": {
        "defaults": {
            "___": "validated URL string",
            "url": "validated URL",
            "SecurityError": "exception raised on blocked request"
        }
    }
}

def humanize_text(text: str, style: str = "professional") -> str:
    """Apply natural phrasing to completion."""
    prefixes = ["Essentially,", "In practice,", "The core approach is to", "Fundamentally,"]
    if style == "creative":
        return text[0].lower() + text[1:] if text else text
    return text

def fill_blanks(text: str, context: str = "technical_completion") -> str:
    """Fill ___ blanks with template defaults."""
    tmpl = TEMPLATES.get(context, TEMPLATES["technical_completion"])
    defaults = tmpl["defaults"]
    
    result = text
    for pattern, replacement in defaults.items():
        result = result.replace("___", replacement, 1)
    
    # Remaining blanks get generic
    while "___" in result:
        result = result.replace("___", "a secure solution", 1)
    
    return humanize_text(result, context.split("_")[0] if "_" in context else "professional")

class HermesHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

    def send_json(self, data: Dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/api/health":
            self.send_json({"status": "alive", "port": 8000, "mode": "stdlib"})
        elif path == "/docs":
            # Mock Swagger UI redirect
            html = """<!DOCTYPE html><html><head><title>Hermes Mother API Docs</title></head>
            <body style="font-family:sans-serif;padding:40px">
            <h1>Hermes Mother Engine</h1>
            <p>HTTP Server running on 127.0.0.1:8000</p>
            <h2>Endpoints</h2>
            <ul>
              <li>GET /api/health - Health check</li>
              <li>POST /api/humanize-fill - Fill blanks in text</li>
            </ul>
            </body></html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        elif path == "/" or path == "":
            self.send_response(302)
            self.send_header('Location', '/docs')
            self.end_headers()
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path == "/api/humanize-fill":
            input_text = data.get("input_text", "")
            context_type = data.get("context_type", "technical_completion")
            
            # Fill blanks
            result = fill_blanks(input_text, context_type)
            
            # Log to cache
            COMPLETIONS_CACHE[input_text[:50]] = result
            
            self.send_json({
                "status": "success",
                "completion": result,
                "context": context_type,
                "timestamp": datetime.now().isoformat()
            })
        elif path == "/api/reset-cache":
            COMPLETIONS_CACHE.clear()
            self.send_json({"status": "cleared"})
        else:
            self.send_json({"error": "Not found"}, 404)

def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the HTTP server."""
    server = HTTPServer((host, port), HermesHandler)
    print(f"Hermes Mother Engine running on http://{host}:{port}")
    print("Endpoints: /api/health, /api/humanize-fill, /docs")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    run_server()