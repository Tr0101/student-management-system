from app import create_app, db
from app.models import Exam, Schedule, Course
from datetime import date

app = create_app()
with app.app_context():
    c = Course.query.first()
    if not c:
        print("⚠️ Không tìm thấy môn học nào trong database. Hãy tạo ít nhất 1 Course trước.")
    else:
        e = Exam(course_id=c.id, date=date(2025, 12, 20), room="A101", note="Giữa kỳ")
        s = Schedule(course_id=c.id, weekday="Thứ Hai", time="07:30 - 09:30", room="A204")

        db.session.add_all([e, s])
        db.session.commit()
        print("✅ Đã thêm dữ liệu mẫu lịch thi và thời khóa biểu thành công!")
