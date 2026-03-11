"""Exercise 1-3: data: URL — data 스킴으로 인라인 HTML 지원"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from browser import URL


class TestDataURL:
    """data: 스킴 지원 검증."""

    def test_data_url_basic(self):
        """data:text/html,Hello world! 를 올바르게 파싱하는지 확인."""
        url = URL("data:text/html,Hello world!")
        body = url.request()
        assert body == "Hello world!"

    def test_data_url_with_html_tags(self):
        """data: URL에 HTML 태그가 포함된 경우."""
        url = URL("data:text/html,<b>Bold</b>")
        body = url.request()
        assert body == "<b>Bold</b>"

    def test_data_url_empty_body(self):
        """data: URL의 본문이 비어있는 경우."""
        url = URL("data:text/html,")
        body = url.request()
        assert body == ""

    def test_data_url_special_characters(self):
        """data: URL에 특수문자가 포함된 경우."""
        url = URL("data:text/html,Hello&amp;World")
        body = url.request()
        assert body == "Hello&amp;World"

    def test_data_scheme_parsed(self):
        """data: URL의 scheme이 'data'로 파싱되는지 확인."""
        url = URL("data:text/html,test")
        assert url.scheme == "data"
