import os
from flask import Flask
from .extensions import db, migrate, login_manager, csrf
from .config import Config
from .models import User, Role
from datetime import datetime
from .auth.routes import auth_bp
from .main.routes import main_bp
from .students.routes import students_bp
from .courses.routes import courses_bp
from .enrollments.routes import enroll_bp
from .exams.routes import exam_bp
from .schedules.routes import schedule_bp
from .extensions import db, migrate, login_manager, csrf, mail
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(enroll_bp, url_prefix="/enrollments")
    app.register_blueprint(exam_bp, url_prefix="/exams")
    app.register_blueprint(schedule_bp, url_prefix="/schedules")

    from .seed import register_seed_command
    register_seed_command(app)
   # === Inject biến global cho Jinja2 ===
    @app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.now().year,  # dùng cho footer {{ current_year }}
            "now": datetime.now                   # nếu template nào xài {{ now() }}
        }
    return app
