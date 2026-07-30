import json

INPUT_FILE = "data/cleaned_data.json"
OUTPUT_FILE = "kg/control_relations.json"

CONTROL_THRESHOLD = 50.0


def load_relations():
    with open(INPUT_FILE, "r") as f:
        return json.load(f)


def infer_direct_control(relations):
    direct_controls = []

    for r in relations:
        if r["percentage"] >= CONTROL_THRESHOLD:
            direct_controls.append({
                "controller": r["source"],
                "controlled": r["target"],
                "type": "DIRECT_CONTROL",
                "path": [r["source"], r["target"]],
                "reason": f"{r['source']} owns {r['percentage']}% of {r['target']}"
            })

    return direct_controls


def infer_indirect_control(direct_controls):
    indirect_controls = []

    control_map = {}

    for relation in direct_controls:
        controller = relation["controller"]
        controlled = relation["controlled"]

        if controller not in control_map:
            control_map[controller] = []

        control_map[controller].append(controlled)

    for controller in control_map:
        visited = set()
        stack = [(controller, [controller])]

        while stack:
            current, path = stack.pop()

            for next_company in control_map.get(current, []):
                if next_company not in visited:
                    visited.add(next_company)
                    new_path = path + [next_company]

                    if len(new_path) > 2:
                        indirect_controls.append({
                            "controller": controller,
                            "controlled": next_company,
                            "type": "INDIRECT_CONTROL",
                            "path": new_path,
                            "reason": f"{controller} controls {next_company} through {' -> '.join(new_path[1:-1])}"
                        })

                    stack.append((next_company, new_path))

    return indirect_controls


def main():
    relations = load_relations()

    direct_controls = infer_direct_control(relations)
    indirect_controls = infer_indirect_control(direct_controls)

    output = {
        "direct_control": direct_controls,
        "indirect_control": indirect_controls
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print("Control relations saved to", OUTPUT_FILE)


if __name__ == "__main__":
    main()