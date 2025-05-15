from flask import Blueprint, render_template, current_app
from app.extensions import db, login_manager
from app.models.user import User


bp = Blueprint("main", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/artifacts/", methods=["GET"])
def artifacts_get():
    return render_template("artifacts.html", months=current_app.months)

@bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500