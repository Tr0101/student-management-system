from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Exam, Course
from app.extensions import db, csrf

exam_bp = Blueprint("exams", __name__, template_folder="../templates")

@exam_bp.route("/")
def index():
    exams = Exam.query.all()
    return render_template("exams/index.html", exams=exams)

@exam_bp.route("/create", methods=["GET", "POST"])
def create():
    courses = Course.query.all()
    if request.method == "POST":
        date = request.form["date"]
        room = request.form["room"]
        course_id = request.form["course_id"]
        exam = Exam(course_id=course_id, date=date, room=room)
        db.session.add(exam)
        db.session.commit()
        flash("Đã tạo lịch thi!", "success")
        return redirect(url_for("exams.index"))
    return render_template("exams/form.html", courses=courses)
