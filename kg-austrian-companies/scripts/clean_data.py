import csv
import json
import os

INPUT_FILE = "data/Raw_Companies_Data.csv"
OUTPUT_FILE = "data/cleaned_data.json"
REPORT_FILE = "kg/data_quality_report.json"

MIN_PERCENTAGE = 0.0
MAX_PERCENTAGE = 100.0

# Text normalization

def normalize_entity_name(name):

    name = name.strip()

    # Replace repeated spaces
    name = " ".join(name.split())

    return name

# Load and validate CSV

def clean_data():

    cleaned_relations = []
    total_rows = 0
    valid_rows = 0
    invalid_rows = 0
    duplicate_rows = 0
    invalid_records = []
    seen_relations = set()

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        required_columns = {
            "owner",
            "target",
            "percentage"
        }

        if not required_columns.issubset(
            reader.fieldnames or []
        ):
            raise ValueError(
                "CSV must contain columns: "
                "owner,target,percentage"
            )

        for row_number, row in enumerate(
            reader,
            start=2
        ):

            total_rows += 1

            try:
                owner = normalize_entity_name(
                    row["owner"]
                )

                target = normalize_entity_name(
                    row["target"]
                )

                percentage = float(
                    row["percentage"]
                )

                # Basic validation
                if not owner:
                    raise ValueError(
                        "Owner is empty."
                    )

                if not target:
                    raise ValueError(
                        "Target is empty."
                    )

                if owner == target:
                    raise ValueError(
                        "Owner and target are identical."
                    )

                if not (
                    MIN_PERCENTAGE
                    <= percentage
                    <= MAX_PERCENTAGE
                ):
                    raise ValueError(
                        "Ownership percentage must be "
                        "between 0 and 100."
                    )

                # Detect duplicates
                relation_key = (
                    owner,
                    target,
                    percentage
                )

                if relation_key in seen_relations:
                    duplicate_rows += 1
                    continue

                seen_relations.add(
                    relation_key
                )

                cleaned_relations.append({
                    "source": owner,
                    "target": target,
                    "percentage": percentage
                })

                valid_rows += 1

            except (ValueError, TypeError) as error:

                invalid_rows += 1

                invalid_records.append({
                    "row": row_number,
                    "data": row,
                    "error": str(error)
                })

    # Entity statistics

    entities = set()

    for relation in cleaned_relations:

        entities.add(
            relation["source"]
        )

        entities.add(
            relation["target"]
        )

    # Quality report

    quality_report = {
        "input_file": INPUT_FILE,
        "output_file": OUTPUT_FILE,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "duplicate_rows_removed": duplicate_rows,
        "unique_entities": len(entities),
        "unique_ownership_relations": len(
            cleaned_relations
        ),
        "validation_rules": {
            "percentage_min": MIN_PERCENTAGE,
            "percentage_max": MAX_PERCENTAGE,
            "empty_entity_names_rejected": True,
            "self_ownership_rejected": True,
            "duplicate_relations_removed": True,
            "whitespace_normalization": True
        },
        "invalid_records": invalid_records
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cleaned_relations,
            f,
            indent=2,
            ensure_ascii=False
        )

    # Write report

    os.makedirs(
        os.path.dirname(REPORT_FILE),
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            quality_report,
            f,
            indent=2,
            ensure_ascii=False
        )

    # summary

    print("Data cleaning completed.")
    print()
    print(f"Total input rows: {total_rows}")
    print(f"Valid rows: {valid_rows}")
    print(f"Invalid rows: {invalid_rows}")
    print(
        f"Duplicate rows removed: "
        f"{duplicate_rows}"
    )
    print(f"Unique entities: {len(entities)}")
    print(
        f"Unique ownership relations: "
        f"{len(cleaned_relations)}"
    )
    print()
    print(
        f"Cleaned data saved to: {OUTPUT_FILE}"
    )
    print(
        f"Data quality report saved to: "
        f"{REPORT_FILE}"
    )

if __name__ == "__main__":
    clean_data()
    