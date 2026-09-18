import json
import os
from collections import Counter

INPUT_FILE = "data/cleaned_data.json"
OUTPUT_FILE = "kg/graph.json"
METADATA_FILE = "kg/graph_metadata.json"

def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def determine_entity_type(entity_name):
    """
    Simple entity classification for this prototype.

    Companies are identified by common Austrian legal-form
    suffixes. Other entities are classified as entities.
    """

    company_suffixes = (
        "GmbH",
        "AG",
        "m.b.H.",
        "SE",
        "KG"
    )

    if entity_name.endswith(company_suffixes):
        return "company"

    return "entity"

def build_kg(relations):
    nodes = {}
    edges = []

    for relation in relations:

        source = relation["source"]
        target = relation["target"]
        percentage = relation["percentage"]

        if source not in nodes:

            nodes[source] = {
                "id": source,
                "label": source,
                "type": determine_entity_type(source)
            }

        if target not in nodes:

            nodes[target] = {
                "id": target,
                "label": target,
                "type": determine_entity_type(target)
            }

        edges.append({
            "from": source,
            "to": target,
            "label": f"{percentage}%",
            "type": "OWNS",
            "percentage": percentage
        })

    return list(nodes.values()), edges

def create_metadata(nodes, edges, relations):

    node_types = Counter(
        node["type"]
        for node in nodes
    )

    relationship_types = Counter(
        edge["type"]
        for edge in edges
    )

    metadata = {
        "source": INPUT_FILE,
        "graph_file": OUTPUT_FILE,

        "statistics": {
            "nodes": len(nodes),
            "edges": len(edges),
            "input_relations": len(relations),
            "node_types": dict(node_types),
            "relationship_types": dict(
                relationship_types
            )
        },

        "schema": {
            "node_attributes": [
                "id",
                "label",
                "type"
            ],
            "edge_attributes": [
                "from",
                "to",
                "label",
                "type",
                "percentage"
            ]
        }
    }

    return metadata

def main():

    print("Loading cleaned ownership data...")
    relations = load_data()

    print(
        f"Ownership relations loaded: "
        f"{len(relations)}")

    nodes, edges = build_kg(relations)
    metadata = create_metadata(nodes,edges,relations)
    graph = {"nodes": nodes,"edges": edges}

    os.makedirs(os.path.dirname(OUTPUT_FILE),exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            graph,
            f,
            indent=2,
            ensure_ascii=False)

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Knowledge graph created.")
    print()
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")
    print()
    print("Node types:")

    for node_type, count in metadata["statistics"][
        "node_types"
    ].items():

        print(f"  {node_type}: {count}")

    print()
    print("Relationship types:")

    for relation_type, count in metadata["statistics"][
        "relationship_types"
    ].items():

        print(
            f"  {relation_type}: {count}"
        )

    print()
    print(f"Graph saved to: {OUTPUT_FILE}")
    print(f"Metadata saved to: {METADATA_FILE}")

if __name__ == "__main__":
    main()
    