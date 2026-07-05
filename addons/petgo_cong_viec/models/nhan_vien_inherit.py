from odoo import models, fields, api

class NhanVienInherit(models.Model):
    _inherit = 'nhan_vien'

    diem_danh_gia_tb = fields.Float(string="Điểm Đánh giá (Trung bình)", compute="_compute_danh_gia")
    tien_thuong_phat = fields.Float(string="Tiền Thưởng/Phạt (VNĐ)", compute="_compute_danh_gia")
    luong_sau_danh_gia = fields.Float(string="Lương sau Đánh giá (VNĐ)", compute="_compute_danh_gia")

    def _compute_danh_gia(self):
        for nv in self:
            # 1. Thu thập tất cả các ca làm việc của nhân viên này để tính sao
            ca_lam = self.env['petgo.cong_viec'].search([
                ('nhan_vien_groomer_id', '=', nv.id),
                ('danh_gia_sao', '!=', False)
            ])
            
            tong_thuong = 0
            tong_sao = 0
            count = len(ca_lam)
            
            for ca in ca_lam:
                sao = int(ca.danh_gia_sao)
                tong_sao += sao
                if sao == 5: tong_thuong += 50000
                elif sao == 4: tong_thuong += 20000
                elif sao == 2: tong_thuong -= 20000
                elif sao == 1: tong_thuong -= 50000
            
            nv.tien_thuong_phat = tong_thuong
            nv.diem_danh_gia_tb = (tong_sao / count) if count > 0 else 0
            
            # 2. ĐỒNG BỘ MÔ-ĐUN TÍNH LƯƠNG: Lấy tổng lương gốc
            # Thay 'luong_co_ban' bằng tên trường lương thật trong module Tính Lương của bạn
            luong_goc = nv.quan_ly_cham_cong_luong if hasattr(nv, 'quan_ly_cham_cong_luong') else 0.0
            
            # 3. Tính toán số tiền thực nhận cuối cùng sau khi áp số sao
            nv.luong_sau_danh_gia = luong_goc + nv.tien_thuong_phat