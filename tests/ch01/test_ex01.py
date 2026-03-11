"""Exercise 1-1: HTTP/1.1 — Connection, User-Agent 헤더 전송 검증"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from conftest import make_200_handler
from browser import URL


class TestHTTP11:
    """HTTP/1.1 전환, Connection: close, User-Agent 헤더 전송 검증."""

    def test_sends_connection_close(self, test_server):
        """Connection: close 헤더가 전송되는지 확인."""
        server = test_server({
            "/": make_200_handler("ok"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        url.request()
        assert server.last_request_headers.get("Connection") == "close"

    def test_sends_user_agent(self, test_server):
        """User-Agent 헤더가 전송되는지 확인."""
        server = test_server({
            "/": make_200_handler("ok"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        url.request()
        assert "User-Agent" in server.last_request_headers
        assert len(server.last_request_headers["User-Agent"]) > 0

    def test_http_version_1_1(self, test_server):
        """HTTP/1.1 요청 + Connection: close 조합으로 동작 확인."""
        server = test_server({
            "/": make_200_handler("hello"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        body = url.request()
        assert body == "hello"
        assert server.last_request_headers.get("Connection") == "close"

    def test_custom_headers_easy_to_add(self, test_server):
        """추가 헤더를 쉽게 넣을 수 있는 구조인지 확인.

        request(headers=...) 인자 또는 URL.headers 속성 중 하나를 지원하면 통과.
        """
        server = test_server({
            "/": make_200_handler("ok"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")

        try:
            url.request(headers={"X-Custom": "test-value"})
            assert server.last_request_headers.get("X-Custom") == "test-value"
        except TypeError:
            url2 = URL(f"http://127.0.0.1:{server.port}/")
            if hasattr(url2, "headers"):
                url2.headers["X-Custom"] = "test-value"
                url2.request()
                assert server.last_request_headers.get("X-Custom") == "test-value"
            else:
                raise AssertionError(
                    "추가 헤더를 쉽게 넣을 수 있는 인터페이스가 없습니다. "
                    "request(headers=...) 인자 또는 URL.headers 속성을 구현하세요."
                )
