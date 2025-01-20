from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

class Sessionhelper():
    @staticmethod
    def create_session():
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise ValueError("Database url is not provided in env file!") 

        engine = create_engine(database_url)
        session = sessionmaker(bind=engine)
        return session()
