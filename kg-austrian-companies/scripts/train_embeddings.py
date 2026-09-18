import json
import os
import random
import torch
import torch.nn as nn
import torch.optim as optim

# Configuration
INPUT_FILE = "kg/graph.json"
OUTPUT_FILE = "kg/embeddings.json"
EMBEDDING_DIM = 32
EPOCHS = 1000
LEARNING_RATE = 0.01
MARGIN = 1.0
SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)

# Load graph

def load_graph():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# Convert graph into triples

def build_triples(graph):
    triples = []

    for edge in graph["edges"]:
        triples.append(
            (
                edge["from"],
                edge["type"],
                edge["to"]
            )
        )

    return triples

# TransE model

class TransE(nn.Module):
    """
    TransE learns embeddings such that:
        embedding(head) + embedding(relation)≈ embedding(tail)
    For a correct triple, the distance should be small.
    """

    def __init__(self, num_entities, num_relations, embedding_dim):
        super().__init__()

        self.entity_embeddings = nn.Embedding(
            num_entities,
            embedding_dim
        )

        self.relation_embeddings = nn.Embedding(
            num_relations,
            embedding_dim
        )

        self.reset_parameters()

    def reset_parameters(self):
        nn.init.uniform_(
            self.entity_embeddings.weight,
            -0.1,
            0.1
        )

        nn.init.uniform_(
            self.relation_embeddings.weight,
            -0.1,
            0.1
        )

    def score(self, heads, relations, tails):
        head_vectors = self.entity_embeddings(heads)
        relation_vectors = self.relation_embeddings(relations)
        tail_vectors = self.entity_embeddings(tails)

        return torch.linalg.vector_norm(
            head_vectors + relation_vectors - tail_vectors,
            ord=1,
            dim=1
        )


def generate_negative_triple(
    triple,
    entity_names,
    entity_to_id
):
    head, relation, tail = triple

    if random.random() < 0.5:
        # Replace head
        new_head = random.choice(entity_names)

        while new_head == head:
            new_head = random.choice(entity_names)

        return (
            new_head,
            relation,
            tail
        )

    # Replace tail
    new_tail = random.choice(entity_names)

    while new_tail == tail:
        new_tail = random.choice(entity_names)

    return (
        head,
        relation,
        new_tail
    )

# Main training function

def main():
    print("Loading knowledge graph...")

    graph = load_graph()
    triples = build_triples(graph)

    if not triples:
        raise ValueError("No triples were found in graph.json.")

    print(f"Number of triples: {len(triples)}")

    # Collect entities and relations
    entities = set()

    for head, relation, tail in triples:
        entities.add(head)
        entities.add(tail)

    entity_names = sorted(entities)

    relation_names = sorted(
        set(relation for _, relation, _ in triples)
    )

    entity_to_id = {
        name: index
        for index, name in enumerate(entity_names)
    }

    relation_to_id = {
        name: index
        for index, name in enumerate(relation_names)
    }

    print(f"Number of entities: {len(entity_names)}")
    print(f"Relations: {relation_names}")

    # Convert triples to IDs
    positive_triples = [
        (entity_to_id[head],relation_to_id[relation],entity_to_id[tail])
        for head, relation, tail in triples]

    # Model
    model = TransE(
        num_entities=len(entity_names),
        num_relations=len(relation_names),
        embedding_dim=EMBEDDING_DIM)

    optimizer = optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE)

    loss_function = nn.MarginRankingLoss(
        margin=MARGIN)

    # Training
    print("\nTraining TransE...\n")

    for epoch in range(1, EPOCHS + 1):

        total_loss = 0.0

        random.shuffle(positive_triples)

        for head_id, relation_id, tail_id in positive_triples:

            positive_heads = torch.tensor(
                [head_id],
                dtype=torch.long
            )

            positive_relations = torch.tensor(
                [relation_id],
                dtype=torch.long
            )

            positive_tails = torch.tensor(
                [tail_id],
                dtype=torch.long
            )

            # Convert ID triple back to names
            original_triple = (
                entity_names[head_id],
                relation_names[relation_id],
                entity_names[tail_id]
            )

            negative_triple = generate_negative_triple(
                original_triple,
                entity_names,
                entity_to_id
            )

            negative_heads = torch.tensor(
                [entity_to_id[negative_triple[0]]],
                dtype=torch.long
            )

            negative_relations = torch.tensor(
                [relation_to_id[negative_triple[1]]],
                dtype=torch.long
            )

            negative_tails = torch.tensor(
                [entity_to_id[negative_triple[2]]],
                dtype=torch.long
            )

            positive_score = model.score(
                positive_heads,
                positive_relations,
                positive_tails
            )

            negative_score = model.score(
                negative_heads,
                negative_relations,
                negative_tails
            )

            target = torch.tensor(
                [-1.0]
            )

            loss = loss_function(
                positive_score,
                negative_score,
                target
            )

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        if epoch == 1 or epoch % 100 == 0:
            print(
                f"Epoch {epoch:4d} | "
                f"Loss: {total_loss:.4f}"
            )

    # Normalize embeddings
    with torch.no_grad():
        entity_vectors = model.entity_embeddings.weight.data.clone()
        relation_vectors = model.relation_embeddings.weight.data.clone()

        entity_vectors = torch.nn.functional.normalize(
            entity_vectors,
            p=2,
            dim=1
        )

        relation_vectors = torch.nn.functional.normalize(
            relation_vectors,
            p=2,
            dim=1
        )

    # output
    output = {
        "model": "TransE",
        "embedding_dimension": EMBEDDING_DIM,
        "epochs": EPOCHS,
        "learning_rate": LEARNING_RATE,
        "margin": MARGIN,
        "seed": SEED,
        "entities": {},
        "relations": {}
    }

    for entity, entity_id in entity_to_id.items():
        output["entities"][entity] = (
            entity_vectors[entity_id]
            .tolist()
        )

    for relation, relation_id in relation_to_id.items():
        output["relations"][relation] = (
            relation_vectors[relation_id]
            .tolist()
        )

    # Create output directory if necessary
    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\nTraining complete.")
    print(f"Embeddings saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()