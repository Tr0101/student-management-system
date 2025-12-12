from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models import User
from .forms import LoginForm  # 🟢 import form mới
from app.extensions import csrf

from . import auth_bp

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Sai email hoặc mật khẩu!", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Đã đăng xuất!", "info")
    return redirect(url_for("auth.login"))
