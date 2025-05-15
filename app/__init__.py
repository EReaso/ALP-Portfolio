from app.extensions import db, login_manager
from flask import Flask, render_template
import app.config as config
from app.models.user import User
from app.models.month import Month



class App(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.months = []


app = App(__name__)
app.config.from_object(config.Config)
db.init_app(app)
login_manager.init_app(app)

from app.routes.auth import bp as auth_bp
from app.routes.admin import bp as admin_bp
from app.routes.main import bp as main_bp
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)

with app.app_context():
    app.months = Month.init()
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
