from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base

# User table, inherits from ORM Base class
class User(Base):
    # Table name
    __tablename__ = 'users'

    # Attributes
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Define relationship to Task
    tasks = relationship("Task", back_populates="owner")
