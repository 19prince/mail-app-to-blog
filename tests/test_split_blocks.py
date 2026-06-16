import sys
import types
import unittest
from unittest.mock import MagicMock

# odoo.models needs a real Model class so MailingMailing becomes a real Python class
_models_module = types.ModuleType('odoo.models')
_models_module.Model = type('Model', (), {})
sys.modules['odoo.models'] = _models_module

_odoo_mock = MagicMock()
_odoo_mock.models = _models_module
sys.modules['odoo'] = _odoo_mock

for _mod in ['odoo.api', 'odoo.fields', 'odoo.exceptions', 'odoo.tools']:
    sys.modules.setdefault(_mod, MagicMock())

# html_sanitize must return its input unchanged for these tests
sys.modules['odoo.tools'].html_sanitize = lambda x, **kw: x

from models.mailing_mailing import MailingMailing  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Standard Odoo newsletter: logo section + 2 titled sections + footer
STANDARD_EMAIL = """
<table class="o_layout"><tbody><tr><td>
<table class="o_mail_wrapper"><tbody><tr><td>
<table><tbody><tr><td>
<div class="o_stacking_wrapper">
<table class="o_stacking_wrapper"><tbody><tr>
<td class="o_mail_wrapper_td o_editable">

<table data-snippet="s_picture" class="s_picture o_mail_snippet_general">
  <tbody><tr><td><table><tbody><tr><td>
    <div class="container s_allow_columns"><p>June 14, 2026</p><h2>Newsletter Title</h2></div>
  </td></tr></tbody></table></td></tr></tbody>
</table>

<table data-snippet="s_title" class="s_title o_mail_snippet_general">
  <tbody><tr><td><table><tbody><tr><td>
    <div class="container s_allow_columns"><h3>TL;DR</h3></div>
  </td></tr></tbody></table></td></tr></tbody>
</table>

<table data-snippet="s_text_block" class="s_text_block o_mail_snippet_general">
  <tbody><tr><td><table><tbody><tr><td>
    <div class="container s_allow_columns"><ul><li>Bullet one</li><li>Bullet two</li></ul></div>
  </td></tr></tbody></table></td></tr></tbody>
</table>

<table data-snippet="s_title" class="s_title o_mail_snippet_general">
  <tbody><tr><td><table><tbody><tr><td>
    <div class="container s_allow_columns"><h3>TOP NEWS</h3></div>
  </td></tr></tbody></table></td></tr></tbody>
</table>

<table data-snippet="s_text_block" class="s_text_block o_mail_snippet_general">
  <tbody><tr><td><table><tbody><tr><td>
    <div class="container s_allow_columns"><p>Main content here.</p><p>More content.</p></div>
  </td></tr></tbody></table></td></tr></tbody>
</table>

<table class="s_footer_social o_mail_block_footer_social o_mail_snippet_general">
  <tbody><tr><td>
    <a href="/mailing/28/confirm_unsubscribe?document_id=6">Unsubscribe</a>
    | <a href="/contact">Contact</a>
    <p>© 2026 All Rights Reserved</p>
  </td></tr></tbody>
</table>

</td></tr></tbody></table>
</div>
</td></tr></tbody></table>
</td></tr></tbody></table>
</td></tr></tbody></table>
"""

# Email with only one s_title (2-block output expected)
ONE_TITLE_EMAIL = """
<table class="o_layout"><tbody><tr><td>
<table class="o_mail_wrapper"><tbody><tr><td>
<table><tbody><tr><td>
<div class="o_stacking_wrapper">
<table class="o_stacking_wrapper"><tbody><tr>
<td class="o_mail_wrapper_td o_editable">

<table data-snippet="s_picture" class="s_picture o_mail_snippet_general">
  <tbody><tr><td><table><tbody><tr><td>
    <div class="container s_allow_columns"><h2>Header</h2></div>
  </td></tr></tbody></table></td></tr></tbody>
</table>

<table data-snippet="s_title" class="s_title o_mail_snippet_general">
  <tbody><tr><td><table><tbody><tr><td>
    <div class="container s_allow_columns"><h3>Only Section</h3></div>
  </td></tr></tbody></table></td></tr></tbody>
</table>

<table data-snippet="s_text_block" class="s_text_block o_mail_snippet_general">
  <tbody><tr><td><table><tbody><tr><td>
    <div class="container s_allow_columns"><p>Content.</p></div>
  </td></tr></tbody></table></td></tr></tbody>
</table>

<table class="s_footer_social o_mail_block_footer_social">
  <tbody><tr><td>
    <a href="/unsubscribe">Unsubscribe</a> | <a href="/contact">Contact</a>
  </td></tr></tbody>
</table>

</td></tr></tbody></table>
</div>
</td></tr></tbody></table>
</td></tr></tbody></table>
</td></tr></tbody></table>
"""

# Plain HTML with no data-snippet tables — should trigger fallback
PLAIN_EMAIL = """
<div>
  <p>Hello world.</p>
  <a href="/mailing/confirm_unsubscribe?foo=bar">Unsubscribe</a>
  | <a href="/contact">Contact</a>
</div>
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSplitIntoBlocks(unittest.TestCase):

    def _call(self, html):
        """Call _split_into_blocks with None for self (method ignores self)."""
        return MailingMailing._split_into_blocks(None, html)

    def test_standard_email_produces_three_sections(self):
        result = self._call(STANDARD_EMAIL)
        self.assertIsNotNone(result, "Should return content, not None")
        self.assertEqual(
            result.count('<section>'), 3,
            f"Expected 3 <section> elements, got:\n{result}"
        )

    def test_footer_is_stripped(self):
        result = self._call(STANDARD_EMAIL)
        self.assertIsNotNone(result)
        self.assertNotIn('Unsubscribe', result)
        self.assertNotIn('All Rights Reserved', result)
        self.assertNotIn('confirm_unsubscribe', result)

    def test_pipe_separator_absent(self):
        result = self._call(STANDARD_EMAIL)
        self.assertIsNotNone(result)
        # The '|' text node between Unsubscribe and Contact must be gone
        self.assertNotIn('| ', result)

    def test_content_preserved(self):
        result = self._call(STANDARD_EMAIL)
        self.assertIsNotNone(result)
        self.assertIn('TL;DR', result)
        self.assertIn('TOP NEWS', result)
        self.assertIn('Bullet one', result)
        self.assertIn('Main content here', result)
        self.assertIn('June 14, 2026', result)

    def test_one_title_produces_two_sections(self):
        result = self._call(ONE_TITLE_EMAIL)
        self.assertIsNotNone(result)
        self.assertEqual(
            result.count('<section>'), 2,
            f"Expected 2 <section> elements, got:\n{result}"
        )

    def test_plain_html_returns_none_for_fallback(self):
        result = self._call(PLAIN_EMAIL)
        self.assertIsNone(
            result,
            "Should return None when no data-snippet tables found, to signal fallback"
        )

    def test_empty_string_returns_none(self):
        self.assertIsNone(self._call(''))

    def test_none_returns_none(self):
        self.assertIsNone(self._call(None))


class TestPrepareBlogContent(unittest.TestCase):
    """Tests _prepare_blog_content() via direct call, mocking body_html."""

    def _make_record(self, body_html):
        record = MagicMock()
        record.body_html = body_html
        record.ensure_one = MagicMock()
        record._split_into_blocks = lambda html: MailingMailing._split_into_blocks(record, html)
        record._strip_unsubscribe_links = lambda html: MailingMailing._strip_unsubscribe_links(record, html)
        return record

    def test_snippet_email_returns_sections(self):
        record = self._make_record(STANDARD_EMAIL)
        result = MailingMailing._prepare_blog_content(record)
        self.assertIn('<section>', result)
        self.assertEqual(result.count('<section>'), 3)

    def test_plain_email_falls_back_to_strip(self):
        record = self._make_record(PLAIN_EMAIL)
        result = MailingMailing._prepare_blog_content(record)
        # Fallback path: unsubscribe link stripped, content preserved
        self.assertNotIn('confirm_unsubscribe', result)
        self.assertIn('Hello world', result)
        # No sections — just cleaned HTML
        self.assertNotIn('<section>', result)


if __name__ == '__main__':
    unittest.main()
