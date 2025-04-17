from flask import Flask, redirect, render_template, request
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

    @property
    def badges_list(self):
        return self._badges.split(",")
        
    badges = db.Column(db.Text, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text, nullable=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/artifacts/", methods=["GET"])
def artifacts_get():
    return render_template("artifacts.html", artifacts=Artifact.query.all())

@login_required
@app.route("/admin/artifacts/", methods=["GET","POST"])
def admin_artifacts():
    if current_user.id != 1:
        return redirect("/")
    if request.method == "GET":
        return render_template("admin_artifacts.html")
    else:
        title = request.form.get("title")
        description = request.form.get("description")
        badges = request.form.get("badges")
        artifact = Artifact(title=title, description=description, badges=badges)
        db.session.add(artifact)
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
