from flask import Flask, render_template
from cong_nhan import cong_nhan_bp

app = Flask(__name__)

# Đăng ký chức năng Công nhân
app.register_blueprint(cong_nhan_bp)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
