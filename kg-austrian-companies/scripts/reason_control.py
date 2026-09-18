import json
import os
from collections import defaultdict

INPUT_FILE = "data/cleaned_data.json"
OUTPUT_FILE = "kg/control_relations.json"

CONTROL_THRESHOLD = 50.0
MAX_REASONING_DEPTH = 10

def load_relations():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def infer_direct_control(relations):
    direct_controls = []

    for relation in relations:
        owner = relation["source"]
        target = relation["target"]
        percentage = relation["percentage"]

        if percentage >= CONTROL_THRESHOLD:
            direct_controls.append({
                "controller": owner,
                "controlled": target,
                "type": "DIRECT_CONTROL",
                "ownership_percentage": percentage,
                "path": [owner, target],
                "depth": 1,
                "reason": (
                    f"{owner} owns {percentage}% of {target}, "
                    f"which meets the {CONTROL_THRESHOLD}% control threshold."
                )
            })

    return direct_controls

def build_control_graph(direct_controls):
    control_graph = defaultdict(list)

    for relation in direct_controls:
        controller = relation["controller"]
        controlled = relation["controlled"]

        control_graph[controller].append(controlled)

    return control_graph

def infer_indirect_control(
    direct_controls,
    max_depth=MAX_REASONING_DEPTH
):
    control_graph = build_control_graph(direct_controls)

    indirect_controls = []
    discovered = set()

    for controller in control_graph:

        stack = [
            (
                controller,
                [controller]
            )
        ]

        visited_paths = set()

        while stack:
            current, path = stack.pop()

            if len(path) - 1 >= max_depth:
                continue

            for next_entity in control_graph.get(current, []):

                # Prevent cycles
                if next_entity in path:
                    continue

                new_path = path + [next_entity]

                path_key = tuple(new_path)

                if path_key in visited_paths:
                    continue

                visited_paths.add(path_key)

                # We only create an indirect relation
                # when at least one intermediate entity exists.
                if len(new_path) >= 3:

                    key = (
                        controller,
                        next_entity
                    )

                    # Do not duplicate the same controller-target pair.
                    if key not in discovered:

                        discovered.add(key)

                        indirect_controls.append({
                            "controller": controller,
                            "controlled": next_entity,
                            "type": "INDIRECT_CONTROL",
                            "path": new_path,
                            "depth": len(new_path) - 1,
                            "intermediate_entities": new_path[1:-1],
                            "reasoning_rule": (
                                "Transitive control: if A controls B "
                                "and B controls C, then A indirectly "
                                "controls C."
                            ),
                            "reason": (
                                f"{controller} indirectly controls "
                                f"{next_entity} through "
                                f"{' -> '.join(new_path[1:-1])}."
                            )
                        })

                stack.append(
                    (
                        next_entity,
                        new_path
                    )
                )

    return indirect_controls

def find_controllers(
    company,
    direct_controls,
    indirect_controls
):
    controllers = []

    for relation in direct_controls:
        if relation["controlled"] == company:
            controllers.append({
                "controller": relation["controller"],
                "type": "DIRECT_CONTROL",
                "path": relation["path"]
            })

    for relation in indirect_controls:
        if relation["controlled"] == company:
            controllers.append({
                "controller": relation["controller"],
                "type": "INDIRECT_CONTROL",
                "path": relation["path"]
            })

    return controllers

def calculate_statistics(
    relations,
    direct_controls,
    indirect_controls
):
    companies = set()

    for relation in relations:
        companies.add(relation["source"])
        companies.add(relation["target"])

    depth_distribution = defaultdict(int)

    for relation in indirect_controls:
        depth_distribution[
            relation["depth"]
        ] += 1

    return {
        "entities": len(companies),
        "ownership_relations": len(relations),
        "direct_control_relations": len(direct_controls),
        "indirect_control_relations": len(indirect_controls),
        "control_threshold": CONTROL_THRESHOLD,
        "maximum_reasoning_depth": MAX_REASONING_DEPTH,
        "indirect_control_depth_distribution": dict(
            depth_distribution
        )
    }

def main():

    print("Loading ownership data...")
    relations = load_relations()
    print(f"Ownership relations loaded: {len(relations)}")
    print(f"Control threshold: {CONTROL_THRESHOLD}%")
    print(f"Maximum reasoning depth: {MAX_REASONING_DEPTH}")

    direct_controls = infer_direct_control(relations)

    print(
        f"Direct control relations: "
        f"{len(direct_controls)}")

    indirect_controls = infer_indirect_control(
        direct_controls,
        MAX_REASONING_DEPTH)

    print(
        f"Indirect control relations: "
        f"{len(indirect_controls)}")

    # Statistics
    statistics = calculate_statistics(
        relations,
        direct_controls,
        indirect_controls
    )

    # Example query
    # Change this company when testing.
    query_company = "bank99 AG"

    controllers = find_controllers(
        query_company,
        direct_controls,
        indirect_controls
    )

    print(
        f"\nControllers of {query_company}:"
    )

    for controller in controllers:
        print(
            f"  {controller['controller']} "
            f"({controller['type']})"
        )

    # Final output
    output = {
        "configuration": {
            "control_threshold": CONTROL_THRESHOLD,
            "maximum_reasoning_depth": MAX_REASONING_DEPTH
        },
        "statistics": statistics,
        "direct_control": direct_controls,
        "indirect_control": indirect_controls
    }

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

    print(
        f"\nControl relations saved to: {OUTPUT_FILE}"
    )

if __name__ == "__main__":
    main()