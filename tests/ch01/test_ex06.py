"""Exercise 1-6: Keep-alive — Connection: keep-alive 및 소켓 재사용"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from conftest import make_200_handler
from browser import URL


class TestKeepAlive:
    """Connection: keep-alive — 소켓 재사용 검증."""

    def test_sends_keep_alive(self, test_server):
        """Connection: keep-alive 헤더가 전송되는지 확인."""
        server = test_server({
            "/": make_200_handler("ok"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        url.request()
        assert server.last_request_headers.get("Connection") == "keep-alive"

    def test_socket_reuse_same_server(self, test_server):
        """같은 서버에 대한 연속 요청에서 소켓이 재사용되는지 확인."""
        call_count = {"n": 0}

        def counting_handler(req):
            call_count["n"] += 1
            body = f"response {call_count['n']}".encode()
            req.send_response(200)
            req.send_header("Content-Length", str(len(body)))
            req.end_headers()
            req.wfile.write(body)

        server = test_server({"/a": counting_handler, "/b": counting_handler})
        host = f"127.0.0.1:{server.port}"

        url1 = URL(f"http://{host}/a")
        body1 = url1.request()
        assert body1 == "response 1"

        url2 = URL(f"http://{host}/b")
        body2 = url2.request()
        assert body2 == "response 2"

    def test_reads_exact_content_length(self, test_server):
        """Content-Length만큼만 읽는지 확인 (keep-alive에서 필수)."""
        server = test_server({
            "/": make_200_handler("exact"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        body = url.request()
        assert body == "exact"
