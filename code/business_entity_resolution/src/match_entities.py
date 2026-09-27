import csv
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent))

from config import (
    DB_PATH,
    TEST_SOURCE1,
    CANDIDATE_PAIRS,
    MATCHING_RESULTS,
    CHUNK_SIZE,
    FINAL_MATCH_THRESHOLD
)

from normalize import (
    name_key,
    address_key,
    country_key
)


def calculate_score(
    source1_name,
    source1_address,
    source1_country,
    candidate_name,
    candidate_address,
    candidate_country
):

    name_score = fuzz.token_set_ratio(
        source1_name,
        candidate_name
    )

    address_score = fuzz.token_set_ratio(
        source1_address,
        candidate_address
    )

    ratio_name = fuzz.ratio(
        source1_name,
        candidate_name
    )

    ratio_address = fuzz.ratio(
        source1_address,
        candidate_address
    )

    score = (
        name_score * 0.55
        + address_score * 0.30
        + ratio_name * 0.10
        + ratio_address * 0.05
    )

    if (
        source1_name
        and source1_name == candidate_name
    ):
        score += 15

    if (
        source1_address
        and source1_address == candidate_address
    ):
        score += 10

    if (
        source1_country
        and candidate_country
        and source1_country == candidate_country
    ):
        score += 5

    return min(score, 100)


def main():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    candidate_data = {}

    print("Reading candidate pairs...")

    with open(
        CANDIDATE_PAIRS,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter="\t"
        )

        for row in reader:

            candidate_data[
                row["source1_entity_id"]
            ] = row["candidate_entity_ids"]

    MATCHING_RESULTS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    total_rows = 0
    total_matches = 0

    with open(
        MATCHING_RESULTS,
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
                "matched_entity_ids"
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
            desc="Matching entities"
        ):

            for row in chunk.itertuples(index=False):

                source1_id = row.entity_id

                source1_name = name_key(
                    row.business_name
                )

                source1_address = address_key(
                    row.business_address
                )

                source1_country = country_key(
                    row.country
                )

                candidate_string = candidate_data.get(
                    source1_id,
                    ""
                )

                candidate_ids = []

                if candidate_string:
                    candidate_ids = candidate_string.split(",")

                scored_candidates = []

                for candidate_id in candidate_ids:

                    cursor.execute(
                        """
                        SELECT
                            business_name,
                            business_address,
                            country
                        FROM entities
                        WHERE entity_id = ?
                        """,
                        (candidate_id,)
                    )

                    result = cursor.fetchone()

                    if result is None:
                        continue

                    candidate_name = name_key(
                        result[0]
                    )

                    candidate_address = address_key(
                        result[1]
                    )

                    candidate_country = country_key(
                        result[2]
                    )

                    score = calculate_score(
                        source1_name,
                        source1_address,
                        source1_country,
                        candidate_name,
                        candidate_address,
                        candidate_country
                    )

                    scored_candidates.append(
                        (
                            score,
                            candidate_id,
                            source1_name,
                            candidate_name,
                            source1_address,
                            candidate_address
                        )
                    )

                matched = []

                for item in sorted(
                    scored_candidates,
                    reverse=True
                ):

                    score = item[0]

                    candidate_id = item[1]

                    name_a = item[2]
                    name_b = item[3]

                    address_a = item[4]
                    address_b = item[5]

                    strong_name = (
                        name_a
                        and name_b
                        and fuzz.token_set_ratio(
                            name_a,
                            name_b
                        ) >= 85
                    )

                    strong_address = (
                        address_a
                        and address_b
                        and fuzz.token_set_ratio(
                            address_a,
                            address_b
                        ) >= 80
                    )

                    if (
                        score >= FINAL_MATCH_THRESHOLD
                        or strong_name
                        or (
                            strong_address
                            and score >= 65
                        )
                    ):
                        matched.append(candidate_id)

                matched = list(
                    dict.fromkeys(matched)
                )

                writer.writerow(
                    [
                        source1_id,
                        ",".join(matched)
                    ]
                )

                total_rows += 1
                total_matches += len(matched)

    connection.close()

    average = 0

    if total_rows:
        average = (
            total_matches /
            total_rows
        )

    print()
    print("=" * 70)
    print("MATCHING COMPLETE")
    print(
        "Source 1 rows:",
        f"{total_rows:,}"
    )
    print(
        "Matched IDs:",
        f"{total_matches:,}"
    )
    print(
        "Average matches per Source 1:",
        f"{average:.2f}"
    )
    print(
        "Output:",
        MATCHING_RESULTS
    )
    print("=" * 70)


if __name__ == "__main__":
    main()