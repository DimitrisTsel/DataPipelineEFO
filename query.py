# query_efo.py
from sqlalchemy import create_engine, select, Table, MetaData

# --- Connect 
engine = create_engine('sqlite:///efo.db', echo=False) 
metadata = MetaData()


EFO_TERMS = Table('EFO_TERMS', metadata, autoload_with=engine)
EFO_SYNONYMS = Table('EFO_SYNONYMS', metadata, autoload_with=engine)
EFO_PARENTS = Table('EFO_PARENTS', metadata, autoload_with=engine)

with engine.connect() as conn:
    query = select(EFO_TERMS).limit(10)
    print("=== EFO_TERMS ===")
    for row in conn.execute(query):
        print(row)

from sqlalchemy import join
j = join(EFO_TERMS, EFO_SYNONYMS, EFO_TERMS.c.TERM_ID == EFO_SYNONYMS.c.TERM_ID)
query = select(EFO_TERMS.c.TERM_ID, EFO_TERMS.c.LABEL, EFO_SYNONYMS.c.SYNONYM).select_from(j).limit(10)
with engine.connect() as conn:
    print("\n=== Terms with Synonyms ===")
    for row in conn.execute(query):
        print(row)

j = join(EFO_TERMS, EFO_PARENTS, EFO_TERMS.c.TERM_ID == EFO_PARENTS.c.TERM_ID)
query = select(EFO_TERMS.c.TERM_ID, EFO_TERMS.c.LABEL, EFO_PARENTS.c.PARENT_TERM_ID).select_from(j).limit(10)
with engine.connect() as conn:
    print("\n=== Terms with Parents ===")
    for row in conn.execute(query):
        print(row)
