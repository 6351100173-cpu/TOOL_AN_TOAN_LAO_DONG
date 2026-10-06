# ============================================================
# bao_cao.py
# MODULE BÁO CÁO AN TOÀN LAO ĐỘNG
# ============================================================
from flask import Blueprint, render_template, request
import sqlite3
import os
import calendar
from datetime import date, datetime, timedelta
# ============================================================
# 1. KHỞI TẠO BLUEPRINT
# ============================================================
bao_cao_bp = Blueprint("bao_cao", __name__)
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
# 4. CHUYỂN CHUỖI THÀNH NGÀY
# ============================================================
def chuyen_ngay(gia_tri):
    try:
        return datetime.strptime(gia_tri, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return date.today()
# ============================================================
# 5. XÁC ĐỊNH KHOẢNG THỜI GIAN
# ============================================================
def lay_khoang_thoi_gian(che_do, gia_tri):
    hom_nay = date.today()
    if che_do == "ngay":
        ngay_chon = chuyen_ngay(gia_tri)
        return ngay_chon, ngay_chon
    if che_do == "tuan":
        ngay_chon = chuyen_ngay(gia_tri)
        ngay_dau = ngay_chon - timedelta(
            days=ngay_chon.weekday()
        )
        ngay_cuoi = ngay_dau + timedelta(days=6)
        return ngay_dau, ngay_cuoi
    if che_do == "nam":
        try:
            nam = int(gia_tri)
        except (ValueError, TypeError):
            nam = hom_nay.year
        return (
            date(nam, 1, 1),
            date(nam, 12, 31)
        )
    try:
        nam, thang = map(
            int,
            gia_tri.split("-")
        )
    except (ValueError, AttributeError):
        nam = hom_nay.year
        thang = hom_nay.month
    ngay_cuoi_thang = calendar.monthrange(
        nam,
        thang
    )[1]
    return (
        date(nam, thang, 1),
        date(nam, thang, ngay_cuoi_thang)
    )
# ============================================================
# 6. GIÁ TRỊ THỜI GIAN MẶC ĐỊNH
# ============================================================
def lay_gia_tri_mac_dinh(che_do):
    hom_nay = date.today()
    if che_do == "ngay":
        return hom_nay.isoformat()
    if che_do == "tuan":
        return hom_nay.isoformat()
    if che_do == "nam":
        return str(hom_nay.year)
    return hom_nay.strftime("%Y-%m")
# ============================================================
# 7. HIỂN THỊ KHOẢNG THỜI GIAN
# ============================================================
def dinh_dang_khoang_thoi_gian(
    ngay_dau,
    ngay_cuoi
):
    if ngay_dau == ngay_cuoi:
        return ngay_dau.strftime("%d/%m/%Y")
    return (
        ngay_dau.strftime("%d/%m/%Y")
        + " - "
        + ngay_cuoi.strftime("%d/%m/%Y")
    )
# ============================================================
# 8. ROUTE BÁO CÁO
# ============================================================
@bao_cao_bp.route("/bao-cao")
def bao_cao():
    che_do = request.args.get(
        "che_do",
        "thang"
    )
    if che_do not in [
        "ngay",
        "tuan",
        "thang",
        "nam"
    ]:
        che_do = "thang"
    thoi_gian = request.args.get(
        "thoi_gian"
    )
    if not thoi_gian:
        thoi_gian = lay_gia_tri_mac_dinh(
            che_do
        )
    loai_bao_cao = request.args.get(
        "loai",
        "tong-hop"
    )
    if loai_bao_cao not in [
        "tong-hop",
        "cong-nhan",
        "bao-ho",
        "vi-pham",
        "nguy-co"
    ]:
        loai_bao_cao = "tong-hop"
    ngay_dau, ngay_cuoi = (
        lay_khoang_thoi_gian(
            che_do,
            thoi_gian
        )
    )
    ngay_dau_sql = ngay_dau.isoformat()
    ngay_cuoi_sql = ngay_cuoi.isoformat()
    conn = get_db()
    cursor = conn.cursor()
    # ========================================================
    # 9. CÔNG NHÂN
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
    """)
    tong_cong_nhan = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
        WHERE trang_thai = 'Đang làm việc'
    """)
    cong_nhan_dang_lam = cursor.fetchone()[0]
    cursor.execute("""
        SELECT
            ma_cn,
            ho_ten,
            bo_phan,
            cong_viec,
            so_dien_thoai,
            trang_thai
        FROM cong_nhan
        ORDER BY ma_cn
    """)
    danh_sach_cong_nhan = cursor.fetchall()
    # ========================================================
    # 10. KIỂM TRA BẢO HỘ
    # Chỉ lấy lần kiểm tra mới nhất của mỗi công nhân mỗi ngày
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM kiem_tra_bao_ho AS kt
        WHERE kt.ngay_kiem_tra BETWEEN ? AND ?
        AND kt.id = (
            SELECT MAX(kt2.id)
            FROM kiem_tra_bao_ho AS kt2
            WHERE kt2.ma_cn = kt.ma_cn
            AND kt2.ngay_kiem_tra = kt.ngay_kiem_tra
        )
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    tong_kiem_tra = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM kiem_tra_bao_ho AS kt
        WHERE kt.ngay_kiem_tra BETWEEN ? AND ?
        AND kt.ket_qua = 'Đạt'
        AND kt.id = (
            SELECT MAX(kt2.id)
            FROM kiem_tra_bao_ho AS kt2
            WHERE kt2.ma_cn = kt.ma_cn
            AND kt2.ngay_kiem_tra = kt.ngay_kiem_tra
        )
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    bao_ho_dat = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM kiem_tra_bao_ho AS kt
        WHERE kt.ngay_kiem_tra BETWEEN ? AND ?
        AND kt.ket_qua = 'Không đạt'
        AND kt.id = (
            SELECT MAX(kt2.id)
            FROM kiem_tra_bao_ho AS kt2
            WHERE kt2.ma_cn = kt.ma_cn
            AND kt2.ngay_kiem_tra = kt.ngay_kiem_tra
        )
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    bao_ho_khong_dat = cursor.fetchone()[0]
    cursor.execute("""
        SELECT
            kt.id,
            kt.ma_cn,
            c.ho_ten,
            c.bo_phan,
            c.cong_viec,
            kt.ngay_kiem_tra,
            kt.mu_bao_ho,
            kt.ao_phan_quang,
            kt.giay_bao_ho,
            kt.gang_tay,
            kt.kinh_bao_ho,
            kt.day_an_toan,
            kt.ket_qua,
            kt.nguoi_kiem_tra,
            kt.ghi_chu
        FROM kiem_tra_bao_ho AS kt
        LEFT JOIN cong_nhan AS c
        ON kt.ma_cn = c.ma_cn
        WHERE kt.ngay_kiem_tra BETWEEN ? AND ?
        AND kt.id = (
            SELECT MAX(kt2.id)
            FROM kiem_tra_bao_ho AS kt2
            WHERE kt2.ma_cn = kt.ma_cn
            AND kt2.ngay_kiem_tra = kt.ngay_kiem_tra
        )
        ORDER BY
            kt.ngay_kiem_tra DESC,
            kt.ma_cn
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    danh_sach_bao_ho = cursor.fetchall()
    # ========================================================
    # 11. VI PHẠM
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM vi_pham
        WHERE ngay_vi_pham BETWEEN ? AND ?
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    tong_vi_pham = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM vi_pham
        WHERE ngay_vi_pham BETWEEN ? AND ?
        AND trang_thai = 'Chưa xử lý'
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    vi_pham_chua_xu_ly = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM vi_pham
        WHERE ngay_vi_pham BETWEEN ? AND ?
        AND trang_thai = 'Đã xử lý'
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    vi_pham_da_xu_ly = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM vi_pham
        WHERE ngay_vi_pham BETWEEN ? AND ?
        AND muc_do = 'Cao'
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    vi_pham_cao = cursor.fetchone()[0]
    cursor.execute("""
        SELECT
            v.id,
            v.ma_cn,
            c.ho_ten,
            c.bo_phan,
            c.cong_viec,
            v.ngay_vi_pham,
            v.thoi_gian,
            v.noi_dung,
            v.muc_do,
            v.trang_thai,
            v.hinh_thuc_xu_ly,
            v.so_tien_phat,
            v.nguoi_lap,
            v.ghi_chu
        FROM vi_pham AS v
        LEFT JOIN cong_nhan AS c
        ON v.ma_cn = c.ma_cn
        WHERE v.ngay_vi_pham BETWEEN ? AND ?
        ORDER BY
            v.ngay_vi_pham DESC,
            v.id DESC
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    danh_sach_vi_pham = cursor.fetchall()
    # ========================================================
    # 12. NGUY CƠ
    # ========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    tong_nguy_co = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        AND muc_do = 'Cao'
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    nguy_co_cao = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        AND trang_thai = 'Chưa xử lý'
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    nguy_co_chua_xu_ly = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        AND trang_thai = 'Đang xử lý'
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    nguy_co_dang_xu_ly = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        AND trang_thai = 'Đã xử lý'
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    nguy_co_da_xu_ly = cursor.fetchone()[0]
    cursor.execute("""
        SELECT
            n.id,
            printf('NC%03d', n.id) AS ma_nguy_co,
            n.ma_cn,
            c.ho_ten,
            c.bo_phan,
            c.cong_viec,
            n.ngay_phat_hien,
            n.thoi_gian,
            n.khu_vuc,
            n.loai_nguy_co,
            n.mo_ta,
            n.muc_do,
            n.trang_thai,
            n.nguoi_phat_hien,
            n.bien_phap_xu_ly,
            n.nguoi_phu_trach,
            n.han_xu_ly,
            n.ghi_chu,
            n.ghi_chu_xu_ly
        FROM nguy_co AS n
        LEFT JOIN cong_nhan AS c
        ON n.ma_cn = c.ma_cn
        WHERE n.ngay_phat_hien BETWEEN ? AND ?
        ORDER BY
            n.ngay_phat_hien DESC,
            n.id DESC
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    danh_sach_nguy_co = cursor.fetchall()
    # ========================================================
    # 13. THỐNG KÊ VI PHẠM THEO MỨC ĐỘ
    # ========================================================
    cursor.execute("""
        SELECT
            muc_do,
            COUNT(*) AS so_luong
        FROM vi_pham
        WHERE ngay_vi_pham BETWEEN ? AND ?
        GROUP BY muc_do
        ORDER BY so_luong DESC
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    vi_pham_theo_muc_do = cursor.fetchall()
    # ========================================================
    # 14. THỐNG KÊ NGUY CƠ THEO MỨC ĐỘ
    # ========================================================
    cursor.execute("""
        SELECT
            muc_do,
            COUNT(*) AS so_luong
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        GROUP BY muc_do
        ORDER BY so_luong DESC
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    nguy_co_theo_muc_do = cursor.fetchall()
    # ========================================================
    # 15. NGUY CƠ THEO KHU VỰC
    # ========================================================
    cursor.execute("""
        SELECT
            khu_vuc,
            COUNT(*) AS so_luong
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        GROUP BY khu_vuc
        ORDER BY so_luong DESC, khu_vuc
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    nguy_co_theo_khu_vuc = cursor.fetchall()
    # ========================================================
    # 16. TỔNG TIỀN PHẠT
    # ========================================================
    cursor.execute("""
        SELECT COALESCE(
            SUM(so_tien_phat),
            0
        )
        FROM vi_pham
        WHERE ngay_vi_pham BETWEEN ? AND ?
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    tong_tien_phat = cursor.fetchone()[0]
    # ========================================================
    # 17. TÍNH TỶ LỆ
    # ========================================================
    if tong_kiem_tra > 0:
        ty_le_bao_ho_dat = round(
            bao_ho_dat /
            tong_kiem_tra *
            100,
            1
        )
    else:
        ty_le_bao_ho_dat = 0
    if tong_nguy_co > 0:
        ty_le_nguy_co_da_xu_ly = round(
            nguy_co_da_xu_ly /
            tong_nguy_co *
            100,
            1
        )
    else:
        ty_le_nguy_co_da_xu_ly = 0
    if tong_vi_pham > 0:
        ty_le_vi_pham_da_xu_ly = round(
            vi_pham_da_xu_ly /
            tong_vi_pham *
            100,
            1
        )
    else:
        ty_le_vi_pham_da_xu_ly = 0
    # ========================================================
    # 18. DỮ LIỆU TỔNG HỢP
    # ========================================================
    stats = {
        "tong_cong_nhan": tong_cong_nhan,
        "cong_nhan_dang_lam": cong_nhan_dang_lam,
        "tong_kiem_tra": tong_kiem_tra,
        "bao_ho_dat": bao_ho_dat,
        "bao_ho_khong_dat": bao_ho_khong_dat,
        "ty_le_bao_ho_dat": ty_le_bao_ho_dat,
        "tong_vi_pham": tong_vi_pham,
        "vi_pham_chua_xu_ly": vi_pham_chua_xu_ly,
        "vi_pham_da_xu_ly": vi_pham_da_xu_ly,
        "vi_pham_cao": vi_pham_cao,
        "ty_le_vi_pham_da_xu_ly": ty_le_vi_pham_da_xu_ly,
        "tong_tien_phat": tong_tien_phat,
        "tong_nguy_co": tong_nguy_co,
        "nguy_co_cao": nguy_co_cao,
        "nguy_co_chua_xu_ly": nguy_co_chua_xu_ly,
        "nguy_co_dang_xu_ly": nguy_co_dang_xu_ly,
        "nguy_co_da_xu_ly": nguy_co_da_xu_ly,
        "ty_le_nguy_co_da_xu_ly": ty_le_nguy_co_da_xu_ly
    }
    conn.close()
    # ========================================================
    # 19. HIỂN THỊ TEMPLATE
    # ========================================================
    return render_template(
        "bao_cao.html",
        stats=stats,
        danh_sach_cong_nhan=danh_sach_cong_nhan,
        danh_sach_bao_ho=danh_sach_bao_ho,
        danh_sach_vi_pham=danh_sach_vi_pham,
        danh_sach_nguy_co=danh_sach_nguy_co,
        vi_pham_theo_muc_do=vi_pham_theo_muc_do,
        nguy_co_theo_muc_do=nguy_co_theo_muc_do,
        nguy_co_theo_khu_vuc=nguy_co_theo_khu_vuc,
        che_do=che_do,
        thoi_gian=thoi_gian,
        loai_bao_cao=loai_bao_cao,
        ngay_dau=ngay_dau_sql,
        ngay_cuoi=ngay_cuoi_sql,
        khoang_thoi_gian=dinh_dang_khoang_thoi_gian(
            ngay_dau,
            ngay_cuoi
        )
    )