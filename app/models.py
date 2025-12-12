from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db, login_manager

# ==========================
# 🎯 Vai trò hệ thống
# ==========================
class Role:
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    CHOICES = [ADMIN, TEACHER, STUDENT]


# ==========================
# 👤 Bảng người dùng
# ==========================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default=Role.STUDENT, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==========================
# 🎓 Bảng sinh viên
# ==========================
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # MSSV
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="student", uselist=False)
    enrollments = db.relationship("Enrollment", backref="student", cascade="all, delete-orphan")


# ==========================
# 📘 Bảng môn học
# ==========================
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship("Enrollment", backref="course", cascade="all, delete-orphan")
    exams = db.relationship("Exam", backref="course", cascade="all, delete-orphan")
    schedules = db.relationship("Schedule", backref="course", cascade="all, delete-orphan")


# ==========================
# 🧾 Bảng ghi danh / điểm
# ==========================
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    semester = db.Column(db.String(10), nullable=True)
    grade = db.Column(db.Float, nullable=True)  # 0-10 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", "semester", name="uq_enroll_sem"),
    )


# ==========================
# 🧮 Chuyển đổi điểm & tính GPA
# ==========================
def grade_to_letter_and_gpa(grade_10: float):
    if grade_10 is None:
        return None, None
    g = float(grade_10)
    if g >= 8.5: return "A", 4.0
    if g >= 7.0: return "B", 3.0
    if g >= 5.5: return "C", 2.0
    if g >= 4.0: return "D", 1.0
    return "F", 0.0


def compute_student_gpa(student_id: int):
    enrolls = Enrollment.query.filter_by(student_id=student_id).all()
    total_points, total_credits = 0.0, 0
    for e in enrolls:
        if e.grade is None or e.course is None:
            continue
        _, gp = grade_to_letter_and_gpa(e.grade)
        total_points += gp * e.course.credits
        total_credits += e.course.credits
    gpa = round(total_points / total_credits, 2) if total_credits else 0.0
    return gpa, total_credits


# ==========================
# 🗓️ Bảng lịch thi
# ==========================
class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    date = db.Column(db.Date)
    room = db.Column(db.String(50))
    note = db.Column(db.String(255))


# ==========================
# ⏰ Bảng thời khóa biểu
# ==========================
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    weekday = db.Column(db.String(20))  # Ví dụ: "Thứ Hai", "Thứ Ba"
    time = db.Column(db.String(50))     # Ví dụ: "07:30 - 09:30"
    room = db.Column(db.String(50))
