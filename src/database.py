import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Store

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./retail.db")
if DB_URL.startswith("sqlite"):
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    Base.metadata.create_all(engine)
    from .data_generator import seed_demo_data
    with SessionLocal() as session:
        if session.query(Store).count() == 0:
            seed_demo_data(session)

def get_session():
    return SessionLocal()
