from extact import get_terms, EFO_terms
from load import bulk_insert_efo
from db.schema import init_db

if __name__ == "__main__":
    init_db()
    dataset = get_terms(size=100, max_pages=10)  # fetch first 2 pages for testing
    terms, synonyms, parents = EFO_terms(dataset)
    print(f"Fetched {len(terms)} terms, {len(synonyms)} synonyms, {len(parents)} parent links")
    bulk_insert_efo(terms, synonyms, parents)
    print(" Data inserted into database")
