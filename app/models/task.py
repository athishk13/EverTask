from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from database.db import Base

# Task table, inherits from ORM Base class
class Task(Base):
    # Table name
    __tablename__ = 'tasks'

    # Attributes
    task_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    # Links tasks to user
    user_id = Column(Integer, ForeignKey("users.user_id"))
    description = Column(String, nullable=True)
    due_date = Column(Date, nullable=False)
    priority = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    complete = Column(Boolean, nullable=False)

    # Define the relationship to User
    owner = relationship("User", back_populates="tasks")