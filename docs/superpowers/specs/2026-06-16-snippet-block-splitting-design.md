# Design: Snippet-Aware Block Splitting

**Date:** 2026-06-16  
**Status:** Approved  
**Branch:** 18.0

## Problem

`_prepare_blog_content()` returns the entire email body as a single HTML blob. When published to a blog post, the content field contains one monolithic string — the Odoo website editor sees no discrete blocks and there is nothing to drag, reorder, or edit independently.

Additionally, `_strip_unsubscribe_links()` surgically removes the `<a>` unsubscribe tag but leaves behind orphaned pipe separators (e.g., `| Contact`) as text nodes at the bottom of the post.

## Goal

- Split the published blog post content into 2–3 Odoo website builder `<section>` blocks
- Remove the `|` pipe separator cleanly
- No new dependencies; no changes to views, security, or `action_publish_to_blog()`

## Email HTML Structure

Odoo's mass mailing editor produces emails as nested `<table>` elements. Inside the `o_editable` td, each visual section is a `<table data-snippet="...">` element:

| Snippet class | `data-snippet` | Content |
|---|---|---|
| `s_picture` | `s_picture` | Logo / banner image |
| `s_title` | `s_title` | Section heading (blue bar) |
| `s_text_block` | `s_text_block` | Body content |
| `s_title` | `s_title` | Second section heading |
| `s_text_block` | `s_text_block` | Main body content |
| `s_footer_social` | `s_mail_block_footer_social` | LinkedIn, Unsubscribe \| Contact, © |

The `|` lives in the footer table as a literal text node between the Unsubscribe and Contact `<a>` tags.

## Design

### New method: `_split_into_blocks(html)`

1. Parse the sanitized HTML with `lxml.html` (already available in Odoo — no new dependency)
2. Find all `<table data-snippet="...">` elements inside the `o_editable` td
3. **Drop** any table whose `class` contains `s_footer_social` or `o_mail_block_footer_social` — this removes the footer, the unsubscribe link, and the `|` pipe at the source
4. Group remaining snippets using `s_title` as a section boundary:
   - **Block 1** — everything before the first `s_title` (header/logo)
   - **Block 2** — first `s_title` + following snippets until the next `s_title`
   - **Block 3** — second `s_title` + all remaining non-footer snippets
5. From each snippet, extract the inner `<div class="container">` (strips all email table scaffolding, leaving clean content HTML)
6. Wrap each group in a `<section>` element
7. Return the joined `<section>` elements as a string

### Updated method: `_prepare_blog_content()`

- Calls `html_sanitize()` as before
- Then calls `_split_into_blocks()` instead of `_strip_unsubscribe_links()`
- If `_split_into_blocks()` finds no `data-snippet` tables (email not authored in Odoo's editor), falls back to `_strip_unsubscribe_links()` returning a single block

### Retained method: `_strip_unsubscribe_links()`

Kept unchanged as the fallback path for emails without `data-snippet` structure.

## Output (example: "12 Out of 33" newsletter)

```html
<section>
  <!-- logo, date, banner image -->
</section>
<section>
  <!-- TL;DR heading + bullet list -->
</section>
<section>
  <!-- TOP NEWS heading + all main content -->
</section>
```

## Edge Cases

| Scenario | Behaviour |
|---|---|
| No `data-snippet` tables found | Fallback: single blob via `_strip_unsubscribe_links()` |
| Only 1 `s_title` found | 2 blocks: header + content |
| No `s_picture` (no pre-title content) | Block 1 skipped; starts at first `s_title` |
| Footer table absent | Graceful — nothing to drop |

## What Does Not Change

- `action_publish_to_blog()` — no change
- `blog.post.content` field — still an HTML string; `<section>` tags are valid
- Views (`mailing_mailing_views.xml`) — no change
- Security (`ir.model.access.xml`) — no change
- Module manifest — no change
