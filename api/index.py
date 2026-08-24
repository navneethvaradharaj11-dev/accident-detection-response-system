from pathlib import Path
import sys
from urllib.parse import urlparse, unquote

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from web_dashboard import DashboardRequestHandler, TEMPLATES_DIR, STATIC_DIR, CONTROLLER

class handler(DashboardRequestHandler):
    def _normalize_path(self) -> str:
        # Check headers passed by Vercel for original path
        for header_key in ("x-forwarded-uri", "x-matched-path", "x-original-uri", "x-invoke-path"):
            val = self.headers.get(header_key)
            if val:
                path = unquote(urlparse(val).path)
                if path and not path.startswith("/api/index.py"):
                    return path

        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path.startswith("/api/index.py"):
            path = path[len("/api/index.py"):]
            if not path:
                path = "/"

        return path

    def do_GET(self) -> None:
        norm_path = self._normalize_path()
        self.path = norm_path

        if norm_path == "/":
            self._send_file(TEMPLATES_DIR / "index.html", "text/html; charset=utf-8")
            return
        if norm_path == "/service-bay":
            self._send_file(TEMPLATES_DIR / "service_bay.html", "text/html; charset=utf-8")
            return
        if norm_path == "/garage-setup":
            self._send_file(TEMPLATES_DIR / "garage_setup.html", "text/html; charset=utf-8")
            return
        if norm_path == "/api/state":
            self._send_json(CONTROLLER.get_state())
            return
        if norm_path.startswith("/static/"):
            relative = norm_path.removeprefix("/static/")
            target = (STATIC_DIR / relative).resolve()
            if STATIC_DIR.resolve() in target.parents or target.parent == STATIC_DIR.resolve():
                self._send_file(target)
                return

        super().do_GET()

    def do_POST(self) -> None:
        norm_path = self._normalize_path()
        self.path = norm_path
        super().do_POST()
