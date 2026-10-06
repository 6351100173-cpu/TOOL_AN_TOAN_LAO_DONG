# ============================================================
# thong_ke.py
# MODULE THỐNG KÊ AN TOÀN LAO ĐỘNG
# ============================================================
from flask import Blueprint, render_template, request
import sqlite3
import os
import calendar
from datetime import date, datetime, timedelta
# ============================================================
# 1. KHỞI TẠO BLUEPRINT
# ============================================================
thong_ke_bp = Blueprint("thong_ke", __name__)
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
# 4. KIỂM TRA NGÀY HỢP LỆ
# ============================================================
def chuyen_ngay(gia_tri, mac_dinh=None):
    try:
        return datetime.strptime(
            gia_tri,
            "%Y-%m-%d"
        ).date()
    except (ValueError, TypeError):
        return mac_dinh or date.today()
# ============================================================
# 5. XÁC ĐỊNH KHOẢNG THỜI GIAN THỐNG KÊ
# ============================================================
def lay_khoang_thoi_gian(che_do, gia_tri):
    hom_nay = date.today()
    if che_do == "ngay":
        ngay_chon = chuyen_ngay(
            gia_tri,
            hom_nay
        )
        return ngay_chon, ngay_chon
    if che_do == "tuan":
        ngay_chon = chuyen_ngay(
            gia_tri,
            hom_nay
        )
        ngay_dau = ngay_chon - timedelta(
            days=ngay_chon.weekday()
        )
        ngay_cuoi = ngay_dau + timedelta(
            days=6
        )
        return ngay_dau, ngay_cuoi
    if che_do == "thang":
        try:
            if gia_tri:
                nam, thang = map(
                    int,
                    gia_tri.split("-")
                )
            else:
                nam = hom_nay.year
                thang = hom_nay.month
        except (ValueError, TypeError):
            nam = hom_nay.year
            thang = hom_nay.month
        ngay_cuoi_thang = calendar.monthrange(
            nam,
            thang
        )[1]
        ngay_dau = date(
            nam,
            thang,
            1
        )
        ngay_cuoi = date(
            nam,
            thang,
            ngay_cuoi_thang
        )
        return ngay_dau, ngay_cuoi
    if che_do == "nam":
        try:
            nam = int(gia_tri)
        except (ValueError, TypeError):
            nam = hom_nay.year
        ngay_dau = date(
            nam,
            1,
            1
        )
        ngay_cuoi = date(
            nam,
            12,
            31
        )
        return ngay_dau, ngay_cuoi
    return hom_nay, hom_nay
# ============================================================
# 6. TẠO GIÁ TRỊ MẶC ĐỊNH CHO BỘ LỌC
# ============================================================
def lay_gia_tri_mac_dinh(che_do):
    hom_nay = date.today()
    if che_do in [
        "ngay",
        "tuan"
    ]:
        return hom_nay.isoformat()
    if che_do == "thang":
        return hom_nay.strftime(
            "%Y-%m"
        )
    if che_do == "nam":
        return str(
            hom_nay.year
        )
    return hom_nay.isoformat()
# ============================================================
# 7. ĐỊNH DẠNG KHOẢNG THỜI GIAN
# ============================================================
def dinh_dang_khoang_thoi_gian(
    ngay_dau,
    ngay_cuoi
):
    if ngay_dau == ngay_cuoi:
        return ngay_dau.strftime(
            "%d/%m/%Y"
        )
    return (
        ngay_dau.strftime("%d/%m/%Y")
        + " - "
        + ngay_cuoi.strftime("%d/%m/%Y")
    )
# ============================================================
# 8. TẠO NHÃN CHO BIỂU ĐỒ XU HƯỚNG
# ============================================================
def tao_nhan_bieu_do(
    che_do,
    ngay_dau,
    ngay_cuoi
):
    nhan = []
    moc = []
    if che_do == "ngay":
        nhan.append(
            ngay_dau.strftime("%d/%m")
        )
        moc.append(
            (
                ngay_dau.isoformat(),
                ngay_dau.isoformat()
            )
        )
        return nhan, moc
    if che_do == "tuan":
        ten_thu = [
            "Thứ 2",
            "Thứ 3",
            "Thứ 4",
            "Thứ 5",
            "Thứ 6",
            "Thứ 7",
            "Chủ nhật"
        ]
        ngay_hien_tai = ngay_dau
        vi_tri = 0
        while ngay_hien_tai <= ngay_cuoi:
            nhan.append(
                ten_thu[vi_tri]
                + " "
                + ngay_hien_tai.strftime(
                    "%d/%m"
                )
            )
            moc.append(
                (
                    ngay_hien_tai.isoformat(),
                    ngay_hien_tai.isoformat()
                )
            )
            ngay_hien_tai += timedelta(
                days=1
            )
            vi_tri += 1
        return nhan, moc
    if che_do == "thang":
        ngay_hien_tai = ngay_dau
        while ngay_hien_tai <= ngay_cuoi:
            nhan.append(
                ngay_hien_tai.strftime(
                    "%d"
                )
            )
            moc.append(
                (
                    ngay_hien_tai.isoformat(),
                    ngay_hien_tai.isoformat()
                )
            )
            ngay_hien_tai += timedelta(
                days=1
            )
        return nhan, moc
    if che_do == "nam":
        for thang in range(1, 13):
            dau_thang = date(
                ngay_dau.year,
                thang,
                1
            )
            cuoi_thang = date(
                ngay_dau.year,
                thang,
                calendar.monthrange(
                    ngay_dau.year,
                    thang
                )[1]
            )
            nhan.append(
                "Tháng " + str(thang)
            )
            moc.append(
                (
                    dau_thang.isoformat(),
                    cuoi_thang.isoformat()
                )
            )
        return nhan, moc
    return nhan, moc
# ============================================================
# 9. ĐẾM DỮ LIỆU THEO TỪNG MỐC BIỂU ĐỒ
# ============================================================
def dem_theo_moc(
    cursor,
    bang,
    cot_ngay,
    moc
):
    ket_qua = []
    for ngay_dau, ngay_cuoi in moc:
        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {bang}
            WHERE {cot_ngay} BETWEEN ? AND ?
            """,
            (
                ngay_dau,
                ngay_cuoi
            )
        )
        ket_qua.append(
            cursor.fetchone()[0]
        )
    return ket_qua
# ============================================================
# 10. TRANG THỐNG KÊ
# ============================================================
@thong_ke_bp.route("/thong-ke")
def thong_ke():
    che_do = request.args.get(
        "che_do",
        "thang"
    ).strip().lower()
    if che_do not in [
        "ngay",
        "tuan",
        "thang",
        "nam"
    ]:
        che_do = "thang"
    gia_tri = request.args.get(
        "thoi_gian",
        ""
    ).strip()
    if not gia_tri:
        gia_tri = lay_gia_tri_mac_dinh(
            che_do
        )
    ngay_dau, ngay_cuoi = lay_khoang_thoi_gian(
        che_do,
        gia_tri
    )
    ngay_dau_sql = ngay_dau.isoformat()
    ngay_cuoi_sql = ngay_cuoi.isoformat()
    conn = get_db()
    cursor = conn.cursor()
    # ========================================================
    # 11. TỔNG CÔNG NHÂN
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
    # ========================================================
    # 12. THỐNG KÊ KIỂM TRA BẢO HỘ
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
    da_kiem_tra = cursor.fetchone()[0]
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
    if da_kiem_tra > 0:
        ty_le_dat_bao_ho = round(
            (
                bao_ho_dat
                / da_kiem_tra
            ) * 100,
            1
        )
    else:
        ty_le_dat_bao_ho = 0
    # ========================================================
    # 13. THỐNG KÊ VI PHẠM
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
        AND muc_do = 'Cao'
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    vi_pham_cao = cursor.fetchone()[0]
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
    # ========================================================
    # 14. THỐNG KÊ NGUY CƠ
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
    if tong_nguy_co > 0:
        ty_le_nguy_co_da_xu_ly = round(
            (
                nguy_co_da_xu_ly
                / tong_nguy_co
            ) * 100,
            1
        )
    else:
        ty_le_nguy_co_da_xu_ly = 0
    # ========================================================
    # 15. BIỂU ĐỒ XU HƯỚNG VI PHẠM VÀ NGUY CƠ
    # ========================================================
    nhan_xu_huong, moc_xu_huong = tao_nhan_bieu_do(
        che_do,
        ngay_dau,
        ngay_cuoi
    )
    du_lieu_vi_pham = dem_theo_moc(
        cursor,
        "vi_pham",
        "ngay_vi_pham",
        moc_xu_huong
    )
    du_lieu_nguy_co = dem_theo_moc(
        cursor,
        "nguy_co",
        "ngay_phat_hien",
        moc_xu_huong
    )
    # ========================================================
    # 16. BIỂU ĐỒ VI PHẠM THEO NỘI DUNG
    # ========================================================
    cursor.execute("""
        SELECT
            noi_dung,
            COUNT(*) AS so_luong
        FROM vi_pham
        WHERE ngay_vi_pham BETWEEN ? AND ?
        GROUP BY noi_dung
        ORDER BY so_luong DESC, noi_dung ASC
        LIMIT 8
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    vi_pham_theo_loai_rows = cursor.fetchall()
    vi_pham_labels = [
        row["noi_dung"]
        for row in vi_pham_theo_loai_rows
    ]
    vi_pham_values = [
        row["so_luong"]
        for row in vi_pham_theo_loai_rows
    ]
    # ========================================================
    # 17. BIỂU ĐỒ NGUY CƠ THEO LOẠI
    # ========================================================
    cursor.execute("""
        SELECT
            loai_nguy_co,
            COUNT(*) AS so_luong
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        GROUP BY loai_nguy_co
        ORDER BY so_luong DESC, loai_nguy_co ASC
        LIMIT 8
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    nguy_co_theo_loai_rows = cursor.fetchall()
    nguy_co_labels = [
        row["loai_nguy_co"]
        for row in nguy_co_theo_loai_rows
    ]
    nguy_co_values = [
        row["so_luong"]
        for row in nguy_co_theo_loai_rows
    ]
    # ========================================================
    # 18. TOP 5 CÔNG NHÂN CÓ NHIỀU VI PHẠM
    # ========================================================
    cursor.execute("""
        SELECT
            vp.ma_cn,
            COALESCE(cn.ho_ten, 'Chưa xác định') AS ho_ten,
            COALESCE(cn.bo_phan, '-') AS bo_phan,
            COUNT(*) AS so_luong
        FROM vi_pham AS vp
        LEFT JOIN cong_nhan AS cn
            ON vp.ma_cn = cn.ma_cn
        WHERE vp.ngay_vi_pham BETWEEN ? AND ?
        GROUP BY
            vp.ma_cn,
            cn.ho_ten,
            cn.bo_phan
        ORDER BY so_luong DESC, vp.ma_cn ASC
        LIMIT 5
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    top_vi_pham = [
        dict(row)
        for row in cursor.fetchall()
    ]
    # ========================================================
    # 19. TOP 5 LOẠI NGUY CƠ
    # ========================================================
    cursor.execute("""
        SELECT
            loai_nguy_co,
            COUNT(*) AS so_luong
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        GROUP BY loai_nguy_co
        ORDER BY so_luong DESC, loai_nguy_co ASC
        LIMIT 5
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    top_nguy_co = [
        dict(row)
        for row in cursor.fetchall()
    ]
    # ========================================================
    # 20. THỐNG KÊ THEO MỨC ĐỘ NGUY CƠ
    # ========================================================
    cursor.execute("""
        SELECT
            muc_do,
            COUNT(*) AS so_luong
        FROM nguy_co
        WHERE ngay_phat_hien BETWEEN ? AND ?
        GROUP BY muc_do
    """, (
        ngay_dau_sql,
        ngay_cuoi_sql
    ))
    muc_do_nguy_co = {
        "Thấp": 0,
        "Trung bình": 0,
        "Cao": 0
    }
    for row in cursor.fetchall():
        if row["muc_do"] in muc_do_nguy_co:
            muc_do_nguy_co[
                row["muc_do"]
            ] = row["so_luong"]
    # ========================================================
    # 21. GÓI DỮ LIỆU THẺ THỐNG KÊ
    # ========================================================
    stats = {
        "tong_cong_nhan": tong_cong_nhan,
        "cong_nhan_dang_lam": cong_nhan_dang_lam,
        "da_kiem_tra": da_kiem_tra,
        "bao_ho_dat": bao_ho_dat,
        "bao_ho_khong_dat": bao_ho_khong_dat,
        "ty_le_dat_bao_ho": ty_le_dat_bao_ho,
        "tong_vi_pham": tong_vi_pham,
        "vi_pham_cao": vi_pham_cao,
        "vi_pham_chua_xu_ly": vi_pham_chua_xu_ly,
        "vi_pham_da_xu_ly": vi_pham_da_xu_ly,
        "tong_nguy_co": tong_nguy_co,
        "nguy_co_cao": nguy_co_cao,
        "nguy_co_chua_xu_ly": nguy_co_chua_xu_ly,
        "nguy_co_dang_xu_ly": nguy_co_dang_xu_ly,
        "nguy_co_da_xu_ly": nguy_co_da_xu_ly,
        "ty_le_nguy_co_da_xu_ly": ty_le_nguy_co_da_xu_ly
    }
    # ========================================================
    # 22. DỮ LIỆU BIỂU ĐỒ
    # ========================================================
    charts = {
        "xu_huong_labels": nhan_xu_huong,
        "xu_huong_vi_pham": du_lieu_vi_pham,
        "xu_huong_nguy_co": du_lieu_nguy_co,
        "trang_thai_nguy_co_labels": [
            "Chưa xử lý",
            "Đang xử lý",
            "Đã xử lý"
        ],
        "trang_thai_nguy_co_values": [
            nguy_co_chua_xu_ly,
            nguy_co_dang_xu_ly,
            nguy_co_da_xu_ly
        ],
        "vi_pham_labels": vi_pham_labels,
        "vi_pham_values": vi_pham_values,
        "nguy_co_labels": nguy_co_labels,
        "nguy_co_values": nguy_co_values,
        "muc_do_nguy_co_labels": [
            "Thấp",
            "Trung bình",
            "Cao"
        ],
        "muc_do_nguy_co_values": [
            muc_do_nguy_co["Thấp"],
            muc_do_nguy_co["Trung bình"],
            muc_do_nguy_co["Cao"]
        ]
    }
    conn.close()
    # ========================================================
    # 23. HIỂN THỊ TRANG THỐNG KÊ
    # ========================================================
    return render_template(
        "thong_ke.html",
        stats=stats,
        charts=charts,
        top_vi_pham=top_vi_pham,
        top_nguy_co=top_nguy_co,
        che_do=che_do,
        thoi_gian=gia_tri,
        ngay_dau=ngay_dau_sql,
        ngay_cuoi=ngay_cuoi_sql,
        khoang_thoi_gian=dinh_dang_khoang_thoi_gian(
            ngay_dau,
            ngay_cuoi
        )
    )