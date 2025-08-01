# models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from data.database import Base  # Correct import from database module

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, index=True)  # Remove unique=True here
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    score = Column(Integer)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityEntry(Base):
    __tablename__ = "activity_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    activity = Column(String)
    duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    entry = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)