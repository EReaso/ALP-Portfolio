
from flask import Flask, redirect, render_template, request, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import bcrypt
from markupsafe import escape
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Artifact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    badges = db.Column(db.Text, nullable=False)

    @property
    def badges_list(self):
        return [escape(badge) for badge in self.badges.split(",")]

    def to_dict(self):
        return {
            'id': self.id,
            'title': escape(self.title),
            'description': escape(self.description),
            'date': self.date.isoformat(),
            'badges': self.badges_list
        }

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    @classmethod
    def create_admin(cls, username, password):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        admin = cls(username=username, password=hashed, is_admin=True)
        db.session.add(admin)
        db.session.commit()

class Month:
    def __init__(self, date):
        self.date = date
        self.artifacts = []
        
    def __str__(self):
        return self.date.strftime('%B %Y')
    
    def add_artifact(self, artifact):
        self.artifacts.append(artifact)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/artifacts/", methods=["GET"])
def artifacts_get():
    try:
        artifacts = Artifact.query.order_by(Artifact.date.desc()).all()
        months = []
        month_dates = set()
        
        for artifact in artifacts:
            month_date = artifact.date.replace(day=1)
            if month_date not in month_dates:
                month_dates.add(month_date)
                current_month = Month(month_date)
                months.append(current_month)
                current_month.add_artifact(artifact)
            else:
                for month in months:
                    if month.date == month_date:
                        month.add_artifact(artifact)
                        break
        return render_template("artifacts.html", months=months)
    except SQLAlchemyError as e:
        flash('Database error occurred', 'error')
        return redirect('/')

@app.route("/admin/artifacts/", methods=["GET", "POST"])
@login_required
def admin_artifacts():
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect("/")
    
    if request.method == "GET":
        return render_template("admin_artifacts.html")
    
    try:
        title = escape(request.form.get("title"))
        description = escape(request.form.get("description"))
        badges = escape(request.form.get("badges"))
        date_str = request.form.get("date")
        
        if not all([title, description, badges, date_str]):
            flash('All fields are required', 'error')
            return redirect(request.url)
            
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        artifact = Artifact(title=title, description=description, badges=badges, date=date)
        db.session.add(artifact)
        db.session.commit()
        flash('Artifact created successfully', 'success')
        return redirect("/artifacts/")
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        flash('Error creating artifact', 'error')
        return redirect(request.url)

@app.route("/artifacts/<int:id>/edit/", methods=["GET", "POST"])
@login_required
def edit_artifact(id):
    if not current_user.is_admin:
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

@app.route("/artifacts/<int:id>/delete/", methods=["POST"])
@login_required
def delete_artifact(id):
    if not current_user.is_admin:
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

@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/")

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password", "").encode("utf-8")
            
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.checkpw(password, user.password):
                login_user(user)
                flash('Logged in successfully', 'success')
                return redirect("/admin/artifacts/")
            flash('Invalid username or password', 'error')
        except Exception as e:
            flash('Login error occurred', 'error')
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
