"""Exercise 1-4: Entities — &lt; &gt; 엔티티 변환"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from browser import show


class TestEntities:
    """HTML 엔티티 &lt; 와 &gt; 변환 검증."""

    def test_lt_entity(self, capture_stdout):
        """&lt; 가 < 로 출력되는지 확인."""
        show("&lt;")
        assert capture_stdout.getvalue() == "<"

    def test_gt_entity(self, capture_stdout):
        """&gt; 가 > 로 출력되는지 확인."""
        show("&gt;")
        assert capture_stdout.getvalue() == ">"

    def test_lt_gt_combined(self, capture_stdout):
        """&lt;div&gt; 가 <div> 로 출력되는지 확인."""
        show("&lt;div&gt;")
        assert capture_stdout.getvalue() == "<div>"

    def test_entity_mixed_with_text(self, capture_stdout):
        """일반 텍스트와 엔티티가 섞인 경우."""
        show("a &lt; b &gt; c")
        assert capture_stdout.getvalue() == "a < b > c"

    def test_entity_mixed_with_tags(self, capture_stdout):
        """HTML 태그 안에 있지 않은 엔티티만 변환."""
        show("<p>&lt;hello&gt;</p>")
        assert capture_stdout.getvalue() == "<hello>"

    def test_no_entity_plain_text(self, capture_stdout):
        """엔티티가 없는 일반 텍스트는 그대로 출력."""
        show("Hello World")
        assert capture_stdout.getvalue() == "Hello World"

    def test_multiple_entities_in_a_row(self, capture_stdout):
        """엔티티가 연속으로 나오는 경우."""
        show("&lt;&lt;&gt;&gt;")
        assert capture_stdout.getvalue() == "<<>>"
