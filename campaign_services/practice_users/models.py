from sqlalchemy import MetaData, Column, Integer, String, DateTime, create_engine, ForeignKey, Table
from sqlalchemy .orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://practice_user:Vaibhav1@localhost/campaigdb"
metadata = MetaData()
Base = declarative_base()
engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)

auth_user = Table(
        'auth_user', metadata, autoload_with = engine
)

class PracticeUser(Base):
    __tablename__ = 'users'

    id  = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey(auth_user.c.id, ondelete='CASCADE'))
    roles = Column(String)

Base.metadata.create_all(engine)
