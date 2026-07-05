from odoo import models, fields

class HRLuongCoBan(models.Model):
    _name = 'hr_luong_co_ban'
    _description = 'Cấu hình lương cơ bản nhân viên'
    _rec_name = 'nhan_vien_id'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    # Lưu ý: Nếu module nhân sự cũ của bạn bảng nhan_vien không có trường ma_dinh_danh, hãy xóa tạm dòng dưới đây đi để tránh lỗi nhé.
    ma_dinh_danh = fields.Char("Mã định danh", related='nhan_vien_id.ma_dinh_danh', store=True)
    luong_co_ban = fields.Float("Lương cơ bản (VND)", required=True, default=0.0)
    phu_cap_an_trua = fields.Float("Phụ cấp ăn trưa", default=0.0)
    phu_cap_trach_nhiem = fields.Float("Phụ cấp trách nhiệm", default=0.0)
    ghi_chu = fields.Text("Ghi chú bổ sung")