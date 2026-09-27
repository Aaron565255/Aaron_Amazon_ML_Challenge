import sqlite3
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent))

from config import (
    DB_PATH,
    OUTPUT_ROOT,
    TEST_SOURCE2,
    TEST_SOURCE3,
    CHUNK_SIZE
)

from normalize import (
    name_key,
    address_key,
    name_prefix,
    address_prefix,
    make_block_key
)


def create_database():

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    if DB_PATH.exists():
        print("Existing database found.")
        print("Deleting old database...")
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=OFF")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA cache_size=-500000")

    cursor.execute("""
        CREATE TABLE entities (
            entity_id TEXT PRIMARY KEY,
            business_name TEXT,
            business_address TEXT,
            country TEXT,
            source TEXT,
            name_norm TEXT,
            address_norm TEXT,
            name_prefix TEXT,
            address_prefix TEXT,
            block_key TEXT
        )
    """)

    cursor.execute("""
        CREATE INDEX idx_country_name
        ON entities(country, name_norm)
    """)

    cursor.execute("""
        CREATE INDEX idx_country_address
        ON entities(country, address_norm)
    """)

    cursor.execute("""
        CREATE INDEX idx_country_name_prefix
        ON entities(country, name_prefix)
    """)

    cursor.execute("""
        CREATE INDEX idx_country_address_prefix
        ON entities(country, address_prefix)
    """)

    cursor.execute("""
        CREATE INDEX idx_country_block
        ON entities(country, block_key)
    """)

    connection.commit()

    return connection


def process_file(connection, file_path, source_name):

    print()
    print("=" * 70)
    print("PROCESSING:", file_path)
    print("=" * 70)

    cursor = connection.cursor()

    total_rows = 0

    for chunk in tqdm(
        pd.read_csv(
            file_path,
            sep="\t",
            dtype=str,
            keep_default_na=False,
            chunksize=CHUNK_SIZE
        ),
        desc=source_name
    ):

        rows = []

        for row in chunk.itertuples(index=False):

            entity_id = row.entity_id
            business_name = row.business_name
            business_address = row.business_address
            country = row.country

            rows.append(
                (
                    entity_id,
                    business_name,
                    business_address,
                    country,
                    source_name,
                    name_key(business_name),
                    address_key(business_address),
                    name_prefix(business_name),
                    address_prefix(business_address),
                    make_block_key(business_name)
                )
            )

        cursor.executemany(
            """
            INSERT INTO entities (
                entity_id,
                business_name,
                business_address,
                country,
                source,
                name_norm,
                address_norm,
                name_prefix,
                address_prefix,
                block_key
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows
        )

        connection.commit()

        total_rows += len(rows)

    print(
        f"Finished {source_name}: "
        f"{total_rows:,} rows"
    )


def main():

    connection = create_database()

    process_file(
        connection,
        TEST_SOURCE2,
        "source2"
    )

    process_file(
        connection,
        TEST_SOURCE3,
        "source3"
    )

    connection.close()

    print()
    print("=" * 70)
    print("INDEX BUILD COMPLETE")
    print("Database:")
    print(DB_PATH)
    print("=" * 70)


if __name__ == "__main__":
    main()