from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Schedule, Course
from app.extensions import db, csrf

schedule_bp = Blueprint("schedules", __name__, template_folder="../templates")

# === Trang danh sách thời khóa biểu ===
@schedule_bp.route("/")
def index():
    schedules = Schedule.query.all()
    return render_template("schedules/index.html", schedules=schedules)

# === Thêm mới TKB ===
@schedule_bp.route("/create", methods=["GET", "POST"])
def create():
    courses = Course.query.all()
    if request.method == "POST":
        s = Schedule(
            course_id=request.form["course_id"],
            weekday=request.form["weekday"],
            time=request.form["time"],
            room=request.form["room"]
        )
        db.session.add(s)
        db.session.commit()
        flash("✅ Đã thêm thời khóa biểu!", "success")
        return redirect(url_for("schedules.index"))
    return render_template("schedules/form.html", courses=courses)


# === Sửa TKB ===
@schedule_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    schedule = Schedule.query.get_or_404(id)
    courses = Course.query.all()

    if request.method == "POST":
        schedule.course_id = request.form["course_id"]
        schedule.weekday = request.form["weekday"]
        schedule.time = request.form["time"]
        schedule.room = request.form["room"]

        db.session.commit()
        flash("✏️ Đã cập nhật thời khóa biểu!", "info")
        return redirect(url_for("schedules.index"))

    return render_template("schedules/form.html", schedule=schedule, courses=courses)


# === Xóa TKB ===
@schedule_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    schedule = Schedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash("🗑️ Đã xóa thời khóa biểu!", "danger")
    return redirect(url_for("schedules.index"))
