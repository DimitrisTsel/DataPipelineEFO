# EFO Data Pipeline

This project implements a datapipeline to extract, parse, and load Experimental Factor Ontology (EFO)
terms, synonyms, and parent relationships from the Ontology Lookup Service (OLS) API into a PostgreSQL database.  

## The pipeline

1. Initializes the PostgreSQL database and create tables if they do not exist.
2. Extracts EFO terms from the Ontology Lookup Service (OLS) API.
3. Parses the extracted dataset into separate lists of terms, synonyms, and parent links.
4. Loads the parsed data into the PostgreSQL tables using a bulk insert/upsert strategy.
5. Prints confirmation when the pipeline finishes successfully.

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
- `docker start efo-postgres`

Run the pipeline -> `python3 -m main`
