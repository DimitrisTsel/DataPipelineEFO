from extract import extract_terms, parse_efo_terms
from load import  load_efo_term
from db.schema import init_db

def run_pipeline():
    """Run the full EFO data pipeline from extraction to loading.

    Steps:
        1. Initialize the PostgreSQL database and create tables if they do not exist.
        2. Extract EFO terms from the Ontology Lookup Service (OLS) API.
        3. Parse the extracted dataset into separate lists of terms, synonyms, and parent links.
        4. Load the parsed data into the PostgreSQL tables using a bulk insert/upsert strategy.
        5. Print confirmation when the pipeline finishes successfully.
    """
    init_db()
    dataset = extract_terms(size=100, max_pages=1)
    terms, synonyms, parents = parse_efo_terms(dataset)
    print(f"Fetched {len(terms)} terms, {len(synonyms)}" +\
          f" synonyms, {len(parents)} parent links")
    load_efo_term(terms, synonyms, parents)
    print("Pipeline finished successfully.")


if __name__ == "__main__":
    run_pipeline()
