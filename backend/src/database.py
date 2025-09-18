import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "123")
DB_NAME = os.getenv("POSTGRES_DB", "photogallery")
DB_HOST = os.getenv("POSTGRES_HOST", "db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

while True:
    try:
        conn = engine.connect()
        conn.close()
        break
    except OperationalError:
        print("База ещё не готова, ждём 3 секунды...")
        time.sleep(3)

Base.metadata.create_all(bind=engine)
