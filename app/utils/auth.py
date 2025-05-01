import bcrypt
from sqlalchemy.orm import Session
from models.user import User

def create_user(session: Session, username: str, password: str):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(username=username, password_hash=password_hash)
    session.add(user)
    session.commit()

def authenticate(session: Session, username: str, password: str):
    user = session.query(User).filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return user
    return None
