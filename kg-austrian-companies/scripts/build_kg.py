import json

INPUT_FILE = "data/cleaned_data.json"
OUTPUT_FILE = "kg/graph.json"

def build_kg():
    with open(INPUT_FILE, "r") as f:
        relations = json.load(f)

    nodes = {}
    edges = []

    for r in relations:
        source = r["source"]
        target = r["target"]
        percentage = r["percentage"]

        # Add nodes
        if source not in nodes:
            nodes[source] = {"id": source, "label": source, "type": "entity"}
        if target not in nodes:
            nodes[target] = {"id": target, "label": target, "type": "company"}

        # Add edge
        edges.append({
            "from": source,
            "to": target,
            "label": f"{percentage}%",
            "type": "OWNS",
            "percentage": percentage
        })

    graph = {
        "nodes": list(nodes.values()),
        "edges": edges
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(graph, f, indent=2)

    print("KG saved to", OUTPUT_FILE)


if __name__ == "__main__":
    build_kg()