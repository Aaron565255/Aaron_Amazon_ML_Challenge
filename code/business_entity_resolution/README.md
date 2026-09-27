# Amazon Business Entity Resolution

This project performs business entity resolution between Source 1,
Source 2 and Source 3.

## Input

The input data contains:

- entity_id
- business_name
- business_address
- country

All input files are TSV files.

## Pipeline

1. Normalize business names and addresses.
2. Build a SQLite index for Source 2 and Source 3.
3. Generate candidate matches using blocking.
4. Calculate fuzzy name and address similarity.
5. Select high-confidence matches.
6. Generate candidate_pairs.tsv.
7. Generate matching_results.tsv.
8. Validate the outputs.

## Run

From the project root:

```text
python code\business_entity_resolution\src\run_pipeline.py