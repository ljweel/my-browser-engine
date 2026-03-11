"""공통 fixture: stdout 캡처, 테스트용 HTTP 서버, 임시 파일 등"""

import gzip
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import pytest


# ──────────────────────────────────────────────
# stdout 캡처
# ──────────────────────────────────────────────
@pytest.fixture
def capture_stdout(capsys):
    """show() 등 print 기반 함수의 출력을 캡처한다.

    사용법: 함수 호출 후 capture_stdout.getvalue()로 출력 확인.
    """
    class _CaptureProxy:
        def getvalue(self):
            return capsys.readouterr().out
    return _CaptureProxy()


# ──────────────────────────────────────────────
# 임시 파일 (file:// 스킴 테스트용)
# ──────────────────────────────────────────────
@pytest.fixture
def tmp_html_file(tmp_path):
    """임시 HTML 파일을 생성하고 경로를 반환한다."""
    def _create(content: str, filename: str = "test.html") -> Path:
        p = tmp_path / filename
        p.write_text(content, encoding="utf-8")
        return p
    return _create


# ──────────────────────────────────────────────
# 테스트용 HTTP 서버
# ──────────────────────────────────────────────
def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class TestHandler(BaseHTTPRequestHandler):
    """테스트 시나리오별 응답을 반환하는 핸들러."""

    # 클래스 변수로 테스트별 응답 설정
    routes = {}

    def do_GET(self):
        # 요청 헤더를 저장 (테스트에서 검증 가능)
        self.server.last_request_headers = dict(self.headers)
        self.server.last_request_path = self.path

        if self.path in self.server.routes:
            handler = self.server.routes[self.path]
            handler(self)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "9")
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass  # 테스트 중 서버 로그 출력 억제


@pytest.fixture
def test_server():
    """로컬 테스트 HTTP 서버를 실행한다.

    사용법:
        def test_something(test_server):
            server = test_server({
                "/hello": lambda handler: ...,
            })
            url = f"http://localhost:{server.port}/hello"
    """
    servers = []

    def _start(routes: dict):
        port = _find_free_port()
        server = HTTPServer(("127.0.0.1", port), TestHandler)
        server.routes = routes
        server.port = port
        server.last_request_headers = {}
        server.last_request_path = ""
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        servers.append(server)
        return server

    yield _start

    for s in servers:
        s.shutdown()


# ──────────────────────────────────────────────
# 헬퍼: 간단한 200 응답 핸들러 팩토리
# ──────────────────────────────────────────────
def make_200_handler(body: str, extra_headers: dict | None = None):
    """200 OK 응답을 반환하는 핸들러를 생성한다."""
    def handler(req):
        encoded = body.encode("utf-8")
        req.send_response(200)
        req.send_header("Content-Length", str(len(encoded)))
        if extra_headers:
            for k, v in extra_headers.items():
                req.send_header(k, v)
        req.end_headers()
        req.wfile.write(encoded)
    return handler


def make_redirect_handler(location: str, code: int = 301):
    """리다이렉트 응답을 반환하는 핸들러를 생성한다."""
    def handler(req):
        req.send_response(code)
        req.send_header("Location", location)
        req.send_header("Content-Length", "0")
        req.end_headers()
    return handler


def make_gzip_handler(body: str, chunked: bool = False):
    """gzip 압축 응답을 반환하는 핸들러를 생성한다."""
    def handler(req):
        compressed = gzip.compress(body.encode("utf-8"))
        req.send_response(200)
        req.send_header("Content-Encoding", "gzip")
        if chunked:
            req.send_header("Transfer-Encoding", "chunked")
            req.end_headers()
            # chunked 인코딩: 크기(hex)\r\n데이터\r\n ... 0\r\n\r\n
            chunk = f"{len(compressed):x}\r\n".encode() + compressed + b"\r\n"
            chunk += b"0\r\n\r\n"
            req.wfile.write(chunk)
        else:
            req.send_header("Content-Length", str(len(compressed)))
            req.end_headers()
            req.wfile.write(compressed)
    return handler
