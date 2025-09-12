from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    crop = Column(String, nullable=False)
    n = Column(Integer, nullable=False)
    p = Column(Integer, nullable=False)
    k = Column(Integer, nullable=False)
    fertilizer = Column(String, nullable=False)
