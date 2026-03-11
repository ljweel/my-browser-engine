"""Exercise 1-8: Caching — Cache-Control 헤더 기반 HTTP 응답 캐싱"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from browser import URL


class TestCaching:
    """HTTP 캐싱 — Cache-Control 헤더 기반 응답 캐싱."""

    def test_cached_response_reused(self, test_server):
        """같은 URL에 대한 두 번째 요청에서 캐시된 응답을 사용하는지 확인."""
        call_count = {"n": 0}

        def counting_handler(req):
            call_count["n"] += 1
            body = f"response {call_count['n']}".encode()
            req.send_response(200)
            req.send_header("Content-Length", str(len(body)))
            req.send_header("Cache-Control", "max-age=3600")
            req.end_headers()
            req.wfile.write(body)

        server = test_server({"/cacheable": counting_handler})

        url1 = URL(f"http://127.0.0.1:{server.port}/cacheable")
        body1 = url1.request()
        assert body1 == "response 1"

        url2 = URL(f"http://127.0.0.1:{server.port}/cacheable")
        body2 = url2.request()
        assert body2 == "response 1"
        assert call_count["n"] == 1

    def test_no_store_not_cached(self, test_server):
        """Cache-Control: no-store인 경우 캐시하지 않는지 확인."""
        call_count = {"n": 0}

        def no_store_handler(req):
            call_count["n"] += 1
            body = f"response {call_count['n']}".encode()
            req.send_response(200)
            req.send_header("Content-Length", str(len(body)))
            req.send_header("Cache-Control", "no-store")
            req.end_headers()
            req.wfile.write(body)

        server = test_server({"/no-store": no_store_handler})

        url1 = URL(f"http://127.0.0.1:{server.port}/no-store")
        body1 = url1.request()
        assert body1 == "response 1"

        url2 = URL(f"http://127.0.0.1:{server.port}/no-store")
        body2 = url2.request()
        assert body2 == "response 2"
        assert call_count["n"] == 2

    def test_max_age_expired(self, test_server):
        """max-age=0이면 즉시 만료되어 캐시를 사용하지 않는지 확인."""
        call_count = {"n": 0}

        def expired_handler(req):
            call_count["n"] += 1
            body = f"response {call_count['n']}".encode()
            req.send_response(200)
            req.send_header("Content-Length", str(len(body)))
            req.send_header("Cache-Control", "max-age=0")
            req.end_headers()
            req.wfile.write(body)

        server = test_server({"/expired": expired_handler})

        url1 = URL(f"http://127.0.0.1:{server.port}/expired")
        url1.request()

        url2 = URL(f"http://127.0.0.1:{server.port}/expired")
        url2.request()
        assert call_count["n"] == 2

    def test_unknown_cache_control_not_cached(self, test_server):
        """no-store, max-age 이외의 Cache-Control 값이면 캐시하지 않는다."""
        call_count = {"n": 0}

        def unknown_cc_handler(req):
            call_count["n"] += 1
            body = f"response {call_count['n']}".encode()
            req.send_response(200)
            req.send_header("Content-Length", str(len(body)))
            req.send_header("Cache-Control", "private, must-revalidate")
            req.end_headers()
            req.wfile.write(body)

        server = test_server({"/unknown-cc": unknown_cc_handler})

        url1 = URL(f"http://127.0.0.1:{server.port}/unknown-cc")
        url1.request()

        url2 = URL(f"http://127.0.0.1:{server.port}/unknown-cc")
        url2.request()
        assert call_count["n"] == 2

    def test_only_get_200_cached(self, test_server):
        """GET + 200이 아닌 응답은 캐시하지 않는다."""
        call_count = {"n": 0}

        def not_found_handler(req):
            call_count["n"] += 1
            body = b"not found"
            req.send_response(404)
            req.send_header("Content-Length", str(len(body)))
            req.send_header("Cache-Control", "max-age=3600")
            req.end_headers()
            req.wfile.write(body)

        server = test_server({"/missing": not_found_handler})

        url1 = URL(f"http://127.0.0.1:{server.port}/missing")
        try:
            url1.request()
        except Exception:
            pass

        url2 = URL(f"http://127.0.0.1:{server.port}/missing")
        try:
            url2.request()
        except Exception:
            pass
        assert call_count["n"] == 2
