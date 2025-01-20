from sqlalchemy import MetaData, Column, Integer, String, DateTime, create_engine, ForeignKey
from sqlalchemy .orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from django.contrib.auth.models import User

DATABASE_URL = "postgresql://practice_user:Vaibhav1@localhost/campaigdb"
metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)

class PracticeUser(Base):
    __tablename__ = 'users'

    id  = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey(User), ondelete='CASCADE')
    roles = Column(String)

Base.metadata.create_all(engine)
