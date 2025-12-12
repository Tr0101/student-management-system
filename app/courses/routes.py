from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db, csrf
from ..models import Course, Role

courses_bp = Blueprint("courses", __name__, template_folder="../templates/courses")

# ==============================
# 🔐 Decorator kiểm tra quyền
# ==============================
def require_role(*roles):
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_user.is_anonymous or current_user.role not in roles:
                flash("⚠️ Bạn không có quyền truy cập trang này!", "warning")
                return redirect(url_for("main.index"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ==============================
# 📚 Danh sách học phần
# ==============================
@courses_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Course.query
    if q:
        like = f"%{q}%"
        query = query.filter((Course.name.ilike(like)) | (Course.code.ilike(like)))
    courses = query.order_by(Course.id.desc()).all()
    return render_template("courses/index.html", courses=courses, q=q)


# ==============================
# ➕ Thêm học phần
# ==============================
@courses_bp.route("/create", methods=["GET", "POST"])
@login_required
@require_role(Role.ADMIN, Role.TEACHER)
def create():
    if request.method == "POST":
        code = request.form.get("code")
        name = request.form.get("name")
        credits = int(request.form.get("credits", 3))

        if not code or not name:
            flash("❌ Thiếu dữ liệu!", "danger")
            return render_template("courses/form.html", course=None)

        if Course.query.filter_by(code=code).first():
            flash("⚠️ Mã học phần đã tồn tại!", "danger")
            return render_template("courses/form.html", course=None)

        c = Course(code=code, name=name, credits=credits)
        db.session.add(c)
        db.session.commit()
        flash("✅ Đã tạo học phần mới thành công!", "success")
        return redirect(url_for("courses.index"))
    return render_template("courses/form.html", course=None)


# ==============================
# ✏️ Chỉnh sửa học phần
# ==============================
@courses_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@require_role(Role.ADMIN, Role.TEACHER)
def edit(id):
    c = Course.query.get_or_404(id)
    if request.method == "POST":
        c.code = request.form.get("code")
        c.name = request.form.get("name")
        c.credits = int(request.form.get("credits", c.credits))
        db.session.commit()
        flash("✅ Cập nhật học phần thành công!", "success")
        return redirect(url_for("courses.index"))
    return render_template("courses/form.html", course=c)


# ==============================
# ❌ Xóa học phần (đã fix lỗi 400)
# ==============================
@courses_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@require_role(Role.ADMIN, Role.TEACHER)
@csrf.exempt  # ✅ Bỏ kiểm tra CSRF cho form delete
def delete(id):
    try:
        c = Course.query.get_or_404(id)
        db.session.delete(c)
        db.session.commit()
        flash("🗑️ Đã xóa học phần!", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Lỗi khi xóa: {e}", "danger")
    return redirect(url_for("courses.index"))
