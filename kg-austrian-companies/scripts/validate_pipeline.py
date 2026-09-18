import json
import os

CLEANED_DATA_FILE="data/cleaned_data.json"
GRAPH_FILE="kg/graph.json"
GRAPH_METADATA_FILE="kg/graph_metadata.json"
CONTROL_FILE="kg/control_relations.json"
EMBEDDINGS_FILE="kg/embeddings.json"

# Utility

def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Required file does not exist: {path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():

    print("Validating Knowledge Graph pipeline...\n")

    cleaned_data = load_json(CLEANED_DATA_FILE)
    graph = load_json(GRAPH_FILE)
    metadata = load_json(GRAPH_METADATA_FILE)
    controls = load_json(CONTROL_FILE)
    embeddings = load_json(EMBEDDINGS_FILE)

    # Extract graph data

    nodes = graph["nodes"]
    edges = graph["edges"]

    node_ids = {
        node["id"]
        for node in nodes
    }

    # every cleaned relation exists in KG

    graph_edges = {
        (
            edge["from"],
            edge["to"],
            edge["percentage"]
        )
        for edge in edges
    }

    for relation in cleaned_data:

        relation_key = (
            relation["source"],
            relation["target"],
            relation["percentage"]
        )

        assert relation_key in graph_edges, (
            "Cleaned relation missing from graph: "
            f"{relation_key}"
        )

    print("PASS: all cleaned relations exist in graph")

    # every edge references existing nodes

    for edge in edges:
        assert edge["from"] in node_ids, (f"Missing source node: {edge['from']}")
        assert edge["to"] in node_ids, (f"Missing target node: {edge['to']}")

    print("PASS: all graph edges reference valid nodes")

    # graph metadata is consistent

    graph_statistics = metadata["statistics"]
    assert graph_statistics["nodes"] == len(nodes)
    assert graph_statistics["edges"] == len(edges)
    assert graph_statistics["input_relations"] == len(cleaned_data)

    print("PASS: graph metadata is consistent")

    # control relations reference valid nodes

    all_control_relations = (
        controls["direct_control"]
        + controls["indirect_control"])

    for relation in all_control_relations:
        assert relation["controller"] in node_ids
        assert relation["controlled"] in node_ids
        assert relation["controller"] != ""
        assert relation["controlled"] != ""

    print("PASS: all control relations reference valid nodes")

    # embedding coverage

    embedded_entities = set(embeddings["entities"].keys())
    assert embedded_entities == node_ids, (
        "Embedding entities do not match KG nodes")
    
    print("PASS: every KG entity has an embedding")

    # embedding dimensions

    embedding_dimension = embeddings["embedding_dimension"]
    for entity, vector in embeddings["entities"].items():

        assert len(vector) == embedding_dimension, (
            f"Incorrect embedding dimension for {entity}"
        )

    print(
        "PASS: all entity embeddings have "
        f"{embedding_dimension} dimensions"
    )

    print()
    print("=" * 50)
    print("Pipeline Validation Summary")
    print("=" * 50)

    print(f"Entities:              {len(nodes)}")
    print(f"Ownership relations:   {len(edges)}")

    print(
        "Direct control:        "
        f"{len(controls['direct_control'])}"
    )

    print(
        "Indirect control:      "
        f"{len(controls['indirect_control'])}")
    
    print(f"Embedding dimension:   {embedding_dimension}")
    print()
    print("All pipeline validation tests passed.")

if __name__ == "__main__":
    main()