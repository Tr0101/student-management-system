# app/utils/email_utils.py
from flask_mail import Message
from app.extensions import mail

def send_grade_notification(student_email, course_name, grade):
    """Gửi email thông báo điểm cho sinh viên"""
    if not student_email:
        return

    # Nội dung email tùy theo kết quả học tập
    if grade < 5:
        subject = f"[CẢNH BÁO] Kết quả học tập môn {course_name}"
        body = (
            f"Điểm của bạn trong môn {course_name} là {grade}. "
            f"Vui lòng liên hệ cố vấn học tập để được hỗ trợ cải thiện kết quả."
        )
    elif grade >= 8:
        subject = f"[CHÚC MỪNG] Kết quả học tập môn {course_name}"
        body = (
            f"Xin chúc mừng! Bạn đã đạt {grade} điểm trong môn {course_name}. "
            f"Tiếp tục phát huy tinh thần học tập tốt nhé!"
        )
    else:
        subject = f"Kết quả học tập môn {course_name}"
        body = f"Điểm của bạn trong môn {course_name} là {grade}."

    msg = Message(subject=subject, recipients=[student_email], body=body)
    mail.send(msg)
