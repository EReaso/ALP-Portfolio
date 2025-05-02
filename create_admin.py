
from main import app, db, User

def create_admin():
    password = input("Enter admin password: ")
    
    try:
        # Create all tables
        with app.app_context():
            db.create_all()
            # Check if admin already exists
            if User.query.first() is None:
                User.create_admin(password)
                print("Admin user created successfully!")
            else:
                print("Admin user already exists!")
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin()
