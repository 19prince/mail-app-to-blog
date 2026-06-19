# Mailing to Blog

Publish your Odoo email newsletters as blog posts with a single click - from the [19 Prince](https://www.19prince.com) team.
 
## Features

- **Publish to Blog** button on sent mailings creates a draft blog post
- **Choose your blog** per mailing via a dropdown in the Settings tab
- **Newsletter tag** auto-applied to every published blog post; editable per mailing in the Settings tab
- **Unsubscribe links stripped** automatically from blog post content
- Posts are created as **unpublished drafts** for review before going live
- **Smart button** links back from the mailing to its blog post
- **Duplicate-safe** — duplicating a mailing does not carry over the blog post link

## Requirements

- Odoo 18.0 or 19.0 — install from the branch matching your version (`18.0` or `19.0`)
- `mass_mailing` (Email Marketing) module installed
- `website_blog` (Blog) module installed

## Installation

1. Place this module in your Odoo addons path
2. Update the apps list: Settings > Apps > Update Apps List
3. Search for "Mailing to Blog" and install

## Usage

1. Create and send a mailing as usual in Email Marketing
2. After the mailing is sent, open it and go to the **Settings** tab
3. Select a target **Blog** from the dropdown — a **Newsletter** tag is automatically added to the **Blog Tags** field
4. Optionally add or remove tags in the **Blog Tags** field to control how the post is tagged on the site
5. Click the **Publish to Blog** button in the header
6. A draft blog post is created — review and publish it when ready
7. The **Blog Post** smart button links directly to the created post

**Note:** Unsubscribe links from the email are automatically stripped from the blog post content, as they are email-specific and would not function for web readers. The **Newsletter** tag is always applied to the blog post regardless of what is set in the Blog Tags field.

## How content is split into sections

When publishing, the module converts the email HTML into a set of `<section>` blocks that are individually editable and draggable in Odoo's website editor.

**What triggers a section break:**

1. **Section title snippets (`s_title`)** — the green "Headline" blocks used in the email builder (TL;DR, TOP NEWS, etc.) each start a new section that groups the title with its immediately following content.

2. **Headline elements inside text blocks** — any `<h2>`–`<h6>` heading tag inside a text block (`s_text_block`) starts a new section. In practice this means every article heading you insert with the **Heading** tool in a text block becomes its own independently draggable blog section.

**Example structure:**

| Email                                  | Blog sections produced           |
|----------------------------------------|----------------------------------|
| Header image / logo block              | Section 1: header                |
| `s_title` "TL;DR" + bullet text block  | Section 2: TL;DR + bullets       |
| `s_title` "TOP NEWS" + text block with headings: | |
| &nbsp;&nbsp;intro paragraph            | Section 3: TOP NEWS intro        |
| &nbsp;&nbsp;`<h5>` Article One         | Section 4: Article One           |
| &nbsp;&nbsp;`<h5>` Article Two         | Section 5: Article Two           |

**What is not split:**
- Headings *inside* `s_title` or `s_picture` snippets (they are structural, not article headings)
- Footer snippets (`s_footer_social`) — stripped entirely along with unsubscribe links
- Plain emails with no `data-snippet` tables — cleaned with unsubscribe-link stripping only, no section wrapping

## Configuration

No additional configuration is required. The module adds fields directly to the mailing form.

Users need access to both Email Marketing and Website Designer rights to publish mailings to the blog.

## License

LGPL-3 - See [LICENSE](https://www.gnu.org/licenses/lgpl-3.0.html)
