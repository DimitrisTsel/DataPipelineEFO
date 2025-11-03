from sqlalchemy import DateTime, UniqueConstraint, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class EFO_TERMS(Base):
    """
    EFO terms table.
    Uses the STG schema.

    Attributes:
        TERM_ID (str): Primary key, unique EFO term identifier.
        IRI (str): Internationalized Resource Identifier for the term.
        LABEL (str): Human-readable label of the term.
        LOAD_DTM (datetime): Timestamp when the term was loaded/updated.
    """
    __tablename__ = "EFO_TERMS"
    __table_args__ = {'schema': "stg"}  

    TERM_ID = Column(String, primary_key=True, nullable=False)
    IRI = Column(String)
    LABEL = Column(String)
    LOAD_DTM = Column(DateTime)

class EFO_SYNONYMS(Base):
    """
    EFO synonyms table.
    Uses the STG schema.

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
        {'schema': "stg"}
    )


class EFO_PARENTS(Base):
    """
    EFO parent-child relationships table.
    Uses the STG schema.

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
        {'schema': "stg"}
    )
