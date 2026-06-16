# Snippet-Aware Block Splitting Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the blog post content produced by `action_publish_to_blog` into 2–3 `<section>` blocks by reading the email's existing `data-snippet` table structure; eliminate the orphaned `|` pipe separator by dropping the footer table entirely instead of surgically removing just the unsubscribe link.

**Architecture:** Add `_split_into_blocks(html)` to `MailingMailing`. It parses `<table data-snippet>` elements with `lxml.html`, drops the footer table (class `s_footer_social`), groups remaining snippets using `s_title` tables as section boundaries, extracts the inner `<div class="container">` from each snippet, and wraps each group in a `<section>`. `_prepare_blog_content()` calls this first and falls back to the existing `_strip_unsubscribe_links()` if no snippet structure is detected.

**Tech Stack:** `lxml.html` (already in Odoo venv — no new dependency), Python `unittest` (stdlib), Odoo venv Python at `/Users/dortsman/Code/odoo18/venv/bin/python3`

**Spec:** `docs/superpowers/specs/2026-06-16-snippet-block-splitting-design.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `models/mailing_mailing.py` | Add `_split_into_blocks()`; update `_prepare_blog_content()` |
| Create | `tests/__init__.py` | Makes `tests/` a package so `python -m unittest discover` finds tests |
| Create | `tests/test_split_blocks.py` | Unit tests for `_split_into_blocks()` and `_prepare_blog_content()` |

---

## Chunk 1: Tests and `_split_into_blocks()`

### Task 1: Create test file with fixtures and failing tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_split_blocks.py`

- [ ] **Step 1.1: Create `tests/__init__.py`**

  ```bash
  touch /Users/dortsman/Code/mail-app-to-blog/tests/__init__.py
  ```

- [ ] **Step 1.2: Create `tests/test_split_blocks.py` with fixtures and three failing tests**

  ```python
  # tests/test_split_blocks.py
  import sys
  import unittest
  from unittest.mock import MagicMock

  # Stub Odoo modules so the model file can be imported without a running Odoo instance
  for _mod in [
      'odoo', 'odoo.api', 'odoo.fields', 'odoo.models',
      'odoo.exceptions', 'odoo.tools',
  ]:
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
          record = MagicMock(spec=MailingMailing)
          record.body_html = body_html
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
  ```

- [ ] **Step 1.3: Run tests — verify they all fail with `AttributeError` (method not yet implemented)**

  ```bash
  cd /Users/dortsman/Code/mail-app-to-blog
  /Users/dortsman/Code/odoo18/venv/bin/python3 -m unittest tests.test_split_blocks -v 2>&1
  ```

  Expected: All tests error/fail. `AttributeError: type object 'MailingMailing' has no attribute '_split_into_blocks'` is the correct failure mode.

---

### Task 2: Implement `_split_into_blocks()`

**Files:**
- Modify: `models/mailing_mailing.py`

- [ ] **Step 2.1: Add `lxml` import and `_split_into_blocks()` method**

  Open `models/mailing_mailing.py`. After the existing `import re` line at the top, the imports are already sufficient — `lxml.html` will be imported inside the method to keep the module import lightweight.

  Add the new method to the `MailingMailing` class, **after** `_prepare_blog_content()` and **before** `_strip_unsubscribe_links()`:

  ```python
  def _split_into_blocks(self, html_content):
      if not html_content:
          return None
      from lxml import html as lxml_html
      from lxml import etree

      FOOTER_CLASSES = {'s_footer_social', 'o_mail_block_footer_social'}

      try:
          root = lxml_html.fromstring(html_content)
      except etree.ParserError:
          return None

      # Collect all snippet tables anywhere in the document
      snippet_tables = root.xpath('//table[@data-snippet]')
      if not snippet_tables:
          return None

      # Drop footer tables
      content_snippets = [
          t for t in snippet_tables
          if not FOOTER_CLASSES & set(t.get('class', '').split())
      ]
      if not content_snippets:
          return None

      # Group snippets: each s_title starts a new group;
      # snippets before the first s_title form their own group (header).
      groups = []
      current = []
      for table in content_snippets:
          if table.get('data-snippet') == 's_title' and current:
              groups.append(current)
              current = []
          current.append(table)
      if current:
          groups.append(current)

      # Extract the inner <div class="container"> from each snippet.
      # Fall back to the full table if none found.
      sections = []
      for group in groups:
          parts = []
          for table in group:
              containers = table.xpath('.//div[contains(@class,"container")]')
              node = containers[0] if containers else table
              parts.append(lxml_html.tostring(node, encoding='unicode'))
          if parts:
              sections.append('<section>' + ''.join(parts) + '</section>')

      return ''.join(sections) if sections else None
  ```

- [ ] **Step 2.2: Run tests — verify the six `TestSplitIntoBlocks` tests pass**

  ```bash
  cd /Users/dortsman/Code/mail-app-to-blog
  /Users/dortsman/Code/odoo18/venv/bin/python3 -m unittest tests.test_split_blocks.TestSplitIntoBlocks -v 2>&1
  ```

  Expected output (all PASS):
  ```
  test_content_preserved ... ok
  test_empty_string_returns_none ... ok
  test_footer_is_stripped ... ok
  test_none_returns_none ... ok
  test_one_title_produces_two_sections ... ok
  test_pipe_separator_absent ... ok
  test_plain_html_returns_none_for_fallback ... ok
  test_standard_email_produces_three_sections ... ok
  ```

---

### Task 3: Update `_prepare_blog_content()`

**Files:**
- Modify: `models/mailing_mailing.py`

- [ ] **Step 3.1: Replace `_prepare_blog_content()` body**

  Current implementation (lines 90–93):
  ```python
  def _prepare_blog_content(self):
      self.ensure_one()
      content = html_sanitize(self.body_html or '')
      return self._strip_unsubscribe_links(content)
  ```

  Replace with:
  ```python
  def _prepare_blog_content(self):
      self.ensure_one()
      content = html_sanitize(self.body_html or '')
      blocks = self._split_into_blocks(content)
      if blocks:
          return blocks
      return self._strip_unsubscribe_links(content)
  ```

- [ ] **Step 3.2: Run the full test suite — all tests must pass**

  ```bash
  cd /Users/dortsman/Code/mail-app-to-blog
  /Users/dortsman/Code/odoo18/venv/bin/python3 -m unittest tests.test_split_blocks -v 2>&1
  ```

  Expected: All 10 tests PASS, 0 failures, 0 errors.

- [ ] **Step 3.3: Commit**

  ```bash
  cd /Users/dortsman/Code/mail-app-to-blog
  git add models/mailing_mailing.py tests/__init__.py tests/test_split_blocks.py
  git commit -m "feat: split blog content into sections using email snippet structure

  - Add _split_into_blocks(): parses data-snippet tables, groups by
    s_title boundaries, drops footer table (kills the | pipe too),
    wraps each group in <section>
  - _prepare_blog_content() calls _split_into_blocks() first, falls
    back to _strip_unsubscribe_links() for non-snippet emails
  - Add unit tests covering 3-section output, footer stripping,
    pipe removal, 2-section edge case, and fallback path

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
  ```

---

## Manual Verification

After committing, verify end-to-end in Odoo:

1. Restart Odoo with the updated module: `./odoo-bin -u mail_app_to_blog`
2. Open the sent mailing "12 Out of 33, Joule Goes Free, and DC Is June 25"
3. Ensure Blog is set in the Settings tab
4. Click **Publish to Blog**
5. Open the created blog post in the website editor
6. Confirm:
   - [ ] 3 separate draggable `<section>` blocks visible in the editor
   - [ ] No "Unsubscribe" link anywhere in the content
   - [ ] No `|` pipe character in the content
   - [ ] TL;DR section is block 2, TOP NEWS section is block 3
   - [ ] Header/logo is block 1
