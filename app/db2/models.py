from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from .pg import Base
from sqlalchemy.orm import relationship

class User(Base):
    # tablename = 'users'
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

class Survey(Base):
    # tablename = 'surveys'
    __tablename__ = 'surveys'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    is_single_choice = Column(Boolean, default=False)
    user = relationship('User', backref='surveys')

class Option(Base):
    # tablename = 'options'
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    option_text = Column(String(255), nullable=False)

class Vote(Base):
    # tablename = 'votes'
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    voter_ip = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())

class VoteOption(Base):
    # tablename = 'vote_options'
    __tablename__ = 'vote_options'
    id = Column(Integer, primary_key=True)
    vote_id = Column(Integer, ForeignKey('votes.id'), nullable=False)
    option_id = Column(Integer, ForeignKey('options.id'), nullable=False)