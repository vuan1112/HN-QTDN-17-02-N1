from odoo import models, fields, api
import requests
# 1. BẢNG DANH MỤC GIỐNG LOÀI
class PetgoGiongLoai(models.Model):
    _name = 'petgo.giong_loai'
    _description = 'Danh mục Giống loài thú cưng'

    name = fields.Char(string="Tên giống loài", required=True)
    loai = fields.Selection([('cho', 'Chó'), ('meo', 'Mèo')], string="Phân loại", required=True)
    ghi_chu = fields.Text(string="Đặc điểm chung")

# 2. BẢNG KHÁCH HÀNG (CRM)
class PetgoKhachHang(models.Model):
    _name = 'petgo.khach_hang'
    _description = 'Hồ sơ Khách hàng'
    _rec_name = 'ten_khach_hang'

    ma_khach_hang = fields.Char(string="Mã khách hàng", required=True, copy=False, default='Mới')
    ten_khach_hang = fields.Char(string="Tên chủ Pet", required=True)
    so_dien_thoai = fields.Char(string="Số điện thoại", required=True)
    dia_chi = fields.Char(string="Địa chỉ nhà")
    email = fields.Char(string="Email")
    dia_chi = fields.Char(string="Địa chỉ")

    loai_khach_hang = fields.Selection([
        ('ca_nhan', 'Cá nhân'), 
        ('cong_ty', 'Công ty')
    ], string="Loại khách hàng", default='ca_nhan')

    muc_thu_nhap = fields.Selection([
        ('0_20', '0-20 triệu/tháng'), 
        ('20_50', '20-50 triệu/tháng'), 
        ('50_70', '50-70 triệu/tháng'), 
        ('70_100', '70-100 triệu/tháng'), 
        ('100_plus', '100 triệu trở lên')
    ], string="Mức thu nhập")
    
    trang_thai = fields.Selection([
        ('moi', 'Mới'), 
        ('dang_hoat_dong', 'Đang hoạt động')
    ], string="Trạng thái", default='moi')
    
    tong_so_don_hang = fields.Integer(string="Tổng số đơn hàng", default=1)
    
    gioi_tinh = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')], string="Giới tính")
    
    nhom_do_tuoi = fields.Selection([
        ('0_20', '0-20 tuổi'), 
        ('20_30', '20-30 tuổi'), 
        ('30_40', '30-40 tuổi'), 
        ('40_50', '40-50 tuổi')
    ], string="Nhóm độ tuổi")

    # KẾT NỐI VỚI NHÂN SỰ VÀ THÚ CƯNG
    nhan_vien_cham_soc_id = fields.Many2one('nhan_vien', string="Nhân viên Telesale phụ trách")
    thu_cung_ids = fields.One2many('petgo.thu_cung', 'chu_pet_id', string="Danh sách Thú cưng")

    # 4 TRƯỜNG TỰ ĐỘNG HIỂN THỊ THÔNG TIN NHÂN SỰ
    phong_ban_nv = fields.Char(string="Phòng ban", compute='_compute_thong_tin_nv')
    chuc_vu_nv = fields.Char(string="Chức vụ", compute='_compute_thong_tin_nv')
    chi_tiet_cong_tac_nv = fields.Text(string="Lịch sử Công tác", compute='_compute_thong_tin_nv')
    chi_tiet_chung_chi_nv = fields.Text(string="Danh sách Bằng cấp", compute='_compute_thong_tin_nv')

    @api.depends('nhan_vien_cham_soc_id', 'nhan_vien_cham_soc_id.lich_su_cong_tac_ids', 'nhan_vien_cham_soc_id.danh_sach_chung_chi_bang_cap_ids')
    def _compute_thong_tin_nv(self):
        for rec in self:
            if rec.nhan_vien_cham_soc_id:
                # 1. Lấy thông tin chức vụ hiện tại (mới nhất)
                if rec.nhan_vien_cham_soc_id.lich_su_cong_tac_ids:
                    ls_moi_nhat = rec.nhan_vien_cham_soc_id.lich_su_cong_tac_ids[0]
                    rec.phong_ban_nv = ls_moi_nhat.don_vi_id.ten_don_vi if ls_moi_nhat.don_vi_id else "Chưa phân đơn vị"
                    rec.chuc_vu_nv = ls_moi_nhat.chuc_vu_id.ten_chuc_vu if ls_moi_nhat.chuc_vu_id else "Chưa có chức vụ"
                else:
                    rec.phong_ban_nv = "Chưa có thông tin"
                    rec.chuc_vu_nv = "Chưa có thông tin"
                
                # 2. Quét toàn bộ Lịch sử công tác
                ds_cong_tac = []
                for ls in rec.nhan_vien_cham_soc_id.lich_su_cong_tac_ids:
                    don_vi = ls.don_vi_id.ten_don_vi if ls.don_vi_id else '?'
                    chuc_vu = ls.chuc_vu_id.ten_chuc_vu if ls.chuc_vu_id else '?'
                    loai = ls.loai_chuc_vu if ls.loai_chuc_vu else 'Chính'
                    ds_cong_tac.append(f"👉 {chuc_vu} tại {don_vi} ({loai})")
                
                rec.chi_tiet_cong_tac_nv = "\n".join(ds_cong_tac) if ds_cong_tac else "Chưa có lịch sử công tác."

                # 3. Quét toàn bộ Bằng cấp/Chứng chỉ
                ds_bang_cap = []
                for bc in rec.nhan_vien_cham_soc_id.danh_sach_chung_chi_bang_cap_ids:
                    ten_bang = bc.chung_chi_bang_cap_id.ten_chung_chi_bang_cap if bc.chung_chi_bang_cap_id else '?'
                    ds_bang_cap.append(f"🎓 {ten_bang}")
                
                rec.chi_tiet_chung_chi_nv = "\n".join(ds_bang_cap) if ds_bang_cap else "Chưa cập nhật bằng cấp."
            else:
                rec.phong_ban_nv = "Chưa có thông tin"
                rec.chuc_vu_nv = "Chưa có thông tin"
                rec.chi_tiet_cong_tac_nv = "Vui lòng chọn nhân viên Telesale."
                rec.chi_tiet_chung_chi_nv = "Vui lòng chọn nhân viên Telesale."

# 3. BẢNG HỒ SƠ THÚ CƯNG
class PetgoThuCung(models.Model):
    _name = 'petgo.thu_cung'
    _description = 'Hồ sơ Thú cưng chi tiết'

    name = fields.Char(string="Tên bé Pet", required=True)
    chu_pet_id = fields.Many2one('petgo.khach_hang', string="Chủ sở hữu", ondelete='cascade')
    giong_loai_id = fields.Many2one('petgo.giong_loai', string="Giống loài")
    can_nang = fields.Float(string="Cân nặng (kg)")
    tinh_trang_pet = fields.Char(string="Tình trạng (Lông, Da...)")
    suc_khoe_pet = fields.Char(string="Tình trạng Sức khỏe")

#4 danh gia
from odoo import models, fields, api

class PetgoFeedback(models.Model):
    _name = 'petgo.feedback'
    _description = 'Phản hồi của khách hàng'
    _rec_name = 'name'

    ma_phan_hoi = fields.Char(string="Mã phản hồi", required=True, copy=False, readonly=True, default='Mới')
    name = fields.Char(string="Tên phản hồi", required=True)
    
    khach_hang_id = fields.Many2one('petgo.khach_hang', string="Khách hàng", required=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên")
    
    comment = fields.Text(string="Nội dung phản hồi")
    date = fields.Datetime(string="Ngày phản hồi", default=fields.Datetime.now)
    
    rating = fields.Selection([
        ('1 sao', '1 sao'), 
        ('2 sao', '2 sao'), 
        ('3 sao', '3 sao'), 
        ('4 sao', '4 sao'), 
        ('5 sao', '5 sao')
    ], string="Đánh giá", required=True)

    @api.model
    def create(self, vals):
        record = super(PetgoFeedback, self).create(vals)
        # Chỉ giữ lại logic tự động cấp mã (Ví dụ: FB_001)
        if record.ma_phan_hoi == 'Mới':
            record.ma_phan_hoi = f"FB_{record.id:03d}"
        return record