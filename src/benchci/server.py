import os
import yaml
import http.server
import socketserver
from pathlib import Path


def start_server(config_file_path: str, port: int = 8000):
    output_yaml = yaml.safe_load(Path(config_file_path).read_text())
    reports_path = Path(output_yaml["evaluation"]["output"]["reports"]).resolve()

    if not reports_path.exists() or not reports_path.is_dir():
        raise FileNotFoundError(f"Reports directory not found: {reports_path}")

    os.chdir(reports_path)

    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)

    print(f"Serving reports from {reports_path} at http://localhost:{port}")
    with httpd:
        httpd.RequestHandlerClass.directory = str(reports_path)
        httpd.serve_forever()
