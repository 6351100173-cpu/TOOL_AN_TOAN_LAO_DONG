from flask import Flask, render_template
from cong_nhan import cong_nhan_bp
import sqlite3
import os


app = Flask(__name__)


# =========================================================
# ĐĂNG KÝ MODULE CÔNG NHÂN
# =========================================================

app.register_blueprint(cong_nhan_bp)


# =========================================================
# DATABASE
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "atld.db")


def get_dashboard_stats():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tổng số công nhân
    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
    """)
    tong_cong_nhan = cursor.fetchone()[0]

    # Số công nhân đang làm việc
    cursor.execute("""
        SELECT COUNT(*)
        FROM cong_nhan
        WHERE trang_thai = 'Đang làm việc'
    """)
    dang_lam_viec = cursor.fetchone()[0]

    conn.close()

    return {
        "tong_cong_nhan": tong_cong_nhan,
        "dang_lam_viec": dang_lam_viec,

        # Tạm thời chưa có module Bảo hộ, Vi phạm, Nguy cơ
        "da_kiem_tra": 0,
        "vi_pham": 0,
        "nguy_co_cao": 0
    }


# =========================================================
# TRANG CHỦ
# =========================================================

@app.route("/")
def home():

    stats = get_dashboard_stats()

    return render_template(
        "index.html",
        stats=stats
    )


# =========================================================
# CHẠY FLASK
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=False,
        use_reloader=False
    )

