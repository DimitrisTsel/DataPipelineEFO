from sqlalchemy import text
from db.init_db import engine as psql_engine

def transform_stg_to_ods():
    """
    Transforms and loads data from the staging schema (stg)
    into the operational data store (ods) schema.

    This function performs the following operations:
        - Moves all terms from stg.EFO_TERMS to ods.terms_ods with upsert logic.
        - Moves parent relationships from stg.EFO_PARENTS to ods.parents_ods
          only if both child and parent terms exist in ods.terms_ods.
        - Moves synonyms from stg.EFO_SYNONYMS to ods.synonyms_ods
          only if the term exists in ods.terms_ods.
        - Cleans up staging data that was successfully moved to ODS.
    """
    with psql_engine.begin() as conn:

        # Inserts all terms from staging -> ODS
        conn.execute(text("""
            INSERT INTO ods.terms_ods (term_id, iri, label, load_dtm)
            SELECT "TERM_ID", "IRI", "LABEL", "LOAD_DTM"
            FROM stg."EFO_TERMS"
            ON CONFLICT (term_id) DO UPDATE
            SET 
                iri = EXCLUDED.iri,
                label = EXCLUDED.label,
                load_dtm = EXCLUDED.load_dtm
            WHERE ods.terms_ods.load_dtm < EXCLUDED.load_dtm;
        """))

        # Inserts parent relationships to ODS only if both terms exist in terms_ods 
        conn.execute(text("""
            INSERT INTO ods.parents_ods (term_id, parent_term_id, load_dtm)
            SELECT sp."TERM_ID", sp."PARENT_TERM_ID", sp."LOAD_DTM"
            FROM stg."EFO_PARENTS" sp
            JOIN ods."terms_ods" t ON sp."TERM_ID" = t.term_id
            JOIN ods."terms_ods" p ON sp."PARENT_TERM_ID" = p."term_id"
            ON CONFLICT (term_id, parent_term_id) DO NOTHING;
        """))

        # Inserts synonyms only if term exists in ODS terms_ods
        conn.execute(text("""
            INSERT INTO ods.synonyms_ods (term_id, synonym, load_dtm)
            SELECT ss."TERM_ID", ss."SYNONYM", ss."LOAD_DTM"
            FROM stg."EFO_SYNONYMS" ss
            JOIN ods."terms_ods" t ON ss."TERM_ID" = t.term_id
            ON CONFLICT (term_id, synonym) DO UPDATE
            SET load_dtm = GREATEST(ods.synonyms_ods.load_dtm, EXCLUDED.load_dtm);
        """))

        # Cleans up staging data that was successfully moved from STG to ODS
        conn.execute(text("""
            DELETE FROM stg."EFO_PARENTS" sp
            WHERE EXISTS (
                SELECT 1 
                FROM ods.parents_ods ep
                WHERE ep.term_id = sp."TERM_ID" 
                  AND ep.parent_term_id = sp."PARENT_TERM_ID"
            );
        """))

        conn.execute(text("""
            DELETE FROM stg."EFO_SYNONYMS" ss
            WHERE EXISTS (
                SELECT 1 
                FROM ods.synonyms_ods es
                WHERE es.term_id = ss."TERM_ID" 
                  AND es.synonym = ss."SYNONYM"
            );
        """))

        conn.execute(text("""
            DELETE FROM stg."EFO_TERMS" st
            WHERE EXISTS (
                SELECT 1 
                FROM ods.terms_ods et
                WHERE et.term_id = st."TERM_ID"
            );
        """))

    print("Data moved from STG to ODS.")
