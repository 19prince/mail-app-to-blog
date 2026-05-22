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

## Configuration

No additional configuration is required. The module adds fields directly to the mailing form.

Users need access to both Email Marketing and Website Designer rights to publish mailings to the blog.

## License

LGPL-3 - See [LICENSE](https://www.gnu.org/licenses/lgpl-3.0.html)
