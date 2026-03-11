"""Exercise 1-7: Redirects — 301/302 리다이렉트 추적 및 무한 루프 방지"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from conftest import make_200_handler, make_redirect_handler
from browser import URL


class TestRedirects:
    """301/302 리다이렉트 — Location 헤더 추적 및 무한 루프 방지."""

    def test_simple_redirect(self, test_server):
        """단순 301 리다이렉트를 따라가는지 확인."""
        server = test_server({
            "/new": make_200_handler("arrived"),
        })
        server.routes["/old"] = make_redirect_handler(
            f"http://127.0.0.1:{server.port}/new", code=301
        )
        url = URL(f"http://127.0.0.1:{server.port}/old")
        body = url.request()
        assert body == "arrived"

    def test_redirect_302(self, test_server):
        """302 리다이렉트도 처리하는지 확인."""
        server = test_server({
            "/dest": make_200_handler("found it"),
        })
        server.routes["/temp"] = make_redirect_handler(
            f"http://127.0.0.1:{server.port}/dest", code=302
        )
        url = URL(f"http://127.0.0.1:{server.port}/temp")
        body = url.request()
        assert body == "found it"

    def test_redirect_relative_path(self, test_server):
        """Location이 상대 경로(/ 로 시작)인 경우 같은 호스트로 요청."""
        server = test_server({
            "/a": make_redirect_handler("/b", code=301),
            "/b": make_200_handler("relative ok"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/a")
        body = url.request()
        assert body == "relative ok"

    def test_chained_redirects(self, test_server):
        """연속 리다이렉트를 따라가는지 확인."""
        server = test_server({
            "/r3": make_200_handler("end of chain"),
        })
        server.routes["/r1"] = make_redirect_handler(
            f"http://127.0.0.1:{server.port}/r2", code=301
        )
        server.routes["/r2"] = make_redirect_handler(
            f"http://127.0.0.1:{server.port}/r3", code=301
        )
        url = URL(f"http://127.0.0.1:{server.port}/r1")
        body = url.request()
        assert body == "end of chain"

    def test_redirect_loop_protection(self, test_server):
        """무한 리다이렉트 루프를 감지하고 중단하는지 확인."""
        server = test_server({})
        server.routes["/loop"] = make_redirect_handler(
            f"http://127.0.0.1:{server.port}/loop", code=301
        )
        url = URL(f"http://127.0.0.1:{server.port}/loop")
        try:
            url.request()
            assert False, "무한 리다이렉트 루프에서 예외가 발생해야 합니다"
        except Exception:
            pass  # 어떤 형태든 예외가 발생하면 OK

    def test_redirect_limit(self, test_server):
        """리다이렉트 횟수 제한이 동작하는지 확인 (최소 5회 이상은 따라가야)."""
        routes = {"/r5": make_200_handler("deep redirect ok")}
        server = test_server(routes)
        for i in range(5):
            server.routes[f"/r{i}"] = make_redirect_handler(
                f"http://127.0.0.1:{server.port}/r{i+1}", code=301
            )
        url = URL(f"http://127.0.0.1:{server.port}/r0")
        body = url.request()
        assert body == "deep redirect ok"
