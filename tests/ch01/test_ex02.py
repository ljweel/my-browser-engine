"""Exercise 1-2: File URLs — file:// 스킴으로 로컬 파일 읽기"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from browser import URL


class TestFileURL:
    """file:// 스킴으로 로컬 파일을 읽는 기능 검증."""

    def test_read_local_file(self, tmp_html_file):
        """file:// URL로 로컬 파일의 내용을 읽을 수 있는지 확인."""
        p = tmp_html_file("<html><body>Hello File</body></html>")
        url = URL(f"file://{p}")
        body = url.request()
        assert "Hello File" in body

    def test_file_url_plain_text(self, tmp_html_file):
        """HTML이 아닌 일반 텍스트 파일도 읽을 수 있는지 확인."""
        p = tmp_html_file("Just plain text", filename="plain.txt")
        url = URL(f"file://{p}")
        body = url.request()
        assert body == "Just plain text"

    def test_file_url_empty_file(self, tmp_html_file):
        """빈 파일을 읽었을 때 빈 문자열을 반환하는지 확인."""
        p = tmp_html_file("")
        url = URL(f"file://{p}")
        body = url.request()
        assert body == ""

    def test_file_url_unicode(self, tmp_html_file):
        """유니코드 내용이 포함된 파일을 올바르게 읽는지 확인."""
        p = tmp_html_file("안녕하세요 世界")
        url = URL(f"file://{p}")
        body = url.request()
        assert body == "안녕하세요 世界"

    def test_file_scheme_parsed(self):
        """file:// URL의 scheme이 'file'로 파싱되는지 확인."""
        url = URL("file:///tmp/test.html")
        assert url.scheme == "file"
