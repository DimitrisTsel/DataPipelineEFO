from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, create_engine, text
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/efo_db")
with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT version();"))
        print(result.fetchone())
        print("Connected to PostgreSQL database")
    except Exception as e:
        print(f"Error connecting to database: {e}")

Base = declarative_base()

class EFO_TERMS(Base):
    """
    SQLAlchemy model for EFO terms table.

    Attributes:
        TERM_ID (str): Primary key, unique EFO term identifier.
        IRI (str): Internationalized Resource Identifier for the term.
        LABEL (str): Human-readable label of the term.
        LOAD_DTM (datetime): Timestamp when the term was loaded/updated.
    """
    __tablename__ = "EFO_TERMS"

    TERM_ID = Column(String, primary_key=True, nullable=False)
    IRI = Column(String)
    LABEL = Column(String)
    LOAD_DTM = Column(DateTime)

class EFO_SYNONYMS(Base):
    """
    SQLAlchemy model for EFO synonyms table.

    Attributes:
        ID (int): Primary key, auto-incremented.
        TERM_ID (str): Foreign key reference to EFO_TERMS (conceptually).
        SYNONYM (str): Synonym for the term.
        LOAD_DTM (datetime): Timestamp when the synonym was loaded/updated.

    Constraints:
        UniqueConstraint on (TERM_ID, SYNONYM) to prevent duplicate synonyms.
    """
    __tablename__ = "EFO_SYNONYMS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    TERM_ID = Column(String, nullable=False) 
    SYNONYM = Column(String, nullable=False)
    LOAD_DTM = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("TERM_ID", "SYNONYM", name="uq_term_synonym"),
    )


class EFO_PARENTS(Base):
    """
    SQLAlchemy model for EFO parent-child relationships table.

    Attributes:
        ID (int): Primary key, auto-incremented.
        TERM_ID (str): EFO term ID.
        PARENT_TERM_ID (str): Parent term ID.
        LOAD_DTM (datetime): Timestamp when the parent link was loaded.

    Constraints:
        UniqueConstraint on (TERM_ID, PARENT_TERM_ID) to prevent duplicate parent links.
    """
    __tablename__ = "EFO_PARENTS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    TERM_ID = Column(String, nullable=False)
    PARENT_TERM_ID = Column(String, nullable=False)
    LOAD_DTM = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("TERM_ID", "PARENT_TERM_ID", name="uq_parent"),
    )

def init_db():
    """Create all tables in the PostgreSQL database."""
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL database initialized and tables created")