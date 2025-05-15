from app.models.artifact import Artifact

class Month:
  def __init__(self, date):
      self.date = date
      self.artifacts = []

  def __str__(self):
      return self.date.strftime('%B %Y')

  def add_artifact(self, artifact):
      self.artifacts.append(artifact)

  @staticmethod
  def init():
      artifacts = Artifact.query.order_by(Artifact.date.desc()).all()
      months = []

      for artifact in artifacts:
          month_date = artifact.date.replace(day=1)
          if month_date not in (month.date for month in months):
              months.append(month_date)
              current_month = Month(month_date)
              months.append(current_month)
              current_month.add_artifact(artifact)
          else:
              for month in months:
                  if month.date == month_date:
                      month.add_artifact(artifact)
                      break
      return months

