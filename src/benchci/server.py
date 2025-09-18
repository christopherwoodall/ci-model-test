import os
import http.server
import socketserver
from pathlib import Path


def start_server(config, port: int = 8000):
    reports_path = Path(config["evaluation"]["output"]["reports"]).resolve()

    if not reports_path.exists() or not reports_path.is_dir():
        raise FileNotFoundError(f"Reports directory not found: {reports_path}")

    os.chdir(reports_path)

    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)

    print(f"Serving reports from {reports_path} at http://localhost:{port}")
    with httpd:
        httpd.RequestHandlerClass.directory = str(reports_path)
        httpd.serve_forever()
