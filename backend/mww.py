def calculate_mww(distance, walking_speed, pcs, max_wait=5.0):
    """
    Calculate Micro-Wait Window (MWW).

    distance      : passenger distance from elevator in metres
    walking_speed : passenger walking speed in m/s
    pcs           : Passenger Commitment Score
    max_wait      : maximum allowed waiting time
    """

    if walking_speed <= 0:
        return {
            "arrival_time": None,
            "recommendation": "SKIP",
            "wait_duration": 0
        }

    arrival_time = distance / walking_speed

    # High commitment + passenger arriving soon
    if pcs >= 0.80 and arrival_time <= max_wait:

        wait_duration = round(arrival_time, 2)

        return {
            "arrival_time": round(arrival_time, 2),
            "recommendation": "WAIT",
            "wait_duration": wait_duration
        }

    return {
        "arrival_time": round(arrival_time, 2),
        "recommendation": "NO WAIT",
        "wait_duration": 0
    }


# =========================================================
# MICRO-WAIT WINDOW DEMONSTRATION
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("                 MICRO-WAIT WINDOW")
    print("=" * 65)

    # -----------------------------------------------------
    # PASSENGER SCENARIO
    # -----------------------------------------------------

    distance = 2.0
    walking_speed = 1.0
    pcs = 0.94

    result = calculate_mww(
        distance=distance,
        walking_speed=walking_speed,
        pcs=pcs
    )

    print()
    print("PASSENGER SCENARIO")
    print("-" * 65)

    print(f"Distance from Elevator : {distance} m")
    print(f"Walking Speed          : {walking_speed} m/s")
    print(f"PCS                    : {pcs}")
    print(f"Estimated Arrival      : {result['arrival_time']} sec")

    print()
    print("-" * 65)
    print("AI RECOMMENDATION")
    print("-" * 65)

    print(f"Recommendation         : {result['recommendation']}")

    if result["recommendation"] == "WAIT":
        print(f"Wait Duration          : {result['wait_duration']} sec")

    print()
    print("DECISION LOGIC")
    print("-" * 65)

    print("Passenger is approaching")
    print("        ↓")
    print("Calculate arrival time")
    print("        ↓")
    print("Check Passenger Commitment Score")
    print("        ↓")
    print("PCS is high + arrival is soon")
    print("        ↓")
    print("MICRO-WAIT WINDOW")
    print("        ↓")
    print(f"WAIT {result['wait_duration']} SECONDS")

    print()
    print("=" * 65)