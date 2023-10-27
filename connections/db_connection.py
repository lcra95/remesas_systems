import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+mysqldb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

# Reflect existing database into a new model
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# We can now access the table classes by name using the 'classes' attribute
# For example, if you have a table named 'users', you can access it using Base.classes.users

SessionLocal = sessionmaker(bind=engine)


def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
