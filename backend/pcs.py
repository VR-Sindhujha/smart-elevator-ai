def calculate_pcs(
    distance_score,
    direction_score,
    speed_score,
    facing_score,
    button_pressed
):
    """
    Calculate Passenger Commitment Score (PCS).

    Each input should be between 0 and 1.
    """

    button_score = 1.0 if button_pressed else 0.0

    pcs = (
        0.30 * distance_score +
        0.20 * direction_score +
        0.15 * speed_score +
        0.15 * facing_score +
        0.20 * button_score
    )

    return round(pcs, 2)


# ---------------------------------------------------------
# PCS DEMONSTRATION
# ---------------------------------------------------------

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("          PASSENGER COMMITMENT SCORE (PCS)")
    print("=" * 60)

    # Simulated passenger approaching the elevator
    distance_score = 0.95
    direction_score = 1.00
    speed_score = 0.90
    facing_score = 1.00
    button_pressed = True

    pcs = calculate_pcs(
        distance_score,
        direction_score,
        speed_score,
        facing_score,
        button_pressed
    )

    print()
    print("Passenger Scenario")
    print("-" * 60)

    print(f"Distance Score    : {distance_score}")
    print(f"Direction Score   : {direction_score}")
    print(f"Speed Score       : {speed_score}")
    print(f"Facing Elevator   : {facing_score}")
    print(f"Button Pressed    : {button_pressed}")

    print()
    print(f"Passenger Commitment Score : {pcs}")

    if pcs >= 0.80:
        commitment = "HIGH"
    elif pcs >= 0.50:
        commitment = "MEDIUM"
    else:
        commitment = "LOW"

    print(f"Commitment Level            : {commitment}")

    print()
    print("=" * 60)