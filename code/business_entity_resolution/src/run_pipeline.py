import subprocess
import sys
from pathlib import Path


SRC = Path(__file__).resolve().parent


def run_script(name):

    print()
    print("=" * 70)
    print("RUNNING:", name)
    print("=" * 70)

    result = subprocess.run(
        [
            sys.executable,
            str(SRC / name)
        ]
    )

    if result.returncode != 0:

        print()
        print("ERROR WHILE RUNNING:", name)

        sys.exit(result.returncode)


def main():

    run_script("build_index.py")

    run_script("generate_candidates.py")

    run_script("match_entities.py")

    run_script("validate_outputs.py")

    print()
    print("=" * 70)
    print("FULL PIPELINE FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()