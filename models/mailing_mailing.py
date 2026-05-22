import re

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_sanitize


class MailingMailing(models.Model):
    _inherit = 'mailing.mailing'

    blog_id = fields.Many2one(
        'blog.blog',
        string='Blog',
        help='Select a blog to publish this mailing to.',
    )
    blog_post_id = fields.Many2one(
        'blog.post',
        string='Blog Post',
        readonly=True,
        copy=False,
        help='The blog post created from this mailing.',
    )
    tag_ids = fields.Many2many(
        'blog.tag',
        'mailing_mailing_blog_tag_rel',
        'mailing_id',
        'tag_id',
        string='Blog Tags',
    )

    _sql_constraints = [
        ('blog_post_unique', 'UNIQUE(blog_post_id)',
         'A mailing can only have one blog post.'),
    ]

    @api.onchange('blog_id')
    def _onchange_blog_id_tags(self):
        if self.blog_id and not self.tag_ids:
            tag = self.env['blog.tag'].search([('name', '=ilike', 'newsletter')], limit=1)
            if not tag:
                tag = self.env['blog.tag'].sudo().create({'name': 'Newsletter'})
            self.tag_ids = tag

    def action_publish_to_blog(self):
        self.ensure_one()
        if not self.env.user.has_group('website.group_website_designer'):
            raise AccessError(_('You need Website Designer rights to publish to a blog.'))
        if self.state != 'done':
            raise UserError(_('You can only publish sent mailings to the blog.'))
        if not self.blog_id:
            raise UserError(_('Please select a target blog in the Settings tab before publishing.'))
        if self.blog_post_id:
            raise UserError(_('A blog post has already been created from this mailing.'))

        newsletter_tag = self.env['blog.tag'].sudo().search(
            [('name', '=ilike', 'newsletter')], limit=1
        )
        if not newsletter_tag:
            newsletter_tag = self.env['blog.tag'].sudo().create({'name': 'Newsletter'})
        final_tags = self.tag_ids | newsletter_tag

        blog_post = self.env['blog.post'].with_user(self.env.user).sudo().create({
            'name': self.subject,
            'blog_id': self.blog_id.id,
            'content': self._prepare_blog_content(),
            'website_published': False,
            'author_id': self.env.user.partner_id.id,
            'tag_ids': [(6, 0, final_tags.ids)],
        })
        self.blog_post_id = blog_post.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'blog.post',
            'res_id': blog_post.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_blog_post(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'blog.post',
            'res_id': self.blog_post_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _prepare_blog_content(self):
        self.ensure_one()
        content = html_sanitize(self.body_html or '')
        return self._strip_unsubscribe_links(content)

    def _strip_unsubscribe_links(self, html_content):
        """Remove <a> tags with unsubscribe hrefs — email-specific, broken on the web."""
        if not html_content:
            return html_content
        return re.sub(
            r'<a\b[^>]*\bhref=["\'][^"\']*unsubscribe[^"\']*["\'][^>]*>.*?</a>',
            '',
            html_content,
            flags=re.IGNORECASE | re.DOTALL,
        )
