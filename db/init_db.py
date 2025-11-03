from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from db.stg_schema import Base as StgBase
from db.ods_schema import Base as OdsBase


engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/efo_db")
with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT version();"))
        print(result.fetchone())
        print("Connected to PostgreSQL database")
    except Exception as e:
        print(f"Error connecting to database: {e}")

Base = declarative_base()

def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS stg"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ods"))
    # Create all tables
    StgBase.metadata.create_all(bind=engine)
    OdsBase.metadata.create_all(bind=engine)
    print("PostgreSQL database initialized and tables created")
