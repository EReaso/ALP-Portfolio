from flask import Blueprint, render_template, request, redirect, flash, current_app
from flask_login import current_user, login_required
from markupsafe import escape
import datetime
from app.models.artifact import Artifact
from app.extensions import db
from app.models.month import Month
from sqlalchemy.exc import SQLAlchemyError


bp = Blueprint("admin", __name__)

@login_required
@bp.route("/admin/artifacts/", methods=["GET", "POST"])
def admin_artifacts():
    if not current_user.is_authenticated:
        flash('Unauthorized access', 'error')
        return redirect("/")

    if request.method == "GET":
        return render_template("admin_artifacts.html")

    title = escape(request.form.get("title"))
    description = escape(request.form.get("description"))
    badges = escape(request.form.get("badges"))
    date_str = request.form.get("date")

    if not all([title, description, badges, date_str]):
        flash('All fields are required', 'error')
        return redirect(request.url)

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    artifact = Artifact(title=title,
                        description=description,
                        badges=badges,
                        date=date)
    db.session.add(artifact)
    db.session.commit()
    current_app.months = Month.init()
    flash('Artifact created successfully', 'success')
    return redirect("/artifacts/")


@bp.route("/artifacts/<int:id>/edit/", methods=["GET", "POST"])
@login_required
def edit_artifact(id):
    if not current_user.is_authenticated:
        flash('Unauthorized access', 'error')
        return redirect("/")

    try:
        artifact = Artifact.query.get_or_404(id)

        if request.method == "GET":
            return render_template("edit_artifact.html", artifact=artifact)

        artifact.title = escape(request.form.get("title"))
        artifact.description = escape(request.form.get("description"))
        artifact.badges = escape(request.form.get("badges"))
        db.session.commit()
        flash('Artifact updated successfully', 'success')
        return redirect("/artifacts/")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error updating artifact', 'error')
        return redirect(request.url)


@bp.route("/artifacts/<int:id>/delete/", methods=["POST"])
@login_required
def delete_artifact(id):
    if not current_user.is_authenticated:
        flash('Unauthorized access', 'error')
        return redirect("/")

    try:
        artifact = Artifact.query.get_or_404(id)
        db.session.delete(artifact)
        db.session.commit()
        flash('Artifact deleted successfully', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error deleting artifact', 'error')
    return redirect("/artifacts/")
