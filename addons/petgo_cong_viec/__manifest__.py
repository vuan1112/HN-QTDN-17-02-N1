{
'name': 'Công việc',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Điều phối lịch hẹn Spa và tích hợp AI',
    # Sửa lại dòng này cho chuẩn tên thư mục
    'depends': ['base', 'nhan_su', 'petgo_khach_hang', 'quan_ly_cham_cong_luong'],
    'data': [
        'security/ir.model.access.csv',
        'views/cong_viec_views.xml',
    ],
    'installable': True,
    'application': True,
}
