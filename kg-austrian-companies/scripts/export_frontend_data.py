import json
import os

GRAPH_FILE = "kg/graph.json"
CONTROL_FILE = "kg/control_relations.json"
FRONTEND_ASSETS_DIR = "frontend/kg-frontend/public/assets"
FRONTEND_OUTPUT_FILE = "frontend/kg-frontend/public/assets/kg-data.json"


def main():
    os.makedirs(FRONTEND_ASSETS_DIR, exist_ok=True)

    # Read graph using UTF-8
    with open(GRAPH_FILE, "r", encoding="utf-8") as f:
        graph = json.load(f)

    # Read control relations using UTF-8
    with open(CONTROL_FILE, "r", encoding="utf-8") as f:
        controls = json.load(f)

    frontend_data = {
        "nodes": graph["nodes"],
        "edges": graph["edges"],
        "direct_control": controls["direct_control"],
        "indirect_control": controls["indirect_control"]
    }

    # Write frontend data using UTF-8
    with open(
        FRONTEND_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            frontend_data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("Frontend data exported to", FRONTEND_OUTPUT_FILE)


if __name__ == "__main__":
    main()