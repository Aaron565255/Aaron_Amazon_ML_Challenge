import csv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from config import (
    TEST_SOURCE1,
    CANDIDATE_PAIRS,
    MATCHING_RESULTS
)


def read_source1_ids():

    ids = set()

    with open(
        TEST_SOURCE1,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter="\t"
        )

        for row in reader:
            ids.add(row["entity_id"])

    return ids


def read_output(path):

    data = {}

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter="\t"
        )

        for row in reader:

            source1_id = row[
                "source1_entity_id"
            ]

            if "candidate_entity_ids" in row:
                values = row[
                    "candidate_entity_ids"
                ]
            else:
                values = row[
                    "matched_entity_ids"
                ]

            if values:
                ids = [
                    x.strip()
                    for x in values.split(",")
                    if x.strip()
                ]
            else:
                ids = []

            data[source1_id] = ids

    return data


def main():

    print("Reading Source 1...")

    source1_ids = read_source1_ids()

    print(
        "Source 1 entities:",
        f"{len(source1_ids):,}"
    )

    print("Reading candidate output...")

    candidates = read_output(
        CANDIDATE_PAIRS
    )

    print(
        "Candidate rows:",
        f"{len(candidates):,}"
    )

    print("Reading matching output...")

    matches = read_output(
        MATCHING_RESULTS
    )

    print(
        "Matching rows:",
        f"{len(matches):,}"
    )

    errors = []

    if set(candidates) != source1_ids:

        missing = (
            source1_ids -
            set(candidates)
        )

        extra = (
            set(candidates) -
            source1_ids
        )

        if missing:
            errors.append(
                f"Missing candidate rows: {len(missing)}"
            )

        if extra:
            errors.append(
                f"Extra candidate rows: {len(extra)}"
            )

    if set(matches) != source1_ids:

        missing = (
            source1_ids -
            set(matches)
        )

        extra = (
            set(matches) -
            source1_ids
        )

        if missing:
            errors.append(
                f"Missing matching rows: {len(missing)}"
            )

        if extra:
            errors.append(
                f"Extra matching rows: {len(extra)}"
            )

    for source1_id, candidate_ids in candidates.items():

        seen = set()

        for candidate_id in candidate_ids:

            if candidate_id in seen:

                errors.append(
                    f"Duplicate candidate: "
                    f"{source1_id} -> {candidate_id}"
                )

            seen.add(candidate_id)

            if not (
                candidate_id.startswith("S2-")
                or candidate_id.startswith("S3-")
            ):

                errors.append(
                    f"Invalid candidate ID: "
                    f"{candidate_id}"
                )

    for source1_id, match_ids in matches.items():

        candidate_set = set(
            candidates.get(
                source1_id,
                []
            )
        )

        for match_id in match_ids:

            if match_id not in candidate_set:

                errors.append(
                    f"Match not present in candidates: "
                    f"{source1_id} -> {match_id}"
                )

            if not (
                match_id.startswith("S2-")
                or match_id.startswith("S3-")
            ):

                errors.append(
                    f"Invalid match ID: "
                    f"{match_id}"
                )

    print()

    if errors:

        print("=" * 70)
        print("VALIDATION FAILED")
        print("=" * 70)

        for error in errors[:100]:
            print(error)

        print()
        print(
            "Total errors:",
            len(errors)
        )

        return

    print("=" * 70)
    print("VALIDATION PASSED")
    print("=" * 70)

    print()
    print("All Source 1 entities are present.")
    print("Candidate IDs are valid.")
    print("Matched IDs are contained in candidate IDs.")
    print("No validation errors found.")


if __name__ == "__main__":
    main()