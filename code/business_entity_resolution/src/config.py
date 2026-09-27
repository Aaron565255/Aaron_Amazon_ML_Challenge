from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_ROOT = PROJECT_ROOT / "Dataset" / "student_resource" / "dataset"

TRAIN_ROOT = DATASET_ROOT / "train"
TEST_ROOT = DATASET_ROOT / "test"

OUTPUT_ROOT = PROJECT_ROOT / "output"

DB_PATH = OUTPUT_ROOT / "entity_index.db"

TRAIN_SOURCE1 = TRAIN_ROOT / "train_source1.tsv"
TRAIN_SOURCE2 = TRAIN_ROOT / "train_source2.tsv"
TRAIN_SOURCE3 = TRAIN_ROOT / "train_source3.tsv"
TRAIN_GROUND_TRUTH = TRAIN_ROOT / "train_ground_truth.tsv"

TEST_SOURCE1 = TEST_ROOT / "test_source1.tsv"
TEST_SOURCE2 = TEST_ROOT / "test_source2.tsv"
TEST_SOURCE3 = TEST_ROOT / "test_source3.tsv"

MATCHING_RESULTS = OUTPUT_ROOT / "matching_results.tsv"
CANDIDATE_PAIRS = OUTPUT_ROOT / "candidate_pairs.tsv"

CHUNK_SIZE = 50000

MAX_CANDIDATES_PER_BLOCK = 50

FINAL_MATCH_THRESHOLD = 72