from odoo import models, fields, api
import requests

# 1. BẢNG DANH MỤC DỊCH VỤ CỐ ĐỊNH
class PetgoDichVu(models.Model):
    _name = 'petgo.dich_vu'
    _description = 'Danh mục Dịch vụ Spa'
    
    name = fields.Char(string="Tên dịch vụ (VD: Tắm cơ bản, Cắt tỉa)", required=True)
    gia_tien = fields.Float(string="Đơn giá (VNĐ)", required=True)
    thoi_gian = fields.Integer(string="Thời gian làm (Phút)")

# 2. BẢNG CHI TIẾT DỊCH VỤ TRONG 1 CA (Quan hệ N-1 với Ca làm việc)
class PetgoCongViecLine(models.Model):
    _name = 'petgo.cong_viec.line'
    _description = 'Chi tiết dịch vụ trong ca làm'

    cong_viec_id = fields.Many2one('petgo.cong_viec', string="Ca làm việc", ondelete='cascade')
    dich_vu_id = fields.Many2one('petgo.dich_vu', string="Dịch vụ chọn", required=True)
    gia_tien = fields.Float(string="Thành tiền", related='dich_vu_id.gia_tien', store=True)

# 3. BẢNG QUẢN LÝ CA LÀM VIỆC CHÍNH
class PetgoCongViec(models.Model):
    _name = 'petgo.cong_viec'
    _description = 'Quản lý ca làm việc Spa lưu động'
    _rec_name = 'tieu_de'

    tieu_de = fields.Char(string="Tiêu đề Ca làm", required=True)
    
    # 🔗 LIÊN KẾT MODULE KHÁCH HÀNG
    khach_hang_id = fields.Many2one('petgo.khach_hang', string="Khách hàng", required=True)
    
    # Tính năng thông minh: Thuộc tính domain giúp chỉ lọc ra thú cưng của đúng vị khách vừa chọn
    thu_cung_id = fields.Many2one('petgo.thu_cung', string="Thú cưng làm Dịch vụ", 
                                  domain="[('chu_pet_id', '=', khach_hang_id)]")
    
    # 🔗 LIÊN KẾT MODULE NHÂN SỰ
    nhan_vien_groomer_id = fields.Many2one('nhan_vien', string="Thợ Groomer thực hiện")
    kinh_nghiem_tho = fields.Text(string="Hồ sơ Năng lực Thợ", compute="_compute_kinh_nghiem", store=True)

    # Viết hàm tự động quét dữ liệu bằng cấp, lịch sử
    @api.depends('nhan_vien_groomer_id')
    def _compute_kinh_nghiem(self):
        for rec in self:
            if rec.nhan_vien_groomer_id:
                # 1. Quét danh sách chứng chỉ qua bảng trung gian
                ds_chung_chi = rec.nhan_vien_groomer_id.danh_sach_chung_chi_bang_cap_ids
                
                # Trích xuất tên chứng chỉ từ bảng gốc chung_chi_bang_cap_id
                ten_cac_chung_chi = [cc.chung_chi_bang_cap_id.ten_chung_chi_bang_cap for cc in ds_chung_chi if cc.chung_chi_bang_cap_id]
                chuoi_chung_chi = ", ".join(ten_cac_chung_chi) if ten_cac_chung_chi else "Chưa cập nhật chứng chỉ"
                
                # 2. Đếm số lượng lịch sử công tác
                ds_lich_su = rec.nhan_vien_groomer_id.lich_su_cong_tac_ids
                so_nam_kinh_nghiem = len(ds_lich_su)
                
                # 3. Gộp lại hiển thị
                rec.kinh_nghiem_tho = f"🎓 Bằng cấp: {chuoi_chung_chi}\n💼 Đã trải qua {so_nam_kinh_nghiem} vị trí công tác."
            else:
                rec.kinh_nghiem_tho = "Vui lòng chọn thợ để xem năng lực."
    
    ngay_hen = fields.Date(string="Ngày làm việc", default=fields.Date.today, required=True)
    
    trang_thai = fields.Selection([
        ('moi', 'Mới đặt lịch'),
        ('di_chuyen', 'Đang tới nhà khách'),
        ('dang_lam', 'Đang thực hiện Spa'),
        ('hoan_thanh', 'Hoàn thành')
    ], string="Trạng thái", default='moi')

    # Liên kết tới bảng Chi tiết dịch vụ để tạo Bill
    dich_vu_line_ids = fields.One2many('petgo.cong_viec.line', 'cong_viec_id', string="Các dịch vụ")
    tong_tien = fields.Float(string="Tổng hóa đơn", compute='_compute_tong_tien', store=True)

    danh_gia_sao = fields.Selection([
        ('1', '⭐ 1 Sao (Phạt 50k)'), ('2', '⭐⭐ 2 Sao (Phạt 20k)'), 
        ('3', '⭐⭐⭐ 3 Sao'), ('4', '⭐⭐⭐⭐ 4 Sao (Thưởng 20k)'), 
        ('5', '⭐⭐⭐⭐⭐ 5 Sao (Thưởng 50k)')
    ], string="Khách hàng Đánh giá")
    nhan_xet = fields.Text(string="Nhận xét của khách")
    mo_ta = fields.Text(string="Ghi chú & Tình trạng")
    noi_dung_ai_soan = fields.Text(string="AI Gợi ý")

    # Hàm tự động tính tổng hóa đơn
    @api.depends('dich_vu_line_ids.gia_tien')
    def _compute_tong_tien(self):
        for rec in self:
            rec.tong_tien = sum(line.gia_tien for line in rec.dich_vu_line_ids)

    # Khi đổi khách hàng -> Xóa trắng thú cưng cũ
    @api.onchange('khach_hang_id')
    def _onchange_khach_hang_id(self):
        self.thu_cung_id = False

    # Khi chọn thú cưng -> Lôi tình trạng sức khỏe từ Module Khách hàng sang
    @api.onchange('thu_cung_id')
    def _onchange_thu_cung_id(self):
        if self.thu_cung_id:
            tinh_trang = self.thu_cung_id.tinh_trang_pet or "Bình thường"
            suc_khoe = self.thu_cung_id.suc_khoe_pet or "Bình thường"
            self.mo_ta = f"--- CẢNH BÁO TỪ HỒ SƠ PET ---\n- Tình trạng: {tinh_trang}\n- Sức khỏe: {suc_khoe}\n\n(Ghi chú thợ đi ca: ...)"

    # ============ PHƯƠNG THỨC AI ============
    def action_tao_noi_dung_ai(self):
        for rec in self:
            ten_kh = rec.khach_hang_id.ten_khach_hang if rec.khach_hang_id else "Anh/Chị"
            ten_pet = rec.thu_cung_id.name if rec.thu_cung_id else "thú cưng"
            yeu_cau = rec.tieu_de
            ngay_hen = rec.ngay_hen if rec.ngay_hen else "sắp tới"
            
            prompt = f"Bạn là nhân viên PetGo Spa. Hãy viết 1 tin nhắn Zalo gửi khách '{ten_kh}'. Thông báo thợ đang trên đường đến làm dịch vụ '{yeu_cau}' cho bé '{ten_pet}' vào ngày {ngay_hen}."
            
            # Sử dụng API key của bạn
            api_key = "AIzaSyASqfWpF4vMT4YyF5stjfuvno89MRcgRaU"
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3.1-flash-lite:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            
            try:
                response = requests.post(url, headers=headers, json=data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    rec.noi_dung_ai_soan = result['candidates'][0]['content']['parts'][0]['text']
                else:
                    rec.noi_dung_ai_soan = f"Lỗi API: {response.status_code}"
            except Exception as e:
                rec.noi_dung_ai_soan = f"Lỗi kết nối: {str(e)}"
        
        return True