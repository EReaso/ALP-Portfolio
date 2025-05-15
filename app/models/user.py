from app.extensions import db
from flask_login import UserMixin
from flask import current_app
import bcrypt


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  password = db.Column(db.Text, nullable=False)

  @classmethod
  def create_admin(cls, password):
      with current_app.app_context():
          cls.query.delete()
          hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
          admin = cls(password=hashed)
          db.session.add(admin)
          db.session.commit()