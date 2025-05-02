
from main import db, User
import sys

def create_admin():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    
    try:
        User.create_admin(username, password)
        print("Admin user created successfully!")
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin()
