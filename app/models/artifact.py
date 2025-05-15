from app.extensions import db
from markupsafe import escape

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
