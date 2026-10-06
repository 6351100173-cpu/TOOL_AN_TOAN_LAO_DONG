from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import date, datetime
# =========================================================
# BLUEPRINT VI PHẠM
# =========================================================
vi_pham_bp = Blueprint("vi_pham", __name__)
# =========================================================
# DATABASE CHUNG
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "atld.db")
# =========================================================
# KẾT NỐI DATABASE
# =========================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
# =========================================================
# TẠO BẢNG VI PHẠM
# =========================================================
def init_vi_pham_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vi_pham (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_cn TEXT NOT NULL,
            ngay_vi_pham TEXT NOT NULL,
            thoi_gian TEXT,
            noi_dung TEXT NOT NULL,
            muc_do TEXT DEFAULT 'Trung bình',
            trang_thai TEXT DEFAULT 'Chưa xử lý',
            hinh_thuc_xu_ly TEXT,
            so_tien_phat REAL DEFAULT 0,
            nguoi_lap TEXT,
            ghi_chu TEXT
        )
    """)
    conn.commit()
    conn.close()
# =========================================================
# KHỞI TẠO BẢNG
# =========================================================
init_vi_pham_db()
# =========================================================
# HÀM ĐỊNH DẠNG TIỀN VND
# =========================================================
def dinh_dang_vnd(so_tien):
    try:
        so_tien = float(so_tien or 0)
        if so_tien <= 0:
            return ""
        return f"{so_tien:,.0f}".replace(",", ".") + " VND"
    except (ValueError, TypeError):
        return ""
# =========================================================
# HÀM ĐỊNH DẠNG NGÀY
# =========================================================
def dinh_dang_ngay(ngay):
    try:
        return datetime.strptime(
            ngay,
            "%Y-%m-%d"
        ).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return ngay or "-"
# =========================================================
# TRANG DANH SÁCH VI PHẠM
# =========================================================
@vi_pham_bp.route("/vi-pham")
def danh_sach_vi_pham():
    ngay_chon = request.args.get(
        "ngay",
        date.today().isoformat()
    )
    conn = get_db()
    cursor = conn.cursor()
    # =====================================================
    # DANH SÁCH CÔNG NHÂN
    # =====================================================
    cursor.execute("""
        SELECT
            id,
            ma_cn,
            ho_ten,
            bo_phan,
            cong_viec,
            so_dien_thoai,
            trang_thai
        FROM cong_nhan
        WHERE trang_thai = 'Đang làm việc'
        ORDER BY ma_cn
    """)
    workers = cursor.fetchall()
    # =====================================================
    # DANH SÁCH VI PHẠM
    # =====================================================
    cursor.execute("""
        SELECT
            vp.id,
            vp.ma_cn,
            cn.ho_ten,
            cn.bo_phan,
            cn.cong_viec,
            cn.so_dien_thoai,
            vp.ngay_vi_pham,
            vp.thoi_gian,
            vp.noi_dung,
            vp.muc_do,
            vp.trang_thai,
            vp.hinh_thuc_xu_ly,
            vp.so_tien_phat,
            vp.nguoi_lap,
            vp.ghi_chu
        FROM vi_pham vp
        LEFT JOIN cong_nhan cn
            ON vp.ma_cn = cn.ma_cn
        WHERE vp.ngay_vi_pham = ?
        ORDER BY vp.id DESC
    """, (ngay_chon,))
    violations = cursor.fetchall()
    # =====================================================
    # THỐNG KÊ
    # =====================================================
    tong_vi_pham = len(violations)
    chua_xu_ly = sum(
        1 for item in violations
        if item["trang_thai"] == "Chưa xử lý"
    )
    da_xu_ly = sum(
        1 for item in violations
        if item["trang_thai"] == "Đã xử lý"
    )
    nghiem_trong = sum(
        1 for item in violations
        if item["muc_do"] == "Cao"
    )
    stats = {
        "tong_vi_pham": tong_vi_pham,
        "chua_xu_ly": chua_xu_ly,
        "da_xu_ly": da_xu_ly,
        "nghiem_trong": nghiem_trong
    }
    conn.close()
    return render_template(
        "vi_pham.html",
        violations=violations,
        workers=workers,
        ngay_chon=ngay_chon,
        stats=stats
    )
# =========================================================
# GHI NHẬN VI PHẠM MỚI
# =========================================================
@vi_pham_bp.route("/them-vi-pham", methods=["POST"])
def them_vi_pham():
    ma_cn = request.form.get(
        "ma_cn",
        ""
    ).strip()
    ngay_vi_pham = request.form.get(
        "ngay_vi_pham",
        date.today().isoformat()
    ).strip()
    thoi_gian = request.form.get(
        "thoi_gian",
        ""
    ).strip()
    noi_dung = request.form.get(
        "noi_dung",
        ""
    ).strip()
    muc_do = request.form.get(
        "muc_do",
        "Trung bình"
    ).strip()
    nguoi_lap = request.form.get(
        "nguoi_lap",
        "Giám sát"
    ).strip()
    ghi_chu = request.form.get(
        "ghi_chu",
        ""
    ).strip()
    if not ma_cn or not noi_dung:
        return redirect(
            url_for(
                "vi_pham.danh_sach_vi_pham",
                ngay=ngay_vi_pham
            )
        )
    if not thoi_gian:
        thoi_gian = datetime.now().strftime("%H:%M")
    if muc_do not in [
        "Thấp",
        "Trung bình",
        "Cao"
    ]:
        muc_do = "Trung bình"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ma_cn
        FROM cong_nhan
        WHERE ma_cn = ?
        LIMIT 1
    """, (ma_cn,))
    worker = cursor.fetchone()
    if worker is None:
        conn.close()
        return redirect(
            url_for(
                "vi_pham.danh_sach_vi_pham",
                ngay=ngay_vi_pham
            )
        )
    cursor.execute("""
        INSERT INTO vi_pham (
            ma_cn,
            ngay_vi_pham,
            thoi_gian,
            noi_dung,
            muc_do,
            trang_thai,
            hinh_thuc_xu_ly,
            so_tien_phat,
            nguoi_lap,
            ghi_chu
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ma_cn,
        ngay_vi_pham,
        thoi_gian,
        noi_dung,
        muc_do,
        "Chưa xử lý",
        None,
        0,
        nguoi_lap,
        ghi_chu
    ))
    conn.commit()
    conn.close()
    return redirect(
        url_for(
            "vi_pham.danh_sach_vi_pham",
            ngay=ngay_vi_pham
        )
    )
# =========================================================
# CẬP NHẬT / XỬ LÝ VI PHẠM
# =========================================================
@vi_pham_bp.route(
    "/xu-ly-vi-pham/<int:vi_pham_id>",
    methods=["POST"]
)
def xu_ly_vi_pham(vi_pham_id):
    ngay_vi_pham = request.form.get(
        "ngay_vi_pham",
        date.today().isoformat()
    ).strip()
    muc_do = request.form.get(
        "muc_do",
        "Trung bình"
    ).strip()
    hinh_thuc_xu_ly = request.form.get(
        "hinh_thuc_xu_ly",
        ""
    ).strip()
    so_tien_phat_raw = request.form.get(
        "so_tien_phat",
        "0"
    ).strip()
    ghi_chu = request.form.get(
        "ghi_chu",
        ""
    ).strip()
    trang_thai = request.form.get(
        "trang_thai",
        "Chưa xử lý"
    ).strip()
    if muc_do not in [
        "Thấp",
        "Trung bình",
        "Cao"
    ]:
        muc_do = "Trung bình"
    if trang_thai not in [
        "Chưa xử lý",
        "Đã xử lý"
    ]:
        trang_thai = "Chưa xử lý"
    # =====================================================
    # XỬ LÝ TIỀN PHẠT VND
    # Cho phép nhập: 500, 500000, 1.000.000...
    # =====================================================
    try:
        so_tien_chuan = (
            so_tien_phat_raw
            .replace(".", "")
            .replace(",", "")
            .replace("VND", "")
            .replace("vnd", "")
            .strip()
        )
        if so_tien_chuan:
            so_tien_phat = float(so_tien_chuan)
        else:
            so_tien_phat = 0
        if so_tien_phat < 0:
            so_tien_phat = 0
    except ValueError:
        so_tien_phat = 0
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
            ghi_chu
        FROM vi_pham
        WHERE id = ?
        LIMIT 1
    """, (vi_pham_id,))
    violation = cursor.fetchone()
    if violation:
        # =================================================
        # GIỮ DẤU VI PHẠM TỰ ĐỘNG TỪ BẢO HỘ
        # =================================================
        ghi_chu_cu = violation["ghi_chu"] or ""
        marker = "[TỰ ĐỘNG TỪ KIỂM TRA BẢO HỘ]"
        if ghi_chu_cu.startswith(marker):
            if ghi_chu:
                ghi_chu_luu = marker + " " + ghi_chu
            else:
                ghi_chu_luu = marker
        else:
            ghi_chu_luu = ghi_chu
        cursor.execute("""
            UPDATE vi_pham
            SET muc_do = ?,
                hinh_thuc_xu_ly = ?,
                so_tien_phat = ?,
                ghi_chu = ?,
                trang_thai = ?
            WHERE id = ?
        """, (
            muc_do,
            hinh_thuc_xu_ly,
            so_tien_phat,
            ghi_chu_luu,
            trang_thai,
            vi_pham_id
        ))
        conn.commit()
    conn.close()
    return redirect(
        url_for(
            "vi_pham.danh_sach_vi_pham",
            ngay=ngay_vi_pham
        )
    )
# =========================================================
# XUẤT BIÊN BẢN VI PHẠM
# =========================================================
@vi_pham_bp.route(
    "/bien-ban-vi-pham/<int:vi_pham_id>"
)
def bien_ban_vi_pham(vi_pham_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            vp.id,
            vp.ma_cn,
            cn.ho_ten,
            cn.bo_phan,
            cn.cong_viec,
            cn.so_dien_thoai,
            vp.ngay_vi_pham,
            vp.thoi_gian,
            vp.noi_dung,
            vp.muc_do,
            vp.trang_thai,
            vp.hinh_thuc_xu_ly,
            vp.so_tien_phat,
            vp.nguoi_lap,
            vp.ghi_chu
        FROM vi_pham vp
        LEFT JOIN cong_nhan cn
            ON vp.ma_cn = cn.ma_cn
        WHERE vp.id = ?
        LIMIT 1
    """, (vi_pham_id,))
    violation = cursor.fetchone()
    conn.close()
    if violation is None:
        return redirect(
            url_for(
                "vi_pham.danh_sach_vi_pham"
            )
        )
    # =====================================================
    # TẠO SỐ BIÊN BẢN
    # =====================================================
    ngay_ma = (
        violation["ngay_vi_pham"] or ""
    ).replace("-", "")
    so_bien_ban = (
        f"BBVP-{ngay_ma}-{violation['id']:04d}"
    )
    # =====================================================
    # ĐỊNH DẠNG TIỀN
    # =====================================================
    tien_phat_hien_thi = dinh_dang_vnd(
        violation["so_tien_phat"]
    )
    # =====================================================
    # BỎ MARKER TỰ ĐỘNG KHI HIỂN THỊ BIÊN BẢN
    # =====================================================
    ghi_chu = violation["ghi_chu"] or ""
    marker = "[TỰ ĐỘNG TỪ KIỂM TRA BẢO HỘ]"
    if ghi_chu.startswith(marker):
        ghi_chu = ghi_chu[len(marker):].strip()
    return render_template(
        "bien_ban_vi_pham.html",
        violation=violation,
        so_bien_ban=so_bien_ban,
        ngay_hien_thi=dinh_dang_ngay(
            violation["ngay_vi_pham"]
        ),
        tien_phat_hien_thi=tien_phat_hien_thi,
        ghi_chu_hien_thi=ghi_chu
    )