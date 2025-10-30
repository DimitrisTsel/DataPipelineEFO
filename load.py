from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from db.psql import engine as psql_engine
from db.psql import EFO_TERMS, EFO_SYNONYMS, EFO_PARENTS

def insert_efo_term(terms, synonyms, parents):
    # Deduplicate before inserting
    terms = list({(tid, iri, label) for tid, iri, label in terms})
    synonyms = list({(tid, syn) for tid, syn in synonyms})
    parents = list({(child, parent) for child, parent in parents})

    with Session(psql_engine) as session:
        if terms:
            stmt_terms = insert(EFO_TERMS).values([
                {"TERM_ID": tid, "IRI": iri, "LABEL": label} for tid, iri, label in terms
            ])
            stmt_terms = stmt_terms.on_conflict_do_update(
                index_elements=["TERM_ID"],
                set_={
                    "IRI": stmt_terms.excluded.IRI,
                    "LABEL": stmt_terms.excluded.LABEL
                }
            )
            session.execute(stmt_terms)

        if parents:
            stmt_parents = insert(EFO_PARENTS).values([
                {"TERM_ID": child, "PARENT_TERM_ID": parent} for child, parent in parents
            ]).on_conflict_do_nothing(
                index_elements=["TERM_ID", "PARENT_TERM_ID"]
            )
            session.execute(stmt_parents)

        if synonyms:
            stmt_synonyms = insert(EFO_SYNONYMS).values([
                {"TERM_ID": tid, "SYNONYM": syn} for tid, syn in synonyms
            ]).on_conflict_do_nothing(
                index_elements=["TERM_ID", "SYNONYM"]
            )
            session.execute(stmt_synonyms)

        session.commit()


    print("EFO terms, synonyms, and parents inserted/updated successfully")