from sqlalchemy import create_engine, insert, Table, MetaData
from db.schema import EFO_TERMS, EFO_SYNONYMS, EFO_PARENTS
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///efo.db', echo=False)  # change path or use PostgreSQL if needed
metadata = MetaData()

def bulk_insert_efo(terms, synonyms, parents):
    with Session(engine) as session:
        # Terms
        stmt_terms = insert(EFO_TERMS).values([
            {"TERM_ID": tid, "IRI": iri, "LABEL": label} for tid, iri, label in terms
        ])
        stmt_terms = stmt_terms.prefix_with("OR IGNORE")  # SQLite: skip duplicates
        session.execute(stmt_terms)

        # Synonyms
        stmt_syn = insert(EFO_SYNONYMS).values([
            {"TERM_ID": tid, "SYNONYM": syn} for tid, syn in synonyms
        ])
        stmt_syn = stmt_syn.prefix_with("OR IGNORE")
        session.execute(stmt_syn)

        # Parents
        stmt_par = insert(EFO_PARENTS).values([
            {"TERM_ID": child, "PARENT_TERM_ID": parent} for child, parent in parents
        ])
        stmt_par = stmt_par.prefix_with("OR IGNORE")
        session.execute(stmt_par)

        session.commit()