"""Chapter 1 Base: URL 파싱, HTTP 요청, show(), load() 검증"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from conftest import make_200_handler
from browser import URL, show, load


# ================================================================
# URL 파싱
# ================================================================
class TestURLParsing:
    """URL.__init__에서 scheme, host, port, path를 올바르게 분리하는지 검증."""

    def test_http_basic(self):
        url = URL("http://example.org/index.html")
        assert url.scheme == "http"
        assert url.host == "example.org"
        assert url.port == 80
        assert url.path == "/index.html"

    def test_https_basic(self):
        url = URL("https://example.org/page")
        assert url.scheme == "https"
        assert url.host == "example.org"
        assert url.port == 443
        assert url.path == "/page"

    def test_no_path_adds_slash(self):
        """경로 없이 호스트만 있으면 path가 /이 되어야 한다."""
        url = URL("http://example.org")
        assert url.path == "/"

    def test_custom_port(self):
        url = URL("http://example.org:8080/api")
        assert url.host == "example.org"
        assert url.port == 8080
        assert url.path == "/api"

    def test_https_custom_port(self):
        url = URL("https://example.org:4443/secure")
        assert url.host == "example.org"
        assert url.port == 4443

    def test_deep_path(self):
        url = URL("http://example.org/a/b/c/d")
        assert url.path == "/a/b/c/d"

    def test_root_path(self):
        url = URL("http://example.org/")
        assert url.path == "/"

    def test_unsupported_scheme_raises(self):
        """http, https 외의 스킴은 AssertionError가 발생해야 한다."""
        try:
            URL("ftp://example.org/")
            assert False, "ftp 스킴에서 예외가 발생해야 합니다"
        except AssertionError:
            pass


# ================================================================
# URL.request() — HTTP 요청
# ================================================================
class TestURLRequest:
    """test_server를 사용해 실제 HTTP 요청/응답 흐름 검증."""

    def test_get_request_returns_body(self, test_server):
        """GET 요청의 body가 올바르게 반환되는지 확인."""
        server = test_server({
            "/": make_200_handler("Hello from server"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        body = url.request()
        assert body == "Hello from server"

    def test_request_sends_host_header(self, test_server):
        """Host 헤더가 올바르게 전송되는지 확인."""
        server = test_server({
            "/": make_200_handler("ok"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        url.request()
        assert "Host" in server.last_request_headers

    def test_request_correct_path(self, test_server):
        """요청 경로가 올바르게 전송되는지 확인."""
        server = test_server({
            "/some/path": make_200_handler("found"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/some/path")
        body = url.request()
        assert body == "found"
        assert server.last_request_path == "/some/path"

    def test_request_empty_body(self, test_server):
        """빈 본문을 올바르게 처리하는지 확인."""
        server = test_server({
            "/empty": make_200_handler(""),
        })
        url = URL(f"http://127.0.0.1:{server.port}/empty")
        body = url.request()
        assert body == ""

    def test_request_unicode_body(self, test_server):
        """유니코드 본문을 올바르게 처리하는지 확인."""
        server = test_server({
            "/unicode": make_200_handler("안녕하세요"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/unicode")
        body = url.request()
        assert body == "안녕하세요"


# ================================================================
# show() — HTML 태그 제거
# ================================================================
class TestShow:
    """show()가 HTML 태그를 제거하고 텍스트만 출력하는지 검증."""

    def test_plain_text(self, capture_stdout):
        show("Hello World")
        assert capture_stdout.getvalue() == "Hello World"

    def test_strip_single_tag(self, capture_stdout):
        show("<p>Hello</p>")
        assert capture_stdout.getvalue() == "Hello"

    def test_strip_nested_tags(self, capture_stdout):
        show("<html><body><p>Hello</p></body></html>")
        assert capture_stdout.getvalue() == "Hello"

    def test_multiple_text_segments(self, capture_stdout):
        show("<p>Hello</p><p>World</p>")
        assert capture_stdout.getvalue() == "HelloWorld"

    def test_empty_input(self, capture_stdout):
        show("")
        assert capture_stdout.getvalue() == ""

    def test_only_tags(self, capture_stdout):
        show("<br><hr><img>")
        assert capture_stdout.getvalue() == ""

    def test_text_with_attributes(self, capture_stdout):
        """태그 내 속성이 있어도 태그 전체가 제거되는지 확인."""
        show('<a href="url">Link</a>')
        assert capture_stdout.getvalue() == "Link"


# ================================================================
# load() — request + show 통합
# ================================================================
class TestLoad:
    """load()가 request()와 show()를 올바르게 조합하는지 검증."""

    def test_load_fetches_and_shows(self, test_server, capture_stdout):
        server = test_server({
            "/": make_200_handler("<html><body>Hello Load</body></html>"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        load(url)
        assert capture_stdout.getvalue() == "Hello Load"

    def test_load_strips_tags(self, test_server, capture_stdout):
        server = test_server({
            "/": make_200_handler("<p>one</p><p>two</p>"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        load(url)
        assert capture_stdout.getvalue() == "onetwo"
