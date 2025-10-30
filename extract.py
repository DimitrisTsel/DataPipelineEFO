import requests
import time

BASE_URL = "https://www.ebi.ac.uk/ols4/api/ontologies/efo/terms"

def get_terms(size=100, max_pages=1):
    """Fetch terms from EFO API (paginated)."""
    first_response = requests.get(f"{BASE_URL}?page=0&size={size}")
    first_response.raise_for_status()
    total_pages = first_response.json()['page']['totalPages']
    total_pages = min(total_pages, max_pages)  # limit pages for testing

    dataset = []
    for page in range(total_pages):
        url = f"{BASE_URL}?page={page}&size={size}"
        r = requests.get(url)
        r.raise_for_status()
        terms = r.json().get('_embedded', {}).get('terms', [])
        dataset.extend(terms)
        time.sleep(0.1)  # be nice to API

        print(f"Fetched page {page + 1}/{total_pages}, total terms: {len(dataset)}")
    return dataset

def EFO_terms(dataset):
    terms_list = []
    synonyms_list = []
    parents_list = []

    for term in dataset:
        term_id = term.get('obo_id')
        iri = term.get('iri')
        label = term.get('label')
        if not term_id:
            continue

        # --- Term
        terms_list.append((term_id, iri, label))

        # --- Synonyms
        for syn in term.get('synonyms', []):
            if syn:  # skip null/empty
                synonyms_list.append((term_id, syn))

        # --- Parents
        if '_links' in term and 'parents' in term['_links']:
            parent_url = term['_links']['parents']['href']
            r = requests.get(parent_url)
            r.raise_for_status()
            parents = r.json().get('_embedded', {}).get('terms', [])
            print(f"Term {term_id} has {len(parents)} parents")
            for p in parents:
                parent_id = p.get('obo_id')
                if parent_id:
                    parents_list.append((term_id, parent_id))

    return terms_list, synonyms_list, parents_list