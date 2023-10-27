from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+mysqldb://lrequena:18594LCra..@170.239.85.238:3306/remesas_systems"

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
