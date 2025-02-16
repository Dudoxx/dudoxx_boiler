{
    'name': 'Dudoxx Boiler',
    'version': '16.0.0.1',
    'author': 'Walid Boudabbous',
    'website': 'https://www.dudoxx.com',
    'license': 'LGPL-3',
    'category': 'Tools',
    'summary': 'Reference implementation of Odoo features and best practices',
    'description': '''
        This module serves as a reference implementation demonstrating Odoo features and best practices.
        It includes:
        - Model relationships (many2many)
        - Standard views (tree, form, search)
        - Security implementation
        - Best practices in code organization
    ''',
    'depends': ['base', 'mail', 'hr'],
    'assets': {
        'web.assets_backend': [
            'dudoxx_boiler/static/src/css/style.css',
        ],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/sequences.xml',
        'data/sample_data.xml',

        # Views - Client
        'views/client/client_kanban_view.xml',
        'views/client/client_tree_view.xml',
        'views/client/client_form_view.xml',
        'views/client/client_search_view.xml',
        'views/client/client_actions.xml',

        # Views - Document
        'views/client_document/client_document_tree_view.xml',
        'views/client_document/client_document_form_view.xml',
        'views/client_document/client_document_kanban_view.xml',
        'views/client_document/client_document_search_view.xml',
        'views/client_document/client_document_actions.xml',
        'views/menus/main_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
