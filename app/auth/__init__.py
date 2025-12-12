# app/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")

from . import routes  # Import routes sau khi khai báo blueprint
