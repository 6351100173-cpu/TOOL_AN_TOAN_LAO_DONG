# ============================================================
# cong_nhan.py
# MODULE QUẢN LÝ CÔNG NHÂN
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import os


# ============================================================
# 1. KHỞI TẠO BLUEPRINT
# ============================================================

cong_nhan_bp = Blueprint(
    "cong_nhan",
    __name__
)


# ============================================================
# 2. CẤU HÌNH DATABASE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "atld.db")


def get_db():
    """
    Tạo kết nối đến database chung của hệ thống.
    """

    conn = sqlite3.connect(DB_PATH)

    # Cho phép lấy dữ liệu theo tên cột.
    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# 3. TẠO BẢNG CÔNG NHÂN
# ============================================================

def init_cong_nhan_db():
    """
    Tạo bảng cong_nhan nếu bảng chưa tồn tại.
    """

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
            trang_thai TEXT DEFAULT 'Đang làm việc'
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# 4. TẠO 200 CÔNG NHÂN MẪU
# ============================================================

def tao_cong_nhan_mau():
    """
    Chỉ tạo 200 công nhân mẫu khi bảng công nhân chưa có dữ liệu.

    Nếu database đã có công nhân thì không tạo lại,
    tránh bị trùng dữ liệu mỗi lần chạy Flask.
    """

    conn = get_db()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # Kiểm tra dữ liệu hiện tại
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
    """)

    so_luong = cursor.fetchone()[0]

    if so_luong > 0:
        conn.close()

        print(
            f"Database hiện có {so_luong} công nhân."
        )

        return

    # --------------------------------------------------------
    # Danh sách dùng để tạo dữ liệu mẫu
    # --------------------------------------------------------

    danh_sach_ho = [
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

    danh_sach_ten_dem = [
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

    danh_sach_ten = [
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

    danh_sach_bo_phan = [
        "Kết cấu",
        "Xây dựng",
        "Cơ điện",
        "Hoàn thiện",
        "An toàn lao động",
        "Vận hành máy",
        "Kho vật tư",
        "Giám sát"
    ]

    danh_sach_cong_viec = [
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

    # --------------------------------------------------------
    # Tạo công nhân
    # --------------------------------------------------------

    dem = 1

    for ho in danh_sach_ho:

        for ten_dem in danh_sach_ten_dem:

            for ten in danh_sach_ten:

                if dem > 200:
                    break

                ma_cn = f"CN{dem:03d}"

                ho_ten = (
                    f"{ho} {ten_dem} {ten}"
                )

                bo_phan = danh_sach_bo_phan[
                    (dem - 1) % len(danh_sach_bo_phan)
                ]

                cong_viec = danh_sach_cong_viec[
                    (dem - 1) % len(danh_sach_cong_viec)
                ]

                so_dien_thoai = (
                    f"09{dem:08d}"
                )

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

            # Đủ 200 người thì dừng
            if dem > 200:
                break

        # Đủ 200 người thì dừng
        if dem > 200:
            break

    conn.commit()

    # --------------------------------------------------------
    # Kiểm tra số lượng sau khi tạo
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
    """)

    so_luong = cursor.fetchone()[0]

    conn.close()

    print(
        f"Đã tạo {so_luong} công nhân mẫu."
    )


# ============================================================
# 5. TRANG DANH SÁCH CÔNG NHÂN
# ============================================================

@cong_nhan_bp.route("/cong-nhan")
def cong_nhan():
    """
    Hiển thị toàn bộ danh sách công nhân.
    """

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM cong_nhan
        ORDER BY id ASC
    """)

    workers = cursor.fetchall()

    conn.close()

    return render_template(
        "cong_nhan.html",
        workers=workers
    )


# ============================================================
# 6. THÊM CÔNG NHÂN
# ============================================================

@cong_nhan_bp.route(
    "/them-cong-nhan",
    methods=["POST"]
)
def them_cong_nhan():
    """
    Thêm một công nhân mới vào hệ thống.
    """

    ma_cn = request.form.get(
        "ma_cn",
        ""
    ).strip()

    ho_ten = request.form.get(
        "ho_ten",
        ""
    ).strip()

    bo_phan = request.form.get(
        "bo_phan",
        ""
    ).strip()

    cong_viec = request.form.get(
        "cong_viec",
        ""
    ).strip()

    so_dien_thoai = request.form.get(
        "so_dien_thoai",
        ""
    ).strip()

    trang_thai = request.form.get(
        "trang_thai",
        "Đang làm việc"
    ).strip()

    # Không cho thêm nếu thiếu mã hoặc họ tên
    if not ma_cn or not ho_ten:
        return redirect(
            url_for("cong_nhan.cong_nhan")
        )

    conn = get_db()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # Kiểm tra mã công nhân đã tồn tại chưa
    # --------------------------------------------------------

    cursor.execute("""
        SELECT id
        FROM cong_nhan
        WHERE ma_cn = ?
    """, (ma_cn,))

    cong_nhan_da_co = cursor.fetchone()

    if cong_nhan_da_co:
        conn.close()

        return redirect(
            url_for("cong_nhan.cong_nhan")
        )

    # --------------------------------------------------------
    # Thêm công nhân
    # --------------------------------------------------------

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

    return redirect(
        url_for("cong_nhan.cong_nhan")
    )


# ============================================================
# 7. XÓA CÔNG NHÂN
# ============================================================

@cong_nhan_bp.route(
    "/xoa-cong-nhan/<int:id>",
    methods=["POST"]
)
def xoa_cong_nhan(id):
    """
    Xóa một công nhân khỏi danh sách.
    """

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM cong_nhan
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect(
        url_for("cong_nhan.cong_nhan")
    )


# ============================================================
# 8. KHỞI TẠO DATABASE
# ============================================================

init_cong_nhan_db()

tao_cong_nhan_mau()
