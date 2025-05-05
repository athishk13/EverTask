from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Assign database file
DATABASE_URL = "sqlite:///task_manager.db"

# Create engine and bind the session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# ORM base class
Base = declarative_base()

# Import the user and task table classes, then create the tables
def init_db():
    from app.models.task import Task
    from app.models.user import User
    Base.metadata.create_all(bind=engine)
