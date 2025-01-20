from sqlalchemy import MetaData, Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database connection string
DATABASE_URL = "postgresql://practice_user:Vaibhav1@localhost/campaigdb"

# SQLAlchemy setup
metadata = MetaData()
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# SQLAlchemy model
class PracticeUser(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('auth_user.id', ondelete='CASCADE'))  # Reference Django's User table
    roles = Column(String)

# Create tables
Base.metadata.create_all(engine)
