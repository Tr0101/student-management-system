from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Student, Course, Enrollment, Exam, Schedule, compute_student_gpa
from ..extensions import db

# ==============================
# 📊 Khởi tạo Blueprint chính
# ==============================
main_bp = Blueprint("main", __name__, template_folder="../templates/main")


# ==============================
# 📈 Trang Dashboard chính
# ==============================
@main_bp.route("/")
@login_required
def index():
    """Trang bảng điều khiển tổng quan"""

    # --- Thống kê tổng quan ---
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_enrolls = Enrollment.query.count()

    # --- Phân bố điểm trung bình ---
    grade_rows = db.session.execute(db.text("""
        SELECT ROUND(grade,0) as g, COUNT(*) as c 
        FROM enrollment 
        WHERE grade IS NOT NULL 
        GROUP BY ROUND(grade,0) 
        ORDER BY g
    """)).all()

    labels = [str(int(r.g)) for r in grade_rows]
    values = [int(r.c) for r in grade_rows]

    # --- Top 5 học phần được đăng ký nhiều nhất ---
    top_courses = db.session.execute(db.text("""
        SELECT course.name, COUNT(enrollment.id) as cnt
        FROM course 
        LEFT JOIN enrollment ON course.id = enrollment.course_id
        GROUP BY course.id
        ORDER BY cnt DESC
        LIMIT 5
    """)).all()

    # --- GPA cá nhân (nếu là sinh viên) ---
    gpa_info = None
    if current_user.is_authenticated and current_user.student_id:
        gpa, credits = compute_student_gpa(current_user.student_id)
        gpa_info = {"gpa": gpa, "credits": credits}

    # --- Lịch thi gần nhất ---
    exams = Exam.query.order_by(Exam.date.asc()).limit(5).all()

    # --- Thời khóa biểu ---
    schedules = Schedule.query.order_by(Schedule.weekday).limit(5).all()

    return render_template(
        "main/dashboard.html",
        total_students=total_students,
        total_courses=total_courses,
        total_enrolls=total_enrolls,
        labels=labels,
        values=values,
        top_courses=top_courses,
        gpa_info=gpa_info,
        exams=exams,
        schedules=schedules,
    )


# ==============================
# 📅 Trang xem Thời khóa biểu
# ==============================
@main_bp.route("/schedule")
@login_required
def schedule():
    """Hiển thị thời khóa biểu"""
    schedules = Schedule.query.order_by(Schedule.weekday).all()
    return render_template("main/schedule.html", schedules=schedules)


# ==============================
# 🕒 Trang xem Lịch thi
# ==============================
@main_bp.route("/exams")
@login_required
def exams():
    """Hiển thị lịch thi"""
    exams = Exam.query.order_by(Exam.date.asc()).all()
    return render_template("main/exams.html", exams=exams)


# ==============================
# ✉️ Gửi email thủ công (Admin / Teacher)
# ==============================
from ..utils.email_utils import send_grade_notification
from flask_mail import Message
from ..extensions import mail

@main_bp.route("/send-email", methods=["GET", "POST"])
@login_required
def send_email_manual():
    """Trang gửi email thủ công"""
    if current_user.role not in ("admin", "teacher"):
        flash("⚠️ Bạn không có quyền gửi email.", "warning")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email")
        subject = request.form.get("subject") or "Thông báo từ hệ thống QLSV"
        grade = request.form.get("grade")
        course = request.form.get("course") or "Không xác định"

        try:
            if grade:
                # Gửi theo kết quả học tập
                send_grade_notification(email, course, float(grade))
            else:
                # Gửi email thường
                msg = Message(subject=subject, recipients=[email],
                              body="Tin nhắn từ hệ thống Quản lý Sinh viên.")
                mail.send(msg)

            flash("✅ Email đã được gửi thành công!", "success")
        except Exception as e:
            flash(f"❌ Lỗi khi gửi email: {e}", "danger")

        return redirect(url_for("main.send_email_manual"))

    return render_template("main/send_email.html")
