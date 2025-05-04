from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from database.db import Base

class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    description = Column(String, nullable=True)
    due_date = Column(Date, nullable=False)
    priority = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    complete = Column(Boolean, nullable=False)

    owner = relationship("User", back_populates="tasks")