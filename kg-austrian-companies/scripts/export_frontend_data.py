import json
import os
import shutil

GRAPH_FILE = "kg/graph.json"
CONTROL_FILE = "kg/control_relations.json"
FRONTEND_ASSETS_DIR = "frontend/kg-frontend/public/assets"
FRONTEND_OUTPUT_FILE = "frontend/kg-frontend/public/assets/kg-data.json"

def main():
    os.makedirs(FRONTEND_ASSETS_DIR, exist_ok=True)

    with open(GRAPH_FILE, "r") as f:
        graph = json.load(f)

    with open(CONTROL_FILE, "r") as f:
        controls = json.load(f)

    frontend_data = {
        "nodes": graph["nodes"],
        "edges": graph["edges"],
        "direct_control": controls["direct_control"],
        "indirect_control": controls["indirect_control"]
    }

    with open(FRONTEND_OUTPUT_FILE, "w") as f:
        json.dump(frontend_data, f, indent=2)

    print("Frontend data exported to", FRONTEND_OUTPUT_FILE)


if __name__ == "__main__":
    main()