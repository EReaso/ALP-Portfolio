from app import app

if __name__ == '__main__':
    app.run("localhost", 8000)
else:
    gunicorn_app = app
