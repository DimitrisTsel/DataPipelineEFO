import requests
import time

BASE_URL = "https://www.ebi.ac.uk/ols4/api/ontologies/efo/terms"

def extract_terms(size=100, max_pages=1):
    """
    Fetches EFO terms from the Ontology Lookup Service (OLS) API using pagination.

    This function retrieves terms from the EFO ontology in a paginated manner.
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
    for page in range(total_pages):
        url = f"{BASE_URL}?page={page}&size={size}"
        r = requests.get(url)
        r.raise_for_status()
        terms = r.json().get('_embedded', {}).get('terms', [])
        dataset.extend(terms)
        time.sleep(0.1)

        print(f"Fetched page {page + 1}/{total_pages}, total terms: {len(dataset)}")
    return dataset

def parse_efo_terms(dataset):
    """
    Parses raw EFO term data into structured lists of terms, synonyms, and parent relationships.

    This function processes a list of term dictionaries retrieved from the EFO API
    and extracts:
        - Terms: tuples of (term_id, iri, label)
        - Synonyms: tuples of (term_id, synonym)
        - Parent links: tuples of (term_id, parent_term_id)

    Args:
        dataset (List[dict]): List of term dictionaries as returned by the EFO API.

    Returns:
        Tuple[List[Tuple[str, str, str]], List[Tuple[str, str]], List[Tuple[str, str]]]:
            - terms_list: List of term tuples (term_id, iri, label)
            - synonyms_list: List of synonym tuples (term_id, synonym)
            - parents_list: List of parent tuples (term_id, parent_term_id)
    """

    terms_list = []
    synonyms_list = []
    parents_list = []

    print("Searching for parents...")

    for term in dataset:
        term_id = term.get('obo_id')
        iri = term.get('iri')
        label = term.get('label')
        
        if not term_id:
            continue

        terms_list.append((term_id, iri, label))

        for syn in term.get('synonyms', []):
            if syn:  # skip null/empty
                synonyms_list.append((term_id, syn))
                
        if '_links' in term and 'parents' in term['_links']:
            parent_url = term['_links']['parents']['href']
            r = requests.get(parent_url)
            r.raise_for_status()
            parents = r.json().get('_embedded', {}).get('terms', [])
            for p in parents:
                parent_id = p.get('obo_id')
                if parent_id:
                    parents_list.append((term_id, parent_id))

    return terms_list, synonyms_list, parents_list