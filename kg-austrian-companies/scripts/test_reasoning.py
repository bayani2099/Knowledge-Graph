from reason_control import (
    infer_direct_control,
    infer_indirect_control,
    find_controllers,
)

def assert_relation(
    relations,
    controller,
    controlled,
    relation_type
):
    for relation in relations:
        if (
            relation["controller"] == controller
            and relation["controlled"] == controlled
            and relation["type"] == relation_type
        ):
            return True

    return False

def main():
    # controlled test graph.
    # A controls B
    # B controls C
    # C controls D

    # Therefore:
    # A directly controls B
    # A indirectly controls C
    # A indirectly controls D

    test_relations = [
        {
            "source": "A",
            "target": "B",
            "percentage": 60.0
        },
        {
            "source": "B",
            "target": "C",
            "percentage": 70.0
        },
        {
            "source": "C",
            "target": "D",
            "percentage": 80.0
        },
        {
            "source": "E",
            "target": "F",
            "percentage": 40.0
        }
    ]

    # Test direct control

    direct_controls = infer_direct_control(
        test_relations
    )

    assert assert_relation(
        direct_controls,
        "A",
        "B",
        "DIRECT_CONTROL"
    )

    assert assert_relation(
        direct_controls,
        "B",
        "C",
        "DIRECT_CONTROL"
    )

    assert assert_relation(
        direct_controls,
        "C",
        "D",
        "DIRECT_CONTROL"
    )

    # 40% should NOT create direct control.
    assert not assert_relation(
        direct_controls,
        "E",
        "F",
        "DIRECT_CONTROL"
    )
    print("PASS: direct control tests")

    # Test indirect control

    indirect_controls = infer_indirect_control(
        direct_controls,
        max_depth=10
    )

    assert assert_relation(
        indirect_controls,
        "A",
        "C",
        "INDIRECT_CONTROL"
    )

    assert assert_relation(
        indirect_controls,
        "A",
        "D",
        "INDIRECT_CONTROL"
    )

    assert assert_relation(
        indirect_controls,
        "B",
        "D",
        "INDIRECT_CONTROL"
    )

    print("PASS: indirect control tests")

    # Test reasoning path

    a_to_d = next(
        relation
        for relation in indirect_controls
        if (
            relation["controller"] == "A"
            and relation["controlled"] == "D"
        )
    )

    expected_path = ["A","B","C","D"]

    assert a_to_d["path"] == expected_path

    assert a_to_d["depth"] == 3

    print("PASS: path and depth tests")

    # Test controller query

    controllers = find_controllers(
        "D",
        direct_controls,
        indirect_controls
    )

    controller_names = {
        result["controller"]
        for result in controllers
    }

    assert "C" in controller_names
    assert "B" in controller_names
    assert "A" in controller_names

    print("PASS: controller query tests")

    # Test cycle protection

    cycle_relations = [
        {
            "source": "A",
            "target": "B",
            "percentage": 60.0
        },
        {
            "source": "B",
            "target": "C",
            "percentage": 60.0
        },
        {
            "source": "C",
            "target": "A",
            "percentage": 60.0
        }
    ]

    cycle_direct = infer_direct_control(
        cycle_relations
    )

    cycle_indirect = infer_indirect_control(
        cycle_direct,
        max_depth=10
    )

    # The algorithm must terminate and must not produce a path that loops forever.

    for relation in cycle_indirect:
        assert len(relation["path"]) == len(
            set(relation["path"])
        )

    print("PASS: cycle protection test")

    # Test maximum reasoning depth

    depth_relations = [
        {
            "source": "A",
            "target": "B",
            "percentage": 60.0
        },
        {
            "source": "B",
            "target": "C",
            "percentage": 60.0
        },
        {
            "source": "C",
            "target": "D",
            "percentage": 60.0
        },
        {
            "source": "D",
            "target": "E",
            "percentage": 60.0
        },
        {
            "source": "E",
            "target": "F",
            "percentage": 60.0
        }
    ]

    depth_direct = infer_direct_control(
        depth_relations
    )

    depth_indirect = infer_indirect_control(
        depth_direct,
        max_depth=2
    )

    # No inferred path may exceed the
    # configured reasoning depth.

    for relation in depth_indirect:
        assert relation["depth"] <= 2

    print("PASS: maximum reasoning depth test")
    print()
    print("All reasoning tests passed.")

if __name__ == "__main__":
    main()