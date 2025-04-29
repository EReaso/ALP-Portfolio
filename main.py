from flask import Flask, redirect, render_template, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Artifact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    badges = db.Column(db.Text, nullable=False)

    @property
    def badges_list(self):
        return self.badges.split(",")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text, nullable=False)

    @classmethod
    def create_user(cls):
        db.session.add(cls(password=bcrypt.hashpw(input("password").encode("utf-8"), bcrypt.gensalt())))
        db.session.commit()
 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/artifacts/", methods=["GET"])
def artifacts_get():
    return render_template("artifacts.html", artifacts=Artifact.query.all())

@login_required
@app.route("/admin/artifacts/", methods=["GET", "POST"])
def admin_artifacts():
    if not current_user.is_authenticated:
        return redirect("/")
    if request.method == "GET":
        return render_template("admin_artifacts.html")
    else:
        title = request.form.get("title")
        description = request.form.get("description")
        badges = request.form.get("badges")
        date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
        artifact = Artifact(title=title, description=description, badges=badges, date=date)
        db.session.add(artifact)
        db.session.commit()
        return redirect("/artifacts/")

@login_required
@app.route("/artifacts/<int:id>/edit/", methods=["GET", "POST"])
def edit_artifact(id):
    if not current_user.is_authenticated:
        return redirect("/")
    artifact = Artifact.query.get_or_404(id)
    if request.method == "GET":
        return render_template("edit_artifact.html", artifact=artifact)
    else:
        artifact.title = request.form.get("title")
        artifact.description = request.form.get("description")
        artifact.badges = request.form.get("badges")
        db.session.commit()
        return redirect("/artifacts/")

@login_required
@app.route("/artifacts/<int:id>/delete/", methods=["POST"])
def delete_artifact(id):
    artifact = Artifact.query.get_or_404(id)
    db.session.delete(artifact)
    db.session.commit()
    return redirect("/artifacts/")

@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/")

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.get(1)
        encoded_pw = request.form.get("password", "").encode("utf-8")
        if bcrypt.checkpw(encoded_pw, user.password):
            login_user(user)
            return redirect("/admin/artifacts/")
        else:
            return render_template("login.html", error="Invalid username or password")
    else:
        return render_template("login.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)