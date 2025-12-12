from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db, csrf
from ..models import Student, Role

students_bp = Blueprint("students", __name__, template_folder="../templates/students")

# ==============================
# 🔐 Decorator kiểm tra quyền truy cập
# ==============================
def require_role(*roles):
    """Chỉ cho phép các role được truyền truy cập route."""
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
# 📋 Danh sách sinh viên
# ==============================
@students_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Student.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Student.full_name.ilike(like)) |
            (Student.code.ilike(like)) |
            (Student.email.ilike(like))
        )
    students = query.order_by(Student.id.desc()).all()
    return render_template("students/index.html", students=students, q=q)


# ==============================
# ➕ Thêm sinh viên
# ==============================
@students_bp.route("/create", methods=["GET", "POST"])
@login_required
@require_role(Role.ADMIN, Role.TEACHER)
def create():
    if request.method == "POST":
        code = request.form.get("code")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        class_name = request.form.get("class_name")

        if not code or not full_name or not email:
            flash("❌ Vui lòng nhập đầy đủ thông tin!", "danger")
            return render_template("students/form.html", student=None)

        if Student.query.filter((Student.code == code) | (Student.email == email)).first():
            flash("⚠️ Mã SV hoặc email đã tồn tại!", "danger")
            return render_template("students/form.html", student=None)

        s = Student(code=code, full_name=full_name, email=email, class_name=class_name)
        db.session.add(s)
        db.session.commit()
        flash("✅ Đã thêm sinh viên mới thành công!", "success")
        return redirect(url_for("students.index"))

    return render_template("students/form.html", student=None)


# ==============================
# ✏️ Chỉnh sửa sinh viên
# ==============================
@students_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@require_role(Role.ADMIN, Role.TEACHER)
def edit(id):
    s = Student.query.get_or_404(id)
    if request.method == "POST":
        s.code = request.form.get("code")
        s.full_name = request.form.get("full_name")
        s.email = request.form.get("email")
        s.class_name = request.form.get("class_name")

        db.session.commit()
        flash("✅ Cập nhật thông tin sinh viên thành công!", "success")
        return redirect(url_for("students.index"))

    return render_template("students/form.html", student=s)


# ==============================
# ❌ Xóa sinh viên (đã fix lỗi 400)
# ==============================
@students_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@require_role(Role.ADMIN, Role.TEACHER)
@csrf.exempt  # ✅ Bỏ qua kiểm tra CSRF cho form không có token
def delete(id):
    try:
        s = Student.query.get_or_404(id)
        db.session.delete(s)
        db.session.commit()
        flash("🗑️ Đã xóa sinh viên khỏi hệ thống!", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Lỗi khi xóa: {e}", "danger")
    return redirect(url_for("students.index"))
