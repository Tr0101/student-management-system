from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from io import BytesIO
import pandas as pd
from functools import wraps
from ..extensions import db
from ..models import Enrollment, Student, Course, Role
from ..utils.pdf import build_transcript_pdf
from ..utils.email_utils import send_grade_notification  # ✅ Gửi email tự động

enroll_bp = Blueprint("enrollments", __name__, template_folder="../templates/enrollments")


# ==============================
# 🔐 Decorator kiểm tra quyền
# ==============================
def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_user.is_anonymous or current_user.role not in roles:
                flash("⚠️ Bạn không có quyền truy cập trang này!", "warning")
                return redirect(url_for("main.index"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ==============================
# 📄 Danh sách ghi danh / điểm
# ==============================
@enroll_bp.route("/")
@login_required
def index():
    enrolls = Enrollment.query.order_by(Enrollment.id.desc()).limit(200).all()
    return render_template("enrollments/index.html", enrolls=enrolls)


# ==============================
# 🧾 Ghi danh hoặc nhập điểm
# ==============================
@enroll_bp.route("/assign", methods=["GET", "POST"])
@login_required
@require_role(Role.ADMIN, Role.TEACHER)
def assign():
    students = Student.query.order_by(Student.full_name).all()
    courses = Course.query.order_by(Course.name).all()

    if request.method == "POST":
        student_id = int(request.form.get("student_id"))
        course_id = int(request.form.get("course_id"))
        semester = request.form.get("semester") or None
        grade = request.form.get("grade")
        grade = float(grade) if grade not in (None, "",) else None

        e = Enrollment(student_id=student_id, course_id=course_id, semester=semester, grade=grade)
        db.session.add(e)
        try:
            db.session.commit()
            flash("✅ Đã ghi danh/nhập điểm thành công.", "success")

            # 📨 Gửi email tự động nếu có điểm
            if grade is not None:
                student = Student.query.get(student_id)
                course = Course.query.get(course_id)
                if student and student.email:
                    send_grade_notification(student.email, course.name, grade)

        except Exception as ex:
            db.session.rollback()
            flash(f"❌ Lỗi khi lưu dữ liệu: {ex}", "danger")

        return redirect(url_for("enrollments.index"))

    return render_template("enrollments/assign.html", students=students, courses=courses)


# ==============================
# ⬆️ Import điểm từ file Excel
# ==============================
@enroll_bp.route("/upload", methods=["GET", "POST"])
@login_required
@require_role(Role.ADMIN, Role.TEACHER)
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("⚠️ Chưa chọn file!", "danger")
            return render_template("enrollments/upload.html")
        try:
            df = pd.read_excel(file)
            required = {"student_code", "course_code", "semester", "grade"}
            colmap = {c: c.lower() for c in df.columns if str(c).lower() in required}
            df = df.rename(columns=colmap)
            missing = required - set(df.columns)
            if missing:
                flash("Thiếu cột: " + ", ".join(sorted(missing)), "danger")
                return render_template("enrollments/upload.html")

            inserts = 0
            for _, row in df.iterrows():
                s = Student.query.filter_by(code=str(row['student_code']).strip()).first()
                c = Course.query.filter_by(code=str(row['course_code']).strip()).first()
                if not s or not c:
                    continue
                try:
                    grade = float(row['grade']) if pd.notna(row['grade']) else None
                except:
                    grade = None
                e = Enrollment(student_id=s.id, course_id=c.id, semester=str(row['semester']).strip(), grade=grade)
                db.session.add(e)
                try:
                    db.session.commit()
                    inserts += 1
                    if grade is not None and s.email:
                        send_grade_notification(s.email, c.name, grade)
                except:
                    db.session.rollback()

            flash(f"✅ Đã xử lý xong file. {inserts} bản ghi được thêm!", "success")
            return redirect(url_for("enrollments.index"))
        except Exception as ex:
            flash(f"❌ Lỗi đọc file: {ex}", "danger")
            return render_template("enrollments/upload.html")

    return render_template("enrollments/upload.html")


# ==============================
# ⬇️ Xuất Excel danh sách điểm (✅ sinh viên cũng có quyền)
# ==============================
@enroll_bp.route("/export")
@login_required
def export_excel():
    # ✅ Cho phép tất cả role, nhưng nếu là sinh viên thì chỉ export điểm của họ
    data = []
    if current_user.role == Role.STUDENT:
        enrolls = Enrollment.query.filter_by(student_id=current_user.student_id).all()
    else:
        enrolls = Enrollment.query.all()

    for e in enrolls:
        data.append({
            "student_code": e.student.code,
            "student_name": e.student.full_name,
            "course_code": e.course.code,
            "course_name": e.course.name,
            "credits": e.course.credits,
            "semester": e.semester,
            "grade": e.grade,
        })
    df = pd.DataFrame(data)
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="grades")
    bio.seek(0)
    return send_file(
        bio,
        as_attachment=True,
        download_name="grades_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ==============================
# 📄 Xuất bảng điểm PDF
# ==============================
@enroll_bp.route("/transcript/<int:student_id>.pdf")
@login_required
def transcript_pdf(student_id):
    if current_user.role not in (Role.ADMIN, Role.TEACHER) and current_user.student_id != student_id:
        abort(403)
    pdf_bytes, filename = build_transcript_pdf(student_id)
    return send_file(
        BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
