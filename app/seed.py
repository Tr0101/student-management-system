from .extensions import db
from .models import User, Student, Course, Enrollment, Role

def register_seed_command(app):
    @app.cli.command("seed")
    def seed():
        with app.app_context():
            if not User.query.filter_by(email="admin@demo.com").first():
                admin = User(email="admin@demo.com", role=Role.ADMIN)
                admin.set_password("123456")
                db.session.add(admin)

            if not User.query.filter_by(email="teacher@demo.com").first():
                teacher = User(email="teacher@demo.com", role=Role.TEACHER)
                teacher.set_password("123456")
                db.session.add(teacher)

            stu = Student.query.filter_by(code="SV001").first()
            if not stu:
                stu = Student(code="SV001", full_name="Nguyen Van A", email="student@demo.com", class_name="DTS1")
                db.session.add(stu)
                db.session.flush()
                user_stu = User(email="student@demo.com", role=Role.STUDENT, student_id=stu.id)
                user_stu.set_password("123456")
                db.session.add(user_stu)

            c1 = Course.query.filter_by(code="MATH101").first()
            if not c1:
                c1 = Course(code="MATH101", name="Calculus I", credits=3)
                db.session.add(c1)
            c2 = Course.query.filter_by(code="CS102").first()
            if not c2:
                c2 = Course(code="CS102", name="Intro to CS", credits=4)
                db.session.add(c2)

            db.session.commit()

            if not Enrollment.query.first():
                db.session.add(Enrollment(student_id=stu.id, course_id=c1.id, semester="2025A", grade=8.0))
                db.session.add(Enrollment(student_id=stu.id, course_id=c2.id, semester="2025A", grade=7.2))
                db.session.commit()

            print("✅ Seeded demo data.")
