from odoo import fields, models, _
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

    _sql_constraints = [
        ('blog_post_unique', 'UNIQUE(blog_post_id)',
         'A mailing can only have one blog post.'),
    ]

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

        blog_post = self.env['blog.post'].with_user(self.env.user).sudo().create({
            'name': self.subject,
            'blog_id': self.blog_id.id,
            'content': self._prepare_blog_content(),
            'website_published': False,
            'author_id': self.env.user.partner_id.id,
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
        """Prepare mailing body HTML for blog display.

        Override this method to customize HTML cleanup
        (e.g., strip tracking pixels, unsubscribe footers).
        """
        self.ensure_one()
        return html_sanitize(self.body_html or '')
