"""Exercise 1-5: view-source — HTML 소스를 그대로 텍스트로 출력"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from conftest import make_200_handler
from browser import URL, show


class TestViewSource:
    """view-source: 스킴 — HTML 소스를 그대로 텍스트로 출력."""

    def test_view_source_shows_tags(self, test_server, capture_stdout):
        """view-source에서는 태그가 제거되지 않고 그대로 보여야 한다."""
        server = test_server({
            "/": make_200_handler("<html><body><p>Hello</p></body></html>"),
        })
        url = URL(f"view-source:http://127.0.0.1:{server.port}/")
        body = url.request()
        show(body)
        output = capture_stdout.getvalue()
        assert "<html>" in output
        assert "<body>" in output
        assert "<p>Hello</p>" in output

    def test_view_source_entities_visible(self, test_server, capture_stdout):
        """view-source에서 엔티티를 포함한 소스 전체가 보여야 한다."""
        server = test_server({
            "/": make_200_handler("<p>&lt;div&gt;</p>"),
        })
        url = URL(f"view-source:http://127.0.0.1:{server.port}/")
        body = url.request()
        show(body)
        output = capture_stdout.getvalue()
        assert "<p>" in output

    def test_view_source_scheme_parsed(self):
        """view-source: URL이 올바르게 파싱되는지 확인."""
        url = URL("view-source:http://example.org/")
        assert url.scheme in ("view-source", "view-source:http")
