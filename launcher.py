"""Entry point for the packaged .exe: starts FastAPI and opens the browser."""
import socket
import threading
import time
import webbrowser

import uvicorn

from app.main import app  # explicit import so PyInstaller bundles the app


def free_port(preferred: int = 8000) -> int:
    for port in (preferred, 0):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1]
            except OSError:
                continue
    return preferred


def open_browser(url: str) -> None:
    time.sleep(1.5)
    webbrowser.open(url)


if __name__ == "__main__":
    port = free_port(8000)
    url = f"http://127.0.0.1:{port}"
    print(f"PDF Span Remover running at {url}  (close this window to stop)")
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
