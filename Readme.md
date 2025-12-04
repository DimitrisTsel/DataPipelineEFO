# EFO Data Pipeline

This project implements a data pipeline to extract, parse, and load 
Experimental Factor Ontology (EFO) data from the Ontology Lookup Service (OLS) API 
(https://www.ebi.ac.uk/ols4/api-docs) into a PostgreSQL database.

## The pipeline

1. Initializes the PostgreSQL database and create schemas and tables.
2. Extracts EFO terms, synonyms, and parent relationships from the Ontology Lookup Service (OLS) API 
   using paginated requests and multithreading.
3. Parses the extracted dataset into separate lists of terms, synonyms, and parent links.
4. Loads the parsed data into the staging schema (stg) in batches.
5. Transforms and moves valid data from the staging schema (stg) to the normalized ODS schema (ods),
   ensuring referential integrity:
    - Terms are upserted into ods.terms_ods, updating only if incoming load_dtm is newer.
    - Parent relationships are inserted into ods.parents_ods only if both child and parent terms exist in ods.terms_ods.
    - Synonyms are inserted/updated into ods.synonyms_ods only if the term exists in ods.terms_ods.
6. Cleans up staging tables by removing records that were successfully promoted to ODS.

## Prerequisites

- Python 3
- Docker

Steps: \
Setup Python env
- Create a Python virtual env and execute it -> `python3 -m venv venv` -> `source venv/bin/activate`
- `pip install -r requirements.txt` \

Setup PostgreSQL:

- `docker pull postgres:15`
- `docker run --name efo-postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=efo_db \
    -p 5432:5432 \
    -d postgres:15`
- Check if PostgreSQL is running -> `docker ps`
- `docker exec -it postgres-efo bash`
- `psql -U postgres -d efo_db`

Run the pipeline -> `python3 -m main`
