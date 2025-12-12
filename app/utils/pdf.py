from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from ..models import Student, Enrollment, grade_to_letter_and_gpa, compute_student_gpa

def build_transcript_pdf(student_id: int):
    stu = Student.query.get_or_404(student_id)
    enrolls = Enrollment.query.filter_by(student_id=student_id).all()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, "BẢNG ĐIỂM - TRANSCRIPT")

    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height-3*cm, f"MSSV: {stu.code}")
    c.drawString(2*cm, height-3.6*cm, f"Họ tên: {stu.full_name}")
    c.drawString(2*cm, height-4.2*cm, f"Lớp: {stu.class_name or ''}")

    y = height-5*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Mã HP")
    c.drawString(5*cm, y, "Tên học phần")
    c.drawString(13*cm, y, "Số TC")
    c.drawString(15*cm, y, "Điểm")
    c.drawString(17*cm, y, "Điểm chữ")
    y -= 0.6*cm
    c.setFont("Helvetica", 10)
    for e in enrolls:
        letter, _ = grade_to_letter_and_gpa(e.grade)
        c.drawString(2*cm, y, f"{e.course.code}")
        c.drawString(5*cm, y, f"{e.course.name[:30]}")
        c.drawRightString(14.5*cm, y, f"{e.course.credits}")
        c.drawRightString(16.5*cm, y, f"{'' if e.grade is None else round(e.grade,1)}")
        c.drawRightString(19*cm, y, f"{letter or ''}")
        y -= 0.55*cm
        if y < 3*cm:
            c.showPage()
            y = height-2*cm

    gpa, creds = compute_student_gpa(student_id)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, 2.5*cm, f"Tổng số tín chỉ: {creds}   GPA (4.0): {gpa}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue(), f"transcript_{stu.code}.pdf"
