import json
import random
import torch
import torch.nn as nn
import torch.optim as optim

# Configuration
INPUT_FILE = "../kg/graph.json"
EMBEDDING_DIM = 32
EPOCHS = 500
LEARNING_RATE = 0.01
MARGIN = 1.0
SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)

def load_graph():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# TransE model

class TransE(nn.Module):
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

# Train one model

def train_model(
    triples,
    entity_to_id,
    relation_to_id
):
    model = TransE(
        num_entities=len(entity_to_id),
        num_relations=len(relation_to_id),
        embedding_dim=EMBEDDING_DIM
    )

    optimizer = optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    loss_function = nn.MarginRankingLoss(
        margin=MARGIN
    )

    entity_names = list(entity_to_id.keys())

    for _ in range(EPOCHS):

        shuffled = triples.copy()
        random.shuffle(shuffled)

        for head, relation, tail in shuffled:

            positive_head = torch.tensor(
                [entity_to_id[head]],
                dtype=torch.long
            )

            positive_relation = torch.tensor(
                [relation_to_id[relation]],
                dtype=torch.long
            )

            positive_tail = torch.tensor(
                [entity_to_id[tail]],
                dtype=torch.long
            )

            # Corrupt either head or tail
            if random.random() < 0.5:

                negative_head_name = random.choice(
                    entity_names
                )

                while negative_head_name == head:
                    negative_head_name = random.choice(
                        entity_names
                    )

                negative_head = torch.tensor(
                    [entity_to_id[negative_head_name]],
                    dtype=torch.long
                )

                negative_tail = positive_tail

            else:

                negative_tail_name = random.choice(
                    entity_names
                )

                while negative_tail_name == tail:
                    negative_tail_name = random.choice(
                        entity_names
                    )

                negative_tail = torch.tensor(
                    [entity_to_id[negative_tail_name]],
                    dtype=torch.long
                )

                negative_head = positive_head

            positive_score = model.score(
                positive_head,
                positive_relation,
                positive_tail
            )

            negative_score = model.score(
                negative_head,
                positive_relation,
                negative_tail
            )

            target = torch.tensor([-1.0])

            loss = loss_function(
                positive_score,
                negative_score,
                target
            )

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    return model

# Rank a test triple

def calculate_tail_rank(
    model,
    test_triple,
    all_true_triples,
    entity_to_id,
    relation_to_id
):
    head, relation, true_tail = test_triple

    head_id = entity_to_id[head]
    relation_id = relation_to_id[relation]

    scores = []

    for candidate_tail in entity_to_id:

        # Filter out known true triples except the test triple
        candidate_triple = (
            head,
            relation,
            candidate_tail
        )

        if (
            candidate_triple in all_true_triples
            and candidate_triple != test_triple
        ):
            continue

        score = model.score(
            torch.tensor([head_id]),
            torch.tensor([relation_id]),
            torch.tensor([
                entity_to_id[candidate_tail]
            ])
        )

        scores.append(
            (
                score.item(),
                candidate_tail
            )
        )

    scores.sort(key=lambda x: x[0])

    for rank, (_, candidate) in enumerate(
        scores,
        start=1
    ):
        if candidate == true_tail:
            return rank

    return len(scores)

def main():

    graph = load_graph()

    triples = [
        (
            edge["from"],
            edge["type"],
            edge["to"]
        )
        for edge in graph["edges"]
    ]

    all_true_triples = set(triples)

    entities = set()

    for head, _, tail in triples:
        entities.add(head)
        entities.add(tail)

    entity_names = sorted(entities)

    relations = sorted(
        set(
            relation
            for _, relation, _ in triples
        )
    )

    entity_to_id = {
        entity: index
        for index, entity in enumerate(entity_names)
    }

    relation_to_id = {
        relation: index
        for index, relation in enumerate(relations)
    }

    reciprocal_ranks = []
    hits_at_1 = 0
    hits_at_3 = 0
    hits_at_10 = 0

    print("Starting leave-one-out evaluation...\n")

    for index, test_triple in enumerate(triples):

        train_triples = [
            triple
            for i, triple in enumerate(triples)
            if i != index
        ]

        model = train_model(
            train_triples,
            entity_to_id,
            relation_to_id
        )

        rank = calculate_tail_rank(
            model,
            test_triple,
            all_true_triples,
            entity_to_id,
            relation_to_id
        )

        reciprocal_ranks.append(
            1.0 / rank
        )

        if rank <= 1:
            hits_at_1 += 1

        if rank <= 3:
            hits_at_3 += 1

        if rank <= 10:
            hits_at_10 += 1

        print(
            f"Test triple {index + 1}/{len(triples)}: "
            f"{test_triple}"
        )

        print(
            f"Rank: {rank}\n"
        )

    total = len(triples)

    mrr = sum(reciprocal_ranks) / total
    hits1 = hits_at_1 / total
    hits3 = hits_at_3 / total
    hits10 = hits_at_10 / total

    print("=" * 50)
    print("TransE Link Prediction Results")
    print("=" * 50)

    print(f"MRR:      {mrr:.4f}")
    print(f"Hits@1:   {hits1:.4f}")
    print(f"Hits@3:   {hits3:.4f}")
    print(f"Hits@10:  {hits10:.4f}")

if __name__ == "__main__":
    main()