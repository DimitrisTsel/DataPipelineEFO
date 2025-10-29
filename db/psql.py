from sqlalchemy import ForeignKey, UniqueConstraint, create_engine, text
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/efo_db")
with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print(result.fetchone())
    print("Connected to PostgreSQL database")

Base = declarative_base()

class EFO_TERMS(Base):
    __tablename__ = "EFO_TERMS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    TERM_ID = Column(String, unique=True, nullable=False)
    IRI = Column(String)
    LABEL = Column(String)

class EFO_SYNONYMS(Base):
    __tablename__ = "EFO_SYNONYMS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    TERM_ID = Column(String, nullable=False)  # Removed FK
    SYNONYM = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("TERM_ID", "SYNONYM", name="uq_term_synonym"),
    )


class EFO_PARENTS(Base):
    __tablename__ = "EFO_PARENTS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    TERM_ID = Column(String, nullable=False)  # Removed FK
    PARENT_TERM_ID = Column(String, nullable=False)  # Removed FK

    __table_args__ = (
        UniqueConstraint("TERM_ID", "PARENT_TERM_ID", name="uq_parent"),
    )

def init_db():
    """Create all tables in the PostgreSQL database."""
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL database initialized and tables created")