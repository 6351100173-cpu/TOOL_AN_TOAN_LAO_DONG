# ============================================================
# nguy_co.py
# MODULE QUẢN LÝ NGUY CƠ AN TOÀN LAO ĐỘNG
# ============================================================
from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import date, datetime
# ============================================================
# 1. KHỞI TẠO BLUEPRINT
# ============================================================
nguy_co_bp = Blueprint("nguy_co", __name__)
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
# 4. TẠO / KIỂM TRA BẢNG NGUY CƠ
# ============================================================
def tao_bang_nguy_co():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nguy_co (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_cn TEXT,
            ngay_phat_hien TEXT NOT NULL,
            thoi_gian TEXT,
            khu_vuc TEXT NOT NULL,
            loai_nguy_co TEXT NOT NULL,
            mo_ta TEXT NOT NULL,
            muc_do TEXT DEFAULT 'Trung bình',
            trang_thai TEXT DEFAULT 'Chưa xử lý',
            nguoi_phat_hien TEXT,
            bien_phap_xu_ly TEXT,
            nguoi_phu_trach TEXT,
            han_xu_ly TEXT,
            ghi_chu TEXT,
            ghi_chu_xu_ly TEXT
        )
    """)
    cursor.execute("PRAGMA table_info(nguy_co)")
    cac_cot_hien_tai = [
        row["name"]
        for row in cursor.fetchall()
    ]
    cac_cot_can_co = {
        "ma_cn": "TEXT",
        "ngay_phat_hien": "TEXT",
        "thoi_gian": "TEXT",
        "khu_vuc": "TEXT",
        "loai_nguy_co": "TEXT",
        "mo_ta": "TEXT",
        "muc_do": "TEXT DEFAULT 'Trung bình'",
        "trang_thai": "TEXT DEFAULT 'Chưa xử lý'",
        "nguoi_phat_hien": "TEXT",
        "bien_phap_xu_ly": "TEXT",
        "nguoi_phu_trach": "TEXT",
        "han_xu_ly": "TEXT",
        "ghi_chu": "TEXT",
        "ghi_chu_xu_ly": "TEXT"
    }
    for ten_cot, kieu_du_lieu in cac_cot_can_co.items():
        if ten_cot not in cac_cot_hien_tai:
            cursor.execute(
                f"ALTER TABLE nguy_co "
                f"ADD COLUMN {ten_cot} {kieu_du_lieu}"
            )
    conn.commit()
    conn.close()
tao_bang_nguy_co()
# ============================================================
# 5. DANH SÁCH NGUY CƠ
# ============================================================
@nguy_co_bp.route("/nguy-co")
def danh_sach_nguy_co():
    ngay_chon = request.args.get(
        "ngay",
        ""
    ).strip()
    if not ngay_chon:
        ngay_chon = date.today().strftime(
            "%Y-%m-%d"
        )
    conn = get_db()
    cursor = conn.cursor()
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
        WHERE n.ngay_phat_hien = ?
        ORDER BY
            CASE n.muc_do
                WHEN 'Cao' THEN 1
                WHEN 'Trung bình' THEN 2
                WHEN 'Thấp' THEN 3
                ELSE 4
            END,
            n.thoi_gian DESC,
            n.id DESC
    """, (ngay_chon,))
    danh_sach = cursor.fetchall()
    cursor.execute("""
        SELECT
            ma_cn,
            ho_ten,
            bo_phan,
            cong_viec,
            trang_thai
        FROM cong_nhan
        ORDER BY id ASC
    """)
    danh_sach_cong_nhan = cursor.fetchall()
    stats = {
        "tong_nguy_co": len(danh_sach),
        "chua_xu_ly": 0,
        "dang_xu_ly": 0,
        "da_xu_ly": 0,
        "nguy_co_cao": 0
    }
    for item in danh_sach:
        if item["trang_thai"] == "Chưa xử lý":
            stats["chua_xu_ly"] += 1
        elif item["trang_thai"] == "Đang xử lý":
            stats["dang_xu_ly"] += 1
        elif item["trang_thai"] == "Đã xử lý":
            stats["da_xu_ly"] += 1
        if item["muc_do"] == "Cao":
            stats["nguy_co_cao"] += 1
    conn.close()
    return render_template(
        "nguy_co.html",
        danh_sach=danh_sach,
        danh_sach_cong_nhan=danh_sach_cong_nhan,
        stats=stats,
        ngay_chon=ngay_chon
    )
# ============================================================
# 6. THÊM NGUY CƠ
# ============================================================
@nguy_co_bp.route(
    "/them-nguy-co",
    methods=["POST"]
)
def them_nguy_co():
    ma_cn = request.form.get(
        "ma_cn",
        ""
    ).strip()
    ngay_phat_hien = request.form.get(
        "ngay_phat_hien",
        ""
    ).strip()
    thoi_gian = request.form.get(
        "thoi_gian",
        ""
    ).strip()
    khu_vuc = request.form.get(
        "khu_vuc",
        ""
    ).strip()
    loai_nguy_co = request.form.get(
        "loai_nguy_co",
        ""
    ).strip()
    mo_ta = request.form.get(
        "mo_ta",
        ""
    ).strip()
    muc_do = request.form.get(
        "muc_do",
        "Trung bình"
    ).strip()
    nguoi_phat_hien = request.form.get(
        "nguoi_phat_hien",
        ""
    ).strip()
    ghi_chu = request.form.get(
        "ghi_chu",
        ""
    ).strip()
    if not ngay_phat_hien:
        ngay_phat_hien = date.today().strftime(
            "%Y-%m-%d"
        )
    if not thoi_gian:
        thoi_gian = datetime.now().strftime(
            "%H:%M"
        )
    if muc_do not in [
        "Thấp",
        "Trung bình",
        "Cao"
    ]:
        muc_do = "Trung bình"
    if (
        not ma_cn
        or not khu_vuc
        or not loai_nguy_co
        or not mo_ta
    ):
        return redirect(
            url_for(
                "nguy_co.danh_sach_nguy_co",
                ngay=ngay_phat_hien
            )
        )
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ma_cn
        FROM cong_nhan
        WHERE ma_cn = ?
    """, (ma_cn,))
    cong_nhan = cursor.fetchone()
    if cong_nhan is None:
        conn.close()
        return redirect(
            url_for(
                "nguy_co.danh_sach_nguy_co",
                ngay=ngay_phat_hien
            )
        )
    cursor.execute("""
        INSERT INTO nguy_co (
            ma_cn,
            ngay_phat_hien,
            thoi_gian,
            khu_vuc,
            loai_nguy_co,
            mo_ta,
            muc_do,
            trang_thai,
            nguoi_phat_hien,
            bien_phap_xu_ly,
            nguoi_phu_trach,
            han_xu_ly,
            ghi_chu,
            ghi_chu_xu_ly
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ma_cn,
        ngay_phat_hien,
        thoi_gian,
        khu_vuc,
        loai_nguy_co,
        mo_ta,
        muc_do,
        "Chưa xử lý",
        nguoi_phat_hien,
        "",
        "",
        "",
        ghi_chu,
        ""
    ))
    conn.commit()
    conn.close()
    return redirect(
        url_for(
            "nguy_co.danh_sach_nguy_co",
            ngay=ngay_phat_hien
        )
    )
# ============================================================
# 7. CẬP NHẬT / XỬ LÝ NGUY CƠ
# ============================================================
@nguy_co_bp.route(
    "/xu-ly-nguy-co/<int:nguy_co_id>",
    methods=["POST"]
)
def xu_ly_nguy_co(nguy_co_id):
    ngay_chon = request.form.get(
        "ngay_chon",
        ""
    ).strip()
    ma_cn = request.form.get(
        "ma_cn",
        ""
    ).strip()
    muc_do = request.form.get(
        "muc_do",
        "Trung bình"
    ).strip()
    bien_phap_xu_ly = request.form.get(
        "bien_phap_xu_ly",
        ""
    ).strip()
    nguoi_phu_trach = request.form.get(
        "nguoi_phu_trach",
        ""
    ).strip()
    han_xu_ly = request.form.get(
        "han_xu_ly",
        ""
    ).strip()
    trang_thai = request.form.get(
        "trang_thai",
        "Chưa xử lý"
    ).strip()
    ghi_chu_xu_ly = request.form.get(
        "ghi_chu_xu_ly",
        ""
    ).strip()
    if muc_do not in [
        "Thấp",
        "Trung bình",
        "Cao"
    ]:
        muc_do = "Trung bình"
    if trang_thai not in [
        "Chưa xử lý",
        "Đang xử lý",
        "Đã xử lý"
    ]:
        trang_thai = "Chưa xử lý"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            ngay_phat_hien,
            ma_cn
        FROM nguy_co
        WHERE id = ?
    """, (nguy_co_id,))
    nguy_co = cursor.fetchone()
    if nguy_co is None:
        conn.close()
        return redirect(
            url_for(
                "nguy_co.danh_sach_nguy_co"
            )
        )
    ngay_phat_hien = nguy_co["ngay_phat_hien"]
    if not ma_cn:
        ma_cn = nguy_co["ma_cn"] or ""
    if ma_cn:
        cursor.execute("""
            SELECT ma_cn
            FROM cong_nhan
            WHERE ma_cn = ?
        """, (ma_cn,))
        cong_nhan = cursor.fetchone()
        if cong_nhan is None:
            ma_cn = nguy_co["ma_cn"] or ""
    cursor.execute("""
        UPDATE nguy_co
        SET
            ma_cn = ?,
            muc_do = ?,
            bien_phap_xu_ly = ?,
            nguoi_phu_trach = ?,
            han_xu_ly = ?,
            trang_thai = ?,
            ghi_chu_xu_ly = ?
        WHERE id = ?
    """, (
        ma_cn,
        muc_do,
        bien_phap_xu_ly,
        nguoi_phu_trach,
        han_xu_ly,
        trang_thai,
        ghi_chu_xu_ly,
        nguy_co_id
    ))
    conn.commit()
    conn.close()
    if not ngay_chon:
        ngay_chon = ngay_phat_hien
    return redirect(
        url_for(
            "nguy_co.danh_sach_nguy_co",
            ngay=ngay_chon
        )
    )
# ============================================================
# 8. XÓA NGUY CƠ
# ============================================================
@nguy_co_bp.route(
    "/xoa-nguy-co/<int:nguy_co_id>",
    methods=["POST"]
)
def xoa_nguy_co(nguy_co_id):
    ngay_chon = request.form.get(
        "ngay_chon",
        ""
    ).strip()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ngay_phat_hien
        FROM nguy_co
        WHERE id = ?
    """, (nguy_co_id,))
    nguy_co = cursor.fetchone()
    if nguy_co is None:
        conn.close()
        return redirect(
            url_for(
                "nguy_co.danh_sach_nguy_co",
                ngay=ngay_chon
            )
        )
    ngay_phat_hien = nguy_co[
        "ngay_phat_hien"
    ]
    cursor.execute("""
        DELETE FROM nguy_co
        WHERE id = ?
    """, (nguy_co_id,))
    conn.commit()
    conn.close()
    if not ngay_chon:
        ngay_chon = ngay_phat_hien
    return redirect(
        url_for(
            "nguy_co.danh_sach_nguy_co",
            ngay=ngay_chon
        )
    )
# ============================================================
# 9. BIÊN BẢN / PHIẾU GHI NHẬN NGUY CƠ
# ============================================================
@nguy_co_bp.route(
    "/bien-ban-nguy-co/<int:nguy_co_id>"
)
def bien_ban_nguy_co(nguy_co_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            n.id,
            printf('NC%03d', n.id) AS ma_nguy_co,
            n.ma_cn,
            c.ho_ten,
            c.bo_phan,
            c.cong_viec,
            c.so_dien_thoai,
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
        WHERE n.id = ?
    """, (nguy_co_id,))
    nguy_co = cursor.fetchone()
    conn.close()
    if nguy_co is None:
        return redirect(
            url_for(
                "nguy_co.danh_sach_nguy_co"
            )
        )
    return render_template(
        "bien_ban_nguy_co.html",
        nguy_co=nguy_co
    )