# ============================================================
# ATLD.py
# FILE CHÍNH KHỞI ĐỘNG HỆ THỐNG QUẢN LÝ AN TOÀN LAO ĐỘNG
# ============================================================
from flask import Flask, render_template
from cong_nhan import cong_nhan_bp
from bao_ho import bao_ho_bp
from vi_pham import vi_pham_bp
from nguy_co import nguy_co_bp
from thong_ke import thong_ke_bp
from bao_cao import bao_cao_bp
import sqlite3
import os
from datetime import date
# ============================================================
# 1. KHỞI TẠO ỨNG DỤNG FLASK
# ============================================================
app = Flask(__name__)
# ============================================================
# 2. ĐƯỜNG DẪN DATABASE
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "atld.db")
# ============================================================
# 3. KẾT NỐI DATABASE
# ============================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
# ============================================================
# 4. ĐĂNG KÝ CÁC MODULE
# ============================================================
app.register_blueprint(cong_nhan_bp)
app.register_blueprint(bao_ho_bp)
app.register_blueprint(vi_pham_bp)
app.register_blueprint(nguy_co_bp)
app.register_blueprint(thong_ke_bp)
app.register_blueprint(bao_cao_bp)
# ============================================================
# 5. LẤY THỐNG KÊ CHO TRANG CHỦ
# ============================================================
def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()
    ngay_hom_nay = date.today().isoformat()
    # ========================================================
    # TỔNG SỐ CÔNG NHÂN
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
    """)
    tong_cong_nhan = cursor.fetchone()[0]
    # ========================================================
    # CÔNG NHÂN ĐANG LÀM VIỆC
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
        WHERE trang_thai = 'Đang làm việc'
    """)
    dang_lam_viec = cursor.fetchone()[0]
    # ========================================================
    # SỐ CÔNG NHÂN ĐÃ KIỂM TRA BHLĐ HÔM NAY
    # CHỈ LẤY LẦN KIỂM TRA CUỐI CÙNG CỦA MỖI CÔNG NHÂN
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM kiem_tra_bao_ho AS kt
        WHERE kt.ngay_kiem_tra = ?
        AND kt.id = (
            SELECT MAX(kt2.id)
            FROM kiem_tra_bao_ho AS kt2
            WHERE kt2.ma_cn = kt.ma_cn
            AND kt2.ngay_kiem_tra = kt.ngay_kiem_tra
        )
    """, (ngay_hom_nay,))
    da_kiem_tra = cursor.fetchone()[0]
    # ========================================================
    # SỐ KIỂM TRA BHLĐ ĐẠT HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM kiem_tra_bao_ho AS kt
        WHERE kt.ngay_kiem_tra = ?
        AND kt.ket_qua = 'Đạt'
        AND kt.id = (
            SELECT MAX(kt2.id)
            FROM kiem_tra_bao_ho AS kt2
            WHERE kt2.ma_cn = kt.ma_cn
            AND kt2.ngay_kiem_tra = kt.ngay_kiem_tra
        )
    """, (ngay_hom_nay,))
    bao_ho_dat = cursor.fetchone()[0]
    # ========================================================
    # SỐ KIỂM TRA BHLĐ KHÔNG ĐẠT HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM kiem_tra_bao_ho AS kt
        WHERE kt.ngay_kiem_tra = ?
        AND kt.ket_qua = 'Không đạt'
        AND kt.id = (
            SELECT MAX(kt2.id)
            FROM kiem_tra_bao_ho AS kt2
            WHERE kt2.ma_cn = kt.ma_cn
            AND kt2.ngay_kiem_tra = kt.ngay_kiem_tra
        )
    """, (ngay_hom_nay,))
    bao_ho_khong_dat = cursor.fetchone()[0]
    # ========================================================
    # TỔNG VI PHẠM HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM vi_pham
        WHERE ngay_vi_pham = ?
    """, (ngay_hom_nay,))
    vi_pham = cursor.fetchone()[0]
    # ========================================================
    # VI PHẠM CHƯA XỬ LÝ HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM vi_pham
        WHERE ngay_vi_pham = ?
        AND trang_thai = 'Chưa xử lý'
    """, (ngay_hom_nay,))
    vi_pham_chua_xu_ly = cursor.fetchone()[0]
    # ========================================================
    # VI PHẠM ĐÃ XỬ LÝ HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM vi_pham
        WHERE ngay_vi_pham = ?
        AND trang_thai = 'Đã xử lý'
    """, (ngay_hom_nay,))
    vi_pham_da_xu_ly = cursor.fetchone()[0]
    # ========================================================
    # TỔNG NGUY CƠ HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien = ?
    """, (ngay_hom_nay,))
    tong_nguy_co = cursor.fetchone()[0]
    # ========================================================
    # NGUY CƠ MỨC CAO HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien = ?
        AND muc_do = 'Cao'
    """, (ngay_hom_nay,))
    nguy_co_cao = cursor.fetchone()[0]
    # ========================================================
    # NGUY CƠ CHƯA XỬ LÝ HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien = ?
        AND trang_thai = 'Chưa xử lý'
    """, (ngay_hom_nay,))
    nguy_co_chua_xu_ly = cursor.fetchone()[0]
    # ========================================================
    # NGUY CƠ ĐANG XỬ LÝ HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien = ?
        AND trang_thai = 'Đang xử lý'
    """, (ngay_hom_nay,))
    nguy_co_dang_xu_ly = cursor.fetchone()[0]
    # ========================================================
    # NGUY CƠ ĐÃ XỬ LÝ HÔM NAY
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien = ?
        AND trang_thai = 'Đã xử lý'
    """, (ngay_hom_nay,))
    nguy_co_da_xu_ly = cursor.fetchone()[0]
    # ========================================================
    # TỶ LỆ HOÀN THÀNH KIỂM TRA BHLĐ
    # ========================================================
    if dang_lam_viec > 0:
        ty_le_kiem_tra = round(
            (da_kiem_tra / dang_lam_viec) * 100
        )
    else:
        ty_le_kiem_tra = 0
    ty_le_kiem_tra = min(ty_le_kiem_tra, 100)
    # ========================================================
    # TỶ LỆ BHLĐ ĐẠT
    # ========================================================
    if da_kiem_tra > 0:
        ty_le_bao_ho_dat = round(
            (bao_ho_dat / da_kiem_tra) * 100
        )
    else:
        ty_le_bao_ho_dat = 0
    ty_le_bao_ho_dat = min(ty_le_bao_ho_dat, 100)
    # ========================================================
    # TỶ LỆ TUÂN THỦ QUY ĐỊNH
    # DỰA TRÊN SỐ CÔNG NHÂN ĐANG LÀM VIỆC VÀ VI PHẠM HÔM NAY
    # ========================================================
    if dang_lam_viec > 0:
        ty_le_tuan_thu = round(
            ((dang_lam_viec - min(vi_pham, dang_lam_viec)) / dang_lam_viec) * 100
        )
    else:
        ty_le_tuan_thu = 100
    ty_le_tuan_thu = max(0, min(ty_le_tuan_thu, 100))
    # ========================================================
    # TỶ LỆ KIỂM SOÁT NGUY CƠ
    # ========================================================
    if tong_nguy_co > 0:
        ty_le_kiem_soat_nguy_co = round(
            (nguy_co_da_xu_ly / tong_nguy_co) * 100
        )
    else:
        ty_le_kiem_soat_nguy_co = 100
    ty_le_kiem_soat_nguy_co = max(
        0,
        min(ty_le_kiem_soat_nguy_co, 100)
    )
    # ========================================================
    # ĐIỂM AN TOÀN TỔNG HỢP
    # 40% BHLĐ + 30% TUÂN THỦ + 30% KIỂM SOÁT NGUY CƠ
    # ========================================================
    diem_an_toan = round(
        ty_le_bao_ho_dat * 0.4
        + ty_le_tuan_thu * 0.3
        + ty_le_kiem_soat_nguy_co * 0.3
    )
    diem_an_toan = max(0, min(diem_an_toan, 100))
    # ========================================================
    # XẾP LOẠI MỨC AN TOÀN
    # ========================================================
    if diem_an_toan >= 90:
        muc_an_toan = "RẤT TỐT"
    elif diem_an_toan >= 80:
        muc_an_toan = "TỐT"
    elif diem_an_toan >= 65:
        muc_an_toan = "KHÁ"
    elif diem_an_toan >= 50:
        muc_an_toan = "TRUNG BÌNH"
    else:
        muc_an_toan = "CẦN CẢI THIỆN"
    # ========================================================
    # NỘI DUNG HOẠT ĐỘNG KIỂM TRA BHLĐ
    # ========================================================
    if da_kiem_tra > 0:
        hoat_dong_bao_ho = (
            f"Đã kiểm tra {da_kiem_tra} công nhân trong ngày hôm nay"
        )
    else:
        hoat_dong_bao_ho = (
            "Chưa có lượt kiểm tra bảo hộ trong ngày hôm nay"
        )
    # ========================================================
    # NỘI DUNG HOẠT ĐỘNG VI PHẠM
    # ========================================================
    if vi_pham > 0:
        hoat_dong_vi_pham = (
            f"Ghi nhận {vi_pham} vi phạm, "
            f"{vi_pham_chua_xu_ly} trường hợp chưa xử lý"
        )
    else:
        hoat_dong_vi_pham = (
            "Chưa ghi nhận vi phạm trong ngày hôm nay"
        )
    # ========================================================
    # NỘI DUNG HOẠT ĐỘNG NGUY CƠ
    # ========================================================
    if tong_nguy_co > 0:
        hoat_dong_nguy_co = (
            f"Phát hiện {tong_nguy_co} nguy cơ, "
            f"trong đó có {nguy_co_cao} nguy cơ mức cao"
        )
    else:
        hoat_dong_nguy_co = (
            "Chưa ghi nhận nguy cơ trong ngày hôm nay"
        )
    # ========================================================
    # ĐÓNG DATABASE
    # ========================================================
    conn.close()
    # ========================================================
    # TRẢ DỮ LIỆU CHO TRANG CHỦ
    # ========================================================
    return {
        "tong_cong_nhan": tong_cong_nhan,
        "dang_lam_viec": dang_lam_viec,
        "da_kiem_tra": da_kiem_tra,
        "bao_ho_dat": bao_ho_dat,
        "bao_ho_khong_dat": bao_ho_khong_dat,
        "ty_le_kiem_tra": ty_le_kiem_tra,
        "ty_le_bao_ho_dat": ty_le_bao_ho_dat,
        "vi_pham": vi_pham,
        "tong_vi_pham": vi_pham,
        "vi_pham_chua_xu_ly": vi_pham_chua_xu_ly,
        "vi_pham_da_xu_ly": vi_pham_da_xu_ly,
        "tong_nguy_co": tong_nguy_co,
        "nguy_co_cao": nguy_co_cao,
        "nguy_co_chua_xu_ly": nguy_co_chua_xu_ly,
        "nguy_co_dang_xu_ly": nguy_co_dang_xu_ly,
        "nguy_co_da_xu_ly": nguy_co_da_xu_ly,
        "ty_le_tuan_thu": ty_le_tuan_thu,
        "ty_le_kiem_soat_nguy_co": ty_le_kiem_soat_nguy_co,
        "diem_an_toan": diem_an_toan,
        "muc_an_toan": muc_an_toan,
        "hoat_dong_bao_ho": hoat_dong_bao_ho,
        "hoat_dong_vi_pham": hoat_dong_vi_pham,
        "hoat_dong_nguy_co": hoat_dong_nguy_co,
        "ngay_hom_nay": ngay_hom_nay
    }
# ============================================================
# 6. TRANG CHỦ
# ============================================================
@app.route("/")
def home():
    stats = get_dashboard_stats()
    return render_template(
        "index.html",
        stats=stats
    )
# ============================================================
# 7. CHẠY CHƯƠNG TRÌNH
# ============================================================
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
