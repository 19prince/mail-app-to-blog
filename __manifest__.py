{
    'name': 'Mailing to Blog',
    'version': '19.0.1.0.0',
    'category': 'Marketing/Email Marketing',
    'summary': 'Publish sent newsletters as draft blog posts',
    'description': """
Publish your email newsletters as blog posts with a single click.
Adds a "Publish to Blog" button to sent mailings that creates
a draft blog post from the newsletter content.
    """,
    'author': 'Community',
    'website': 'https://github.com/mm-odoo/mailing_to_blog',
    'license': 'LGPL-3',
    'depends': ['mass_mailing', 'website_blog'],
    'data': [
        'security/ir.model.access.xml',
        'views/mailing_mailing_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
