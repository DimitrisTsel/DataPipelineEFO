from extract import extract_terms, parse_efo_terms
from load import  load_efo_term
from transform import transform_stg_to_ods
from db.init_db import init_db

def run_pipeline():
    """Run the full EFO data pipeline from extraction to loading.

        1. Initialize the PostgreSQL database and create schemas and tables.
        2. Extract EFO terms, synonyms, and parent relationships from the OLS API using paginated requests and multithreading.
        3. Parse the extracted dataset into separate lists of terms, synonyms, and parent links.
        4. Load the parsed data into the staging schema (stg) in batches.
        5. Transform and promote valid data from the staging schema (stg) to the normalized ODS schema (ods),
        ensuring referential integrity:
            - Terms are upserted into ods.terms_ods, updating only if incoming load_dtm is newer.
            - Parent relationships are inserted into ods.parents_ods only if both child and parent terms exist in ods.terms_ods.
            - Synonyms are inserted/updated into ods.synonyms_ods only if the term exists in ods.terms_ods.
        6. Clean up staging tables by removing records that were successfully promoted to ODS.
    """

    init_db()
    dataset = extract_terms(size=100, max_pages=10)
    parse_efo_terms(dataset, BATCH_SIZE=100)
    print("All batches of EFO terms, synonyms, and parents inserted/updated to STG.")
    transform_stg_to_ods()
    print("Pipeline finished successfully.")


if __name__ == "__main__":
    run_pipeline()
