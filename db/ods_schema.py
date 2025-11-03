from sqlalchemy import DateTime, ForeignKey, UniqueConstraint,Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class EFO_TERMS_ODS(Base):
    """
    EFO terms table.
    Uses the ODS schema.

    Attributes:
        term_id (str): Primary key, unique EFO term identifier.
        iri (str): Internationalized Resource Identifier for the term.
        label (str): Human-readable label of the term.
        load_dtm (datetime): Timestamp when the term was loaded or updated.
    """
    __tablename__ = "terms_ods"
    __table_args__ = {"schema": "ods"}

    term_id = Column(String, primary_key=True)
    iri = Column(String)
    label = Column(String)
    load_dtm = Column(DateTime)


class EFO_SYNONYMS_ODS(Base):
    """
    EFO synonyms table.
    Uses the ODS schema.

    Attributes:
        ID (int): Primary key, auto-incremented.
        term_id (str): Foreign key reference to EFO_TERMS_ODS (conceptually).
        synonym (str): Synonym for the term.
        load_dtm (datetime): Timestamp when the synonym was loaded or updated.

    Constraints:
        UniqueConstraint on (term_id, synonym) to prevent duplicate synonyms.
    """

    __tablename__ = "synonyms_ods"
    __table_args__ = (
        UniqueConstraint("term_id", "synonym", name="uq_term_synonym"),
        {"schema": "ods"},
    )
    ID = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(String, ForeignKey("ods.terms_ods.term_id", ondelete="CASCADE"))
    synonym = Column(String, nullable=False)
    load_dtm = Column(DateTime)


class EFO_PARENTS_ODS(Base):
    """
    EFO parent-child relationships table.
    Uses the ODS schema.

    Attributes:
        ID (int): Primary key, auto-incremented.
        term_id (str): EFO term ID (child).
        parent_term_id (str): Parent term ID.
        load_dtm (datetime): Timestamp when the parent link was loaded. 

    Constraints:
        UniqueConstraint on (term_id, parent_term_id) to prevent duplicate parent links.
    """

    __tablename__ = "parents_ods"
    __table_args__ = (
        UniqueConstraint("term_id", "parent_term_id", name="uq_parent"),
        {"schema": "ods"},
    )
    ID = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(String, ForeignKey("ods.terms_ods.term_id", ondelete="CASCADE"))
    parent_term_id = Column(String, ForeignKey("ods.terms_ods.term_id", ondelete="CASCADE"))
    load_dtm = Column(DateTime)
