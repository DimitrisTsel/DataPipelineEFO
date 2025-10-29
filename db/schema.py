from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey



engine = create_engine('sqlite:///efo.db', echo=True)
metadata_obj = MetaData()

EFO_TERMS = Table(
    'EFO_TERMS', metadata_obj,
    Column('ID', Integer, primary_key=True, autoincrement=True),
    Column('TERM_ID', String, unique=True, nullable=False),
    Column('IRI', String),
    Column('LABEL', String)
)

EFO_SYNONYMS = Table(
    'EFO_SYNONYMS', metadata_obj,
    Column('ID', Integer, primary_key=True, autoincrement=True),
    Column('TERM_ID', String, ForeignKey('EFO_TERMS.TERM_ID')),
    Column('SYNONYM', String, nullable=False)
)

EFO_PARENTS = Table(
    'EFO_PARENTS', metadata_obj,
    Column('ID', Integer, primary_key=True, autoincrement=True),
    Column('TERM_ID', String, ForeignKey('EFO_TERMS.TERM_ID')),
    Column('PARENT_TERM_ID', String, ForeignKey('EFO_TERMS.TERM_ID'))
)

def init_db():
    """Create all tables if they do not exist."""
    metadata_obj.create_all(engine)
    print("Database initialized and tables created")
