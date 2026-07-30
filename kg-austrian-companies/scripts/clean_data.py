import csv
import json

INPUT_FILE = "data/Raw_Companies_Data.csv"
OUTPUT_FILE = "data/cleaned_data.json"

def clean_data():
    relations = []

    with open(INPUT_FILE, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            relations.append({
                "source": row["owner"].strip(),
                "target": row["target"].strip(),
                "percentage": float(row["percentage"])
            })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(relations, f, indent=2)

    print("Cleaned data saved to", OUTPUT_FILE)


if __name__ == "__main__":
    clean_data()