from flask import Blueprint, render_template, request, redirect, flash
from flask_login import logout_user, current_user, login_user
from app.models.user import User
import bcrypt

bp = Blueprint("auth", __name__)

@bp.route("/logout/")
def logout():
    logout_user()
    return redirect("/")


@bp.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            password = request.form.get("password", "").encode("utf-8")
            user = User.query.first()  # Get the only user (admin)
            if user and bcrypt.checkpw(password, user.password):
                login_user(user)
                flash('Logged in successfully', 'success')
                return redirect("/admin/artifacts/")
            flash('Invalid password', 'error')
        except Exception as e:
            flash('Login error occurred', 'error')
        return render_template("login.html", error="Invalid password")
    elif current_user.is_authenticated:
        return redirect("/admin/artifacts/")
    return render_template("login.html")