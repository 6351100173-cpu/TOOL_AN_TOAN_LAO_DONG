from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import date, datetime
# =========================================================
# BLUEPRINT
# =========================================================
bao_ho_bp = Blueprint("bao_ho", __name__)
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
# TẠO BẢNG KIỂM TRA BẢO HỘ
# =========================================================
def init_kiem_tra_bao_ho_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kiem_tra_bao_ho (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_cn TEXT NOT NULL,
            ngay_kiem_tra TEXT NOT NULL,
            mu_bao_ho TEXT,
            ao_phan_quang TEXT,
            giay_bao_ho TEXT,
            gang_tay TEXT,
            kinh_bao_ho TEXT,
            day_an_toan TEXT,
            ket_qua TEXT,
            nguoi_kiem_tra TEXT,
            ghi_chu TEXT
        )
    """)
    conn.commit()
    conn.close()
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
# KHỞI TẠO DATABASE
# =========================================================
init_kiem_tra_bao_ho_db()
init_vi_pham_db()
# =========================================================
# TẠO NỘI DUNG VI PHẠM TỪ KIỂM TRA BẢO HỘ
# =========================================================
def tao_noi_dung_vi_pham(
    mu_bao_ho,
    ao_phan_quang,
    giay_bao_ho,
    gang_tay,
    kinh_bao_ho,
    day_an_toan
):
    hang_muc_khong_dat = []
    if mu_bao_ho == "Không đạt":
        hang_muc_khong_dat.append("Mũ bảo hộ")
    if ao_phan_quang == "Không đạt":
        hang_muc_khong_dat.append("Áo phản quang")
    if giay_bao_ho == "Không đạt":
        hang_muc_khong_dat.append("Giày bảo hộ")
    if gang_tay == "Không đạt":
        hang_muc_khong_dat.append("Găng tay")
    if kinh_bao_ho == "Không đạt":
        hang_muc_khong_dat.append("Kính bảo hộ")
    if day_an_toan == "Không đạt":
        hang_muc_khong_dat.append("Dây an toàn")
    if not hang_muc_khong_dat:
        return ""
    return "Không đạt bảo hộ lao động: " + ", ".join(hang_muc_khong_dat)
# =========================================================
# ĐỒNG BỘ MỘT KẾT QUẢ KIỂM TRA SANG VI PHẠM
# =========================================================
def dong_bo_vi_pham_bao_ho(
    cursor,
    ma_cn,
    ngay_kiem_tra,
    ket_qua,
    mu_bao_ho,
    ao_phan_quang,
    giay_bao_ho,
    gang_tay,
    kinh_bao_ho,
    day_an_toan,
    nguoi_kiem_tra,
    ghi_chu
):
    cursor.execute("""
        SELECT id, trang_thai
        FROM vi_pham
        WHERE ma_cn = ?
        AND ngay_vi_pham = ?
        AND ghi_chu LIKE ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        ma_cn,
        ngay_kiem_tra,
        "[TỰ ĐỘNG TỪ KIỂM TRA BẢO HỘ]%"
    ))
    vi_pham_bao_ho = cursor.fetchone()
    if ket_qua == "Không đạt":
        noi_dung = tao_noi_dung_vi_pham(
            mu_bao_ho,
            ao_phan_quang,
            giay_bao_ho,
            gang_tay,
            kinh_bao_ho,
            day_an_toan
        )
        if not noi_dung:
            noi_dung = "Không đạt yêu cầu bảo hộ lao động"
        ghi_chu_dong_bo = "[TỰ ĐỘNG TỪ KIỂM TRA BẢO HỘ]"
        if ghi_chu:
            ghi_chu_dong_bo += " " + ghi_chu
        thoi_gian = datetime.now().strftime("%H:%M")
        if vi_pham_bao_ho:
            cursor.execute("""
                UPDATE vi_pham
                SET noi_dung = ?,
                    muc_do = ?,
                    nguoi_lap = ?,
                    ghi_chu = ?
                WHERE id = ?
            """, (
                noi_dung,
                "Trung bình",
                nguoi_kiem_tra or "Giám sát",
                ghi_chu_dong_bo,
                vi_pham_bao_ho["id"]
            ))
        else:
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
                ngay_kiem_tra,
                thoi_gian,
                noi_dung,
                "Trung bình",
                "Chưa xử lý",
                None,
                0,
                nguoi_kiem_tra or "Giám sát",
                ghi_chu_dong_bo
            ))
    else:
        if vi_pham_bao_ho:
            if vi_pham_bao_ho["trang_thai"] == "Chưa xử lý":
                cursor.execute("""
                    DELETE FROM vi_pham
                    WHERE id = ?
                """, (
                    vi_pham_bao_ho["id"],
                ))
# =========================================================
# ĐỒNG BỘ TOÀN BỘ DỮ LIỆU KIỂM TRA CŨ
# =========================================================
def dong_bo_du_lieu_cu():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            kt.ma_cn,
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
        FROM kiem_tra_bao_ho kt
        INNER JOIN (
            SELECT
                ma_cn,
                ngay_kiem_tra,
                MAX(id) AS max_id
            FROM kiem_tra_bao_ho
            GROUP BY ma_cn, ngay_kiem_tra
        ) moi_nhat
            ON kt.id = moi_nhat.max_id
        WHERE kt.ket_qua = 'Không đạt'
        ORDER BY kt.ngay_kiem_tra ASC, kt.ma_cn ASC
    """)
    du_lieu_cu = cursor.fetchall()
    for item in du_lieu_cu:
        dong_bo_vi_pham_bao_ho(
            cursor,
            item["ma_cn"],
            item["ngay_kiem_tra"],
            item["ket_qua"],
            item["mu_bao_ho"],
            item["ao_phan_quang"],
            item["giay_bao_ho"],
            item["gang_tay"],
            item["kinh_bao_ho"],
            item["day_an_toan"],
            item["nguoi_kiem_tra"] or "Giám sát",
            item["ghi_chu"] or ""
        )
    conn.commit()
    conn.close()
# =========================================================
# QUÉT DỮ LIỆU CŨ KHI KHỞI ĐỘNG
# =========================================================
dong_bo_du_lieu_cu()
# =========================================================
# TRANG KIỂM TRA BẢO HỘ
# =========================================================
@bao_ho_bp.route("/kiem-tra-bao-ho")
def kiem_tra_bao_ho():
    ngay_chon = request.args.get(
        "ngay",
        date.today().isoformat()
    )
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            cn.id,
            cn.ma_cn,
            cn.ho_ten,
            cn.bo_phan,
            cn.cong_viec,
            cn.so_dien_thoai,
            cn.trang_thai,
            kt.mu_bao_ho,
            kt.ao_phan_quang,
            kt.giay_bao_ho,
            kt.gang_tay,
            kt.kinh_bao_ho,
            kt.day_an_toan,
            kt.ket_qua,
            kt.nguoi_kiem_tra,
            kt.ghi_chu
        FROM cong_nhan cn
        LEFT JOIN kiem_tra_bao_ho kt
            ON cn.ma_cn = kt.ma_cn
            AND kt.ngay_kiem_tra = ?
            AND kt.id = (
                SELECT MAX(kt2.id)
                FROM kiem_tra_bao_ho kt2
                WHERE kt2.ma_cn = cn.ma_cn
                AND kt2.ngay_kiem_tra = ?
            )
        WHERE cn.trang_thai = 'Đang làm việc'
        ORDER BY cn.id ASC
    """, (
        ngay_chon,
        ngay_chon
    ))
    danh_sach_kiem_tra = cursor.fetchall()
    tong_cong_nhan = len(danh_sach_kiem_tra)
    da_kiem_tra = sum(
        1 for worker in danh_sach_kiem_tra
        if worker["ket_qua"]
    )
    so_dat = sum(
        1 for worker in danh_sach_kiem_tra
        if worker["ket_qua"] == "Đạt"
    )
    so_khong_dat = sum(
        1 for worker in danh_sach_kiem_tra
        if worker["ket_qua"] == "Không đạt"
    )
    chua_kiem_tra = tong_cong_nhan - da_kiem_tra
    if tong_cong_nhan > 0:
        ty_le_hoan_thanh = round(
            (da_kiem_tra / tong_cong_nhan) * 100
        )
    else:
        ty_le_hoan_thanh = 0
    stats = {
        "tong_cong_nhan": tong_cong_nhan,
        "da_kiem_tra": da_kiem_tra,
        "so_dat": so_dat,
        "so_khong_dat": so_khong_dat,
        "chua_kiem_tra": chua_kiem_tra,
        "ty_le_hoan_thanh": ty_le_hoan_thanh
    }
    conn.close()
    return render_template(
        "bao_ho.html",
        danh_sach_kiem_tra=danh_sach_kiem_tra,
        ngay_chon=ngay_chon,
        stats=stats
    )
# =========================================================
# ĐÁNH DẤU TẤT CẢ CÔNG NHÂN ĐẠT
# =========================================================
@bao_ho_bp.route("/danh-dau-tat-ca-dat", methods=["POST"])
def danh_dau_tat_ca_dat():
    ngay_kiem_tra = request.form.get(
        "ngay_kiem_tra",
        date.today().isoformat()
    )
    nguoi_kiem_tra = request.form.get(
        "nguoi_kiem_tra",
        "Giám sát"
    )
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ma_cn
        FROM cong_nhan
        WHERE trang_thai = 'Đang làm việc'
        ORDER BY id ASC
    """)
    workers = cursor.fetchall()
    for worker in workers:
        ma_cn = worker["ma_cn"]
        cursor.execute("""
            SELECT id
            FROM kiem_tra_bao_ho
            WHERE ma_cn = ?
            AND ngay_kiem_tra = ?
            ORDER BY id DESC
            LIMIT 1
        """, (
            ma_cn,
            ngay_kiem_tra
        ))
        da_co = cursor.fetchone()
        if da_co:
            cursor.execute("""
                UPDATE kiem_tra_bao_ho
                SET mu_bao_ho = ?,
                    ao_phan_quang = ?,
                    giay_bao_ho = ?,
                    gang_tay = ?,
                    kinh_bao_ho = ?,
                    day_an_toan = ?,
                    ket_qua = ?,
                    nguoi_kiem_tra = ?,
                    ghi_chu = ?
                WHERE id = ?
            """, (
                "Đạt",
                "Đạt",
                "Đạt",
                "Đạt",
                "Đạt",
                "Đạt",
                "Đạt",
                nguoi_kiem_tra,
                "",
                da_co["id"]
            ))
        else:
            cursor.execute("""
                INSERT INTO kiem_tra_bao_ho (
                    ma_cn,
                    ngay_kiem_tra,
                    mu_bao_ho,
                    ao_phan_quang,
                    giay_bao_ho,
                    gang_tay,
                    kinh_bao_ho,
                    day_an_toan,
                    ket_qua,
                    nguoi_kiem_tra,
                    ghi_chu
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ma_cn,
                ngay_kiem_tra,
                "Đạt",
                "Đạt",
                "Đạt",
                "Đạt",
                "Đạt",
                "Đạt",
                "Đạt",
                nguoi_kiem_tra,
                ""
            ))
        dong_bo_vi_pham_bao_ho(
            cursor,
            ma_cn,
            ngay_kiem_tra,
            "Đạt",
            "Đạt",
            "Đạt",
            "Đạt",
            "Đạt",
            "Đạt",
            "Đạt",
            nguoi_kiem_tra,
            ""
        )
    conn.commit()
    conn.close()
    return redirect(
        url_for(
            "bao_ho.kiem_tra_bao_ho",
            ngay=ngay_kiem_tra
        )
    )
# =========================================================
# CẬP NHẬT KIỂM TRA MỘT CÔNG NHÂN
# =========================================================
@bao_ho_bp.route("/cap-nhat-bao-ho", methods=["POST"])
def cap_nhat_bao_ho():
    ma_cn = request.form.get(
        "ma_cn",
        ""
    ).strip()
    ngay_kiem_tra = request.form.get(
        "ngay_kiem_tra",
        date.today().isoformat()
    ).strip()
    mu_bao_ho = request.form.get(
        "mu_bao_ho",
        "Đạt"
    ).strip()
    ao_phan_quang = request.form.get(
        "ao_phan_quang",
        "Đạt"
    ).strip()
    giay_bao_ho = request.form.get(
        "giay_bao_ho",
        "Đạt"
    ).strip()
    gang_tay = request.form.get(
        "gang_tay",
        "Đạt"
    ).strip()
    kinh_bao_ho = request.form.get(
        "kinh_bao_ho",
        "Đạt"
    ).strip()
    day_an_toan = request.form.get(
        "day_an_toan",
        "Đạt"
    ).strip()
    nguoi_kiem_tra = request.form.get(
        "nguoi_kiem_tra",
        "Giám sát"
    ).strip()
    ghi_chu = request.form.get(
        "ghi_chu",
        ""
    ).strip()
    cac_hang_muc = [
        mu_bao_ho,
        ao_phan_quang,
        giay_bao_ho,
        gang_tay,
        kinh_bao_ho,
        day_an_toan
    ]
    if all(
        item == "Đạt"
        for item in cac_hang_muc
    ):
        ket_qua = "Đạt"
    else:
        ket_qua = "Không đạt"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id
        FROM kiem_tra_bao_ho
        WHERE ma_cn = ?
        AND ngay_kiem_tra = ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        ma_cn,
        ngay_kiem_tra
    ))
    da_co = cursor.fetchone()
    if da_co:
        cursor.execute("""
            UPDATE kiem_tra_bao_ho
            SET mu_bao_ho = ?,
                ao_phan_quang = ?,
                giay_bao_ho = ?,
                gang_tay = ?,
                kinh_bao_ho = ?,
                day_an_toan = ?,
                ket_qua = ?,
                nguoi_kiem_tra = ?,
                ghi_chu = ?
            WHERE id = ?
        """, (
            mu_bao_ho,
            ao_phan_quang,
            giay_bao_ho,
            gang_tay,
            kinh_bao_ho,
            day_an_toan,
            ket_qua,
            nguoi_kiem_tra,
            ghi_chu,
            da_co["id"]
        ))
    else:
        cursor.execute("""
            INSERT INTO kiem_tra_bao_ho (
                ma_cn,
                ngay_kiem_tra,
                mu_bao_ho,
                ao_phan_quang,
                giay_bao_ho,
                gang_tay,
                kinh_bao_ho,
                day_an_toan,
                ket_qua,
                nguoi_kiem_tra,
                ghi_chu
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ma_cn,
            ngay_kiem_tra,
            mu_bao_ho,
            ao_phan_quang,
            giay_bao_ho,
            gang_tay,
            kinh_bao_ho,
            day_an_toan,
            ket_qua,
            nguoi_kiem_tra,
            ghi_chu
        ))
    # =====================================================
    # ĐỒNG BỘ NGAY SANG VI PHẠM
    # =====================================================
    dong_bo_vi_pham_bao_ho(
        cursor,
        ma_cn,
        ngay_kiem_tra,
        ket_qua,
        mu_bao_ho,
        ao_phan_quang,
        giay_bao_ho,
        gang_tay,
        kinh_bao_ho,
        day_an_toan,
        nguoi_kiem_tra,
        ghi_chu
    )
    conn.commit()
    conn.close()
    return redirect(
        url_for(
            "bao_ho.kiem_tra_bao_ho",
            ngay=ngay_kiem_tra
        )
    )