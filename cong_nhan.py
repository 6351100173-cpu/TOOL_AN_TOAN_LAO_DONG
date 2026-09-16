from flask import Blueprint, render_template, request, redirect
import sqlite3
import os


# =========================================================
# CẤU HÌNH
# =========================================================

cong_nhan_bp = Blueprint("cong_nhan", __name__)


# Database nằm cùng thư mục với ATLD.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "atld.db")


# =========================================================
# KẾT NỐI DATABASE
# =========================================================

def get_db():

    conn = sqlite3.connect(DB_PATH)

    return conn


# =========================================================
# TẠO BẢNG CÔNG NHÂN
# =========================================================

def init_cong_nhan_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cong_nhan (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ma_cn TEXT NOT NULL,

            ho_ten TEXT NOT NULL,

            bo_phan TEXT,

            cong_viec TEXT,

            so_dien_thoai TEXT,

            trang_thai TEXT

        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# TẠO 200 CÔNG NHÂN MẪU
# =========================================================

def tao_cong_nhan_mau():

    conn = get_db()
    cursor = conn.cursor()

    # Kiểm tra database đã có công nhân chưa
    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
    """)

    so_luong = cursor.fetchone()[0]

    # Nếu đã có dữ liệu thì KHÔNG tạo lại
    if so_luong > 0:

        conn.close()

        print(
            f"Database hiện có {so_luong} công nhân."
        )

        return


    # =====================================================
    # DANH SÁCH HỌ
    # =====================================================

    ho = [
        "Nguyễn",
        "Trần",
        "Lê",
        "Phạm",
        "Hoàng",
        "Huỳnh",
        "Phan",
        "Vũ",
        "Võ",
        "Đặng",
        "Bùi",
        "Đỗ",
        "Hồ",
        "Ngô",
        "Dương",
        "Lý",
        "Mai",
        "Đinh",
        "Trương",
        "Đoàn"
    ]


    # =====================================================
    # TÊN ĐỆM
    # =====================================================

    ten_dem = [
        "Văn",
        "Minh",
        "Quốc",
        "Hữu",
        "Đức",
        "Thanh",
        "Công",
        "Anh",
        "Ngọc",
        "Hoàng"
    ]


    # =====================================================
    # TÊN
    # =====================================================

    ten = [
        "An",
        "Anh",
        "Bình",
        "Cường",
        "Dũng",
        "Đạt",
        "Đức",
        "Giang",
        "Hải",
        "Hào",
        "Hiếu",
        "Hùng",
        "Khải",
        "Khang",
        "Kiên",
        "Lâm",
        "Long",
        "Minh",
        "Nam",
        "Nghĩa",
        "Phong",
        "Phúc",
        "Quân",
        "Sơn",
        "Tài",
        "Tâm",
        "Thành",
        "Thắng",
        "Thiện",
        "Tiến",
        "Toàn",
        "Trí",
        "Trung",
        "Tuấn",
        "Tùng",
        "Vinh",
        "Việt",
        "Khoa",
        "Khôi",
        "Lộc"
    ]


    # =====================================================
    # BỘ PHẬN
    # =====================================================

    bo_phan_list = [
        "Kết cấu",
        "Xây dựng",
        "Cơ điện",
        "Hoàn thiện",
        "An toàn lao động",
        "Vận hành máy",
        "Kho vật tư",
        "Giám sát"
    ]


    # =====================================================
    # CÔNG VIỆC
    # =====================================================

    cong_viec_list = [
        "Thợ xây",
        "Thợ sắt",
        "Thợ cốp pha",
        "Thợ điện",
        "Thợ nước",
        "Thợ hàn",
        "Thợ hoàn thiện",
        "Vận hành máy",
        "Phụ xây",
        "Kỹ thuật viên"
    ]


    # =====================================================
    # TẠO 200 NGƯỜI
    # =====================================================

    dem = 1

    for h in ho:

        for td in ten_dem:

            for t in ten:

                if dem > 200:
                    break

                ho_ten = f"{h} {td} {t}"

                ma_cn = f"CN{dem:03d}"

                bo_phan = bo_phan_list[
                    (dem - 1) % len(bo_phan_list)
                ]

                cong_viec = cong_viec_list[
                    (dem - 1) % len(cong_viec_list)
                ]

                so_dien_thoai = f"09{dem:08d}"

                trang_thai = "Đang làm việc"


                cursor.execute("""
                    INSERT INTO cong_nhan (

                        ma_cn,
                        ho_ten,
                        bo_phan,
                        cong_viec,
                        so_dien_thoai,
                        trang_thai

                    )

                    VALUES (?, ?, ?, ?, ?, ?)

                """, (

                    ma_cn,
                    ho_ten,
                    bo_phan,
                    cong_viec,
                    so_dien_thoai,
                    trang_thai

                ))

                dem += 1


    conn.commit()


    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
    """)

    so_luong = cursor.fetchone()[0]

    conn.close()


    print(
        f"Đã tạo {so_luong} công nhân mẫu."
    )


# =========================================================
# TRANG CÔNG NHÂN
# =========================================================

@cong_nhan_bp.route("/cong-nhan")
def cong_nhan():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM cong_nhan
        ORDER BY id
    """)

    workers = cursor.fetchall()

    conn.close()

    return render_template(
        "cong_nhan.html",
        workers=workers
    )


# =========================================================
# THÊM CÔNG NHÂN
# =========================================================

@cong_nhan_bp.route(
    "/them-cong-nhan",
    methods=["POST"]
)
def them_cong_nhan():

    ma_cn = request.form.get("ma_cn")
    ho_ten = request.form.get("ho_ten")
    bo_phan = request.form.get("bo_phan")
    cong_viec = request.form.get("cong_viec")
    so_dien_thoai = request.form.get("so_dien_thoai")
    trang_thai = request.form.get("trang_thai")


    conn = get_db()
    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO cong_nhan (

            ma_cn,
            ho_ten,
            bo_phan,
            cong_viec,
            so_dien_thoai,
            trang_thai

        )

        VALUES (?, ?, ?, ?, ?, ?)

    """, (

        ma_cn,
        ho_ten,
        bo_phan,
        cong_viec,
        so_dien_thoai,
        trang_thai

    ))


    conn.commit()
    conn.close()


    return redirect("/cong-nhan")


# =========================================================
# XÓA CÔNG NHÂN
# =========================================================

@cong_nhan_bp.route(
    "/xoa-cong-nhan/<int:id>",
    methods=["POST"]
)
def xoa_cong_nhan(id):

    conn = get_db()
    cursor = conn.cursor()


    cursor.execute("""
        DELETE FROM cong_nhan
        WHERE id = ?
    """, (id,))


    conn.commit()
    conn.close()


    return redirect("/cong-nhan")


# =========================================================
# KHỞI TẠO
# =========================================================

init_cong_nhan_db()

tao_cong_nhan_mau()