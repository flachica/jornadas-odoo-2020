{
    'name' : 'Odoo Blockchain proxy',
    'author': "Guadaltech Soluciones Tecnologicas <http://www.guadaltech.es>",
    'version' : '0.0.1',
    'summary': 'Tools for communicate with Blockchain network',
    'sequence': 10,
    'description': """
Tools for communicate with Blockchain network
====================
This provide severals tools for communicate with Blockchain network throught Sawtooth SDK
    """,
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'views/blockchain_reader_views.xml'
    ],
    'external_dependencies': {
        'python': ['pyyaml', 'protobuf', 'sawtooth-sdk'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
