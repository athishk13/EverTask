import bcrypt
from sqlalchemy.orm import Session
from models.user import User
from sqlalchemy.exc import IntegrityError

# Create user function with authentication
def create_user(session: Session, username: str, password: str):
    # Strip whitespaces from username
    username = username.strip()
    # Get the password hash
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Create a new user with the username and password hash
    user = User(username=username, password_hash=password_hash)
    # Add the user
    session.add(user)
    # Check for user already existing
    try:
        session.commit()
        return True
    # IF the user already exists, rollback the commit()
    except IntegrityError:
        session.rollback()
        return False

# Authenticate login function
def authenticate(session: Session, username: str, password: str):
    # Strip whitespaces from username
    username = username.strip()
    # Query User table for username
    user = session.query(User).filter_by(username=username).first()
    # Check that the password matches using encrypted check and return user if valid
    if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return user
    return None
