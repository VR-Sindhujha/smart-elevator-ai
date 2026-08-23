def calculate_dbos(
    pcs,
    waiting_score,
    capacity_score,
    qfi,
    energy_cost,
    door_cost
):
    """
    Calculate Dynamic Boarding Opportunity Score (DBOS).

    Prototype scoring model:
    Positive factors:
        PCS
        Waiting priority
        Capacity
        Fairness

    Negative factors:
        Energy cost
        Door operation cost
    """

    dbos = (
        0.30 * pcs +
        0.20 * waiting_score +
        0.15 * capacity_score +
        0.20 * qfi -
        0.10 * energy_cost -
        0.05 * door_cost
    )

    return round(max(0, min(dbos, 1)), 2)


# =========================================================
# DBOS DEMONSTRATION
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("          DYNAMIC BOARDING OPPORTUNITY SCORE")
    print("=" * 65)

    # -----------------------------------------------------
    # FLOOR 3
    # -----------------------------------------------------

    floor3 = calculate_dbos(
        pcs=0.97,
        waiting_score=0.30,
        capacity_score=0.80,
        qfi=0.20,
        energy_cost=0.40,
        door_cost=0.30
    )

    # -----------------------------------------------------
    # FLOOR 5
    # -----------------------------------------------------

    floor5 = calculate_dbos(
        pcs=0.82,
        waiting_score=0.70,
        capacity_score=0.90,
        qfi=0.60,
        energy_cost=0.30,
        door_cost=0.20
    )

    # -----------------------------------------------------
    # FLOOR 7
    # -----------------------------------------------------

    floor7 = calculate_dbos(
        pcs=0.45,
        waiting_score=0.50,
        capacity_score=0.70,
        qfi=0.80,
        energy_cost=0.80,
        door_cost=0.60
    )

    print()
    print("PENDING FLOOR REQUESTS")
    print("-" * 65)

    print(f"Floor 3  →  DBOS = {floor3:.2f}")
    print(f"Floor 5  →  DBOS = {floor5:.2f}")
    print(f"Floor 7  →  DBOS = {floor7:.2f}")

    scores = {
        3: floor3,
        5: floor5,
        7: floor7
    }

    selected_floor = max(scores, key=scores.get)
    selected_score = scores[selected_floor]

    print()
    print("-" * 65)
    print("AI DECISION")
    print("-" * 65)

    print(f"Selected Floor : {selected_floor}")
    print(f"Highest DBOS   : {selected_score:.2f}")

    print()
    print("Decision Flow")
    print("-" * 65)

    print("Multiple floor requests")
    print("        ↓")
    print("Calculate DBOS for each request")
    print("        ↓")
    print("Compare scores")
    print("        ↓")
    print(f"Floor {selected_floor} has the highest priority")
    print("        ↓")
    print("SEND COMMAND TO ELEVATOR")

    print()
    print("=" * 65)