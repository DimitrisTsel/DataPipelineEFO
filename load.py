from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from db.init_db import engine as psql_engine
from db.stg_schema import EFO_TERMS, EFO_SYNONYMS, EFO_PARENTS
from datetime import datetime

def load_efo_term(**kwargs):
    """
    Inserts or updates EFO terms, synonyms, and parent links into the PostgreSQL database.

    This function implements an incremental load with upsert logic:
      - EFO terms are updated only if the incoming LOAD_DTM is newer and either the IRI or LABEL changed.
      - EFO synonyms are updated only if the incoming LOAD_DTM is newer and the synonym changed.
      - EFO parent links are inserted if not already present (duplicates are skipped).

    Accepts keyword arguments:
        - terms: List[Tuple[str, str, str]] -> (TERM_ID, IRI, LABEL)
        - synonyms: List[Tuple[str, str]] -> (TERM_ID, SYNONYM)
        - parents: List[Tuple[str, str]] -> (TERM_ID, PARENT_TERM_ID)

    Returns:
        None
    """
    
    
    terms = kwargs.get('terms', [])
    synonyms = kwargs.get('synonyms', [])
    parents = kwargs.get('parents', [])

    # Deduplicate before inserting
    if terms:
        terms = list({(tid, iri, label, datetime.now()) for tid, iri, label in terms})
    if synonyms:
        synonyms = list({(tid, syn, datetime.now()) for tid, syn in synonyms})
    if parents:
        parents = list({(child, parent, datetime.now()) for child, parent in parents})

    with Session(psql_engine) as session:
        if terms:
            stmt_terms = insert(EFO_TERMS).values([
                {"TERM_ID": tid, "IRI": iri, "LABEL": label, "LOAD_DTM": load_dtm} for tid, iri, label, load_dtm in terms
            ])
            stmt_terms = stmt_terms.on_conflict_do_update(
                index_elements=["TERM_ID"],
                set_={
                    "IRI": stmt_terms.excluded.IRI,
                    "LABEL": stmt_terms.excluded.LABEL,
                    "LOAD_DTM": stmt_terms.excluded.LOAD_DTM
                },
                where=(EFO_TERMS.LOAD_DTM < stmt_terms.excluded.LOAD_DTM) &
                        (EFO_TERMS.IRI != stmt_terms.excluded.IRI or EFO_TERMS.LABEL != stmt_terms.excluded.LABEL)
            )
            session.execute(stmt_terms)

        if parents:
            stmt_parents = insert(EFO_PARENTS).values([
                {"TERM_ID": child, "PARENT_TERM_ID": parent, "LOAD_DTM": load_dtm} for child, parent, load_dtm in parents
            ])
            stmt_parents = stmt_parents.on_conflict_do_nothing(
                index_elements=["TERM_ID", "PARENT_TERM_ID"]  # skip duplicates
            )
            session.execute(stmt_parents)

        if synonyms:
            stmt_synonyms = insert(EFO_SYNONYMS).values([
                {"TERM_ID": tid, "SYNONYM": syn, "LOAD_DTM": load_dtm} for tid, syn, load_dtm in synonyms
            ])
            stmt_synonyms = stmt_synonyms.on_conflict_do_update(
                index_elements=["TERM_ID", "SYNONYM"],
                set_={
                    "LOAD_DTM": stmt_synonyms.excluded.LOAD_DTM
                },
                where=(EFO_SYNONYMS.LOAD_DTM < stmt_synonyms.excluded.LOAD_DTM) &
                        (EFO_SYNONYMS.SYNONYM != stmt_synonyms.excluded.SYNONYM)
            )
            session.execute(stmt_synonyms)

        session.commit()
