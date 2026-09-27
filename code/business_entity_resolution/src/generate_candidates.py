import csv
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent))

from config import (
    DB_PATH,
    TEST_SOURCE1,
    CANDIDATE_PAIRS,
    CHUNK_SIZE,
    MAX_CANDIDATES_PER_BLOCK
)

from normalize import (
    name_key,
    address_key,
    name_prefix,
    address_prefix,
    make_block_key,
    country_key
)


def get_candidates(
    cursor,
    country,
    name_norm,
    address_norm,
    name_pre,
    address_pre,
    block
):

    candidates = set()

    if country and name_norm:

        cursor.execute(
            """
            SELECT entity_id
            FROM entities
            WHERE country = ?
            AND name_norm = ?
            LIMIT ?
            """,
            (
                country,
                name_norm,
                MAX_CANDIDATES_PER_BLOCK
            )
        )

        for row in cursor.fetchall():
            candidates.add(row[0])

    if country and address_norm:

        cursor.execute(
            """
            SELECT entity_id
            FROM entities
            WHERE country = ?
            AND address_norm = ?
            LIMIT ?
            """,
            (
                country,
                address_norm,
                MAX_CANDIDATES_PER_BLOCK
            )
        )

        for row in cursor.fetchall():
            candidates.add(row[0])

    if country and name_pre:

        cursor.execute(
            """
            SELECT entity_id
            FROM entities
            WHERE country = ?
            AND name_prefix = ?
            LIMIT ?
            """,
            (
                country,
                name_pre,
                MAX_CANDIDATES_PER_BLOCK
            )
        )

        for row in cursor.fetchall():
            candidates.add(row[0])

    if country and address_pre:

        cursor.execute(
            """
            SELECT entity_id
            FROM entities
            WHERE country = ?
            AND address_prefix = ?
            LIMIT ?
            """,
            (
                country,
                address_pre,
                MAX_CANDIDATES_PER_BLOCK
            )
        )

        for row in cursor.fetchall():
            candidates.add(row[0])

    if country and block:

        cursor.execute(
            """
            SELECT entity_id
            FROM entities
            WHERE country = ?
            AND block_key = ?
            LIMIT ?
            """,
            (
                country,
                block,
                MAX_CANDIDATES_PER_BLOCK
            )
        )

        for row in cursor.fetchall():
            candidates.add(row[0])

    return candidates


def main():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    CANDIDATE_PAIRS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    total_source1 = 0
    total_candidates = 0

    with open(
        CANDIDATE_PAIRS,
        "w",
        encoding="utf-8",
        newline=""
    ) as output_file:

        writer = csv.writer(
            output_file,
            delimiter="\t"
        )

        writer.writerow(
            [
                "source1_entity_id",
                "candidate_entity_ids"
            ]
        )

        for chunk in tqdm(
            pd.read_csv(
                TEST_SOURCE1,
                sep="\t",
                dtype=str,
                keep_default_na=False,
                chunksize=CHUNK_SIZE
            ),
            desc="Generating candidates"
        ):

            for row in chunk.itertuples(index=False):

                source1_id = row.entity_id

                country = country_key(row.country)

                name_norm = name_key(
                    row.business_name
                )

                address_norm = address_key(
                    row.business_address
                )

                name_pre = name_prefix(
                    row.business_name
                )

                address_pre = address_prefix(
                    row.business_address
                )

                block = make_block_key(
                    row.business_name
                )

                candidates = get_candidates(
                    cursor,
                    country,
                    name_norm,
                    address_norm,
                    name_pre,
                    address_pre,
                    block
                )

                candidate_list = sorted(candidates)

                writer.writerow(
                    [
                        source1_id,
                        ",".join(candidate_list)
                    ]
                )

                total_source1 += 1
                total_candidates += len(candidate_list)

    connection.close()

    average = 0

    if total_source1 > 0:
        average = (
            total_candidates /
            total_source1
        )

    print()
    print("=" * 70)
    print("CANDIDATE GENERATION COMPLETE")
    print(
        "Source 1 rows:",
        f"{total_source1:,}"
    )
    print(
        "Candidate IDs:",
        f"{total_candidates:,}"
    )
    print(
        "Average candidates per Source 1:",
        f"{average:.2f}"
    )
    print(
        "Output:",
        CANDIDATE_PAIRS
    )
    print("=" * 70)


if __name__ == "__main__":
    main()