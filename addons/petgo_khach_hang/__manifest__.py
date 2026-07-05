{
   'name': 'Khách hàng',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Quản lý thông tin chủ vật nuôi và thú cưng',
    'depends': ['base', 'nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/khach_hang_views.xml',
    ],
    'installable': True,
    'application': True,
}