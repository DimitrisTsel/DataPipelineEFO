from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from load import load_efo_term

BASE_URL = "https://www.ebi.ac.uk/ols4/api/ontologies/efo/terms"

def fetch_pages(page, size):
    """Fetch a single page of EFO terms and store the results in a shared list."""

    url = f"{BASE_URL}?page={page}&size={size}"
    r = requests.get(url)
    r.raise_for_status()
    terms = r.json().get("_embedded", {}).get("terms", [])
    return terms

def extract_terms(size=100, max_pages=1):
    """
    Fetches EFO terms from the Ontology Lookup Service (OLS) API using pagination.

    This function retrieves terms from the EFO ontology in a paginated manner.
    Uses multithreading to fetch pages concurrently.
    The number of terms per page can be controlled via `size`, and the number
    of pages fetched can be limited via `max_pages`.

    Args:
        size (int, optional): Number of terms to fetch per API request. Defaults to 100.
        max_pages (int, optional): Maximum number of pages to fetch. Defaults to 1.

    Returns:
        List[dict]: A list of term dictionaries as returned by the EFO API.
    """

    first_response = requests.get(f"{BASE_URL}?page=0&size={size}")
    first_response.raise_for_status()
    total_pages = first_response.json()['page']['totalPages']
    total_pages = min(total_pages, max_pages)  # limit pages for testing

    dataset = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = []

        for page in range(0, total_pages):
            futures.append(pool.submit(fetch_pages, page, size))

        # Collect results as threads finish
        for fut in as_completed(futures):
            dataset.extend(fut.result())

    return dataset

def fetch_parents(term_id, parent_url):
    """Fetch parent terms for a single term."""

    r = requests.get(parent_url)
    r.raise_for_status()
    parents = r.json().get("_embedded", {}).get("terms", [])
    return term_id, [p.get("obo_id") for p in parents if p.get("obo_id")]

def parse_efo_terms(dataset, BATCH_SIZE=50):
    """
    Parses raw EFO term data into structured lists of terms, synonyms, and parent relationships.
    Uses multithreading to fetch parent relationships concurrently.
    This function processes a list of term dictionaries retrieved from the EFO API
    and extracts:
        - Terms: tuples of (term_id, iri, label)
        - Synonyms: tuples of (term_id, synonym)
        - Parent links: tuples of (term_id, parent_term_id)

    Bulk inserts are performed in batches to optimize database loading.
        - If the number of terms, synonyms, or parents reaches a batch size,
          it calls `load_efo_term` to insert them into the database and clears the lists

    Args:
        dataset (List[dict]): List of term dictionaries as returned by the EFO API.
        BATCH_SIZE (int, optional): Number of records to batch before loading into the database. Defaults to 50.
    
    Returns:
        None
    """

    terms_list = []
    synonyms_list = []
    parents_urls = []
    print("Searching for parents...")

    for term in dataset:
        term_id = term.get('obo_id')
        if not term_id:
            continue
        iri = term.get('iri')
        label = term.get('label')

        terms_list.append((term_id, iri, label))

        for syn in term.get('synonyms', []):
            if syn:  # skip null/empty
                synonyms_list.append((term_id, syn))

        parent_link = term.get("_links", {}).get("parents", {}).get("href")
        if parent_link:
            parents_urls.append((term_id, parent_link))
        
        if len(terms_list) >= BATCH_SIZE:
            load_efo_term(terms = terms_list)
            terms_list.clear()
        if len(synonyms_list) >= BATCH_SIZE:
            load_efo_term(synonyms = synonyms_list)
            synonyms_list.clear()

    parents_list = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [
            pool.submit(fetch_parents,tid, url)
            for tid, url in parents_urls
        ]
        for fut in as_completed(futures):
            term_id, parent_ids = fut.result()
            for pid in parent_ids:
                parents_list.append((term_id, pid))
        
            if len(parents_list) >= BATCH_SIZE:
                load_efo_term(parents = parents_list)
                parents_list.clear()

    # Load any remaining records
    if terms_list or synonyms_list or parents_list:
        load_efo_term(terms = terms_list, synonyms = synonyms_list, parents = parents_list)