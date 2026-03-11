"""Exercise 1-9: Compression — gzip 압축 및 chunked Transfer-Encoding 지원"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from conftest import make_200_handler, make_gzip_handler
from browser import URL


class TestCompression:
    """gzip 압축 및 chunked Transfer-Encoding 지원 검증."""

    def test_sends_accept_encoding_gzip(self, test_server):
        """Accept-Encoding: gzip 헤더가 전송되는지 확인."""
        server = test_server({
            "/": make_200_handler("ok"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/")
        url.request()
        accept_enc = server.last_request_headers.get("Accept-Encoding", "")
        assert "gzip" in accept_enc

    def test_decompress_gzip_response(self, test_server):
        """gzip 압축된 응답을 올바르게 디코딩하는지 확인."""
        server = test_server({
            "/gz": make_gzip_handler("Hello Compressed World"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/gz")
        body = url.request()
        assert body == "Hello Compressed World"

    def test_gzip_with_chunked_encoding(self, test_server):
        """chunked Transfer-Encoding + gzip 조합을 처리하는지 확인."""
        server = test_server({
            "/chunked-gz": make_gzip_handler(
                "<html><body>Chunked and Compressed</body></html>",
                chunked=True,
            ),
        })
        url = URL(f"http://127.0.0.1:{server.port}/chunked-gz")
        body = url.request()
        assert "Chunked and Compressed" in body

    def test_non_compressed_still_works(self, test_server):
        """Accept-Encoding을 보내도 비압축 응답을 정상 처리하는지 확인."""
        server = test_server({
            "/plain": make_200_handler("no compression here"),
        })
        url = URL(f"http://127.0.0.1:{server.port}/plain")
        body = url.request()
        assert body == "no compression here"

    def test_gzip_large_body(self, test_server):
        """큰 본문의 gzip 압축/해제가 올바른지 확인."""
        large_text = "A" * 10000 + " END"
        server = test_server({
            "/big": make_gzip_handler(large_text),
        })
        url = URL(f"http://127.0.0.1:{server.port}/big")
        body = url.request()
        assert body == large_text
