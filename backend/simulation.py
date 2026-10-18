from pathlib import Path

content = '''import time

from pcs import calculate_pcs
from qfi import calculate_qfi
from dbos import calculate_dbos
from elevator import Elevator
from mww import calculate_mww


# --------------------------------------------------
# DECISION ENGINE
# --------------------------------------------------

def make_decision(dbos, pcs, qfi):
    """Decide whether the elevator should STOP, WAIT, or SKIP."""

    # Fairness protection takes priority over DBOS.
    if qfi >= 0.80:
        return "STOP"

    # High boarding opportunity.
    if dbos >= 0.70:
        return "STOP"

    # Good opportunity and committed passenger.
    if dbos >= 0.50 and pcs >= 0.70:
        return "WAIT"

    # Otherwise, skip this request for now.
    return "SKIP"


# --------------------------------------------------
# CALCULATE REQUEST SCORE
# --------------------------------------------------

def calculate_request_score(request):
    pcs = calculate_pcs(
        distance_score=request["distance"],
        direction_score=request["direction_score"],
        speed_score=request["speed"],
        facing_score=request["facing"],
        button_pressed=request["button"],
    )

    qfi = calculate_qfi(
        skipped_count=request["skipped"]
    )

    dbos = calculate_dbos(
        pcs=pcs,
        waiting_score=request["waiting"],
        capacity_score=request["capacity"],
        qfi=qfi,
        energy_cost=request["energy"],
        door_cost=request["door"],
    )

    decision = make_decision(dbos, pcs, qfi)

    mww = calculate_mww(
        distance=request["distance"],
        walking_speed=request["walking_speed"],
        pcs=pcs,
    )

    return {
        "floor": request["floor"],
        "pcs": pcs,
        "qfi": qfi,
        "dbos": dbos,
        "decision": decision,
        "arrival_time": mww["arrival_time"],
        "mww": mww["recommendation"],
    }


# ==================================================
# SINGLE ELEVATOR SIMULATION
# ==================================================

if __name__ == "__main__":
    elevator = Elevator(current_floor=1, capacity=12)

    requests = [
        {
            "floor": 3,
            "distance": 0.95,
            "direction_score": 1.0,
            "speed": 0.90,
            "facing": 1.0,
            "button": True,
            "waiting": 0.70,
            "capacity": 0.80,
            "skipped": 1,
            "energy": 0.20,
            "door": 0.10,
            "walking_speed": 1.0,
        },
        {
            "floor": 5,
            "distance": 0.70,
            "direction_score": 0.80,
            "speed": 0.70,
            "facing": 1.0,
            "button": True,
            "waiting": 0.90,
            "capacity": 0.80,
            "skipped": 3,
            "energy": 0.30,
            "door": 0.15,
            "walking_speed": 0.8,
        },
        {
            "floor": 7,
            "distance": 0.40,
            "direction_score": 0.40,
            "speed": 0.30,
            "facing": 0.0,
            "button": True,
            "waiting": 0.60,
            "capacity": 0.50,
            "skipped": 4,
            "energy": 0.40,
            "door": 0.20,
            "walking_speed": 0.4,
        },
    ]

    time_step = 0
    max_steps = 100  # Safety guard to prevent an endless simulation.

    while requests and time_step < max_steps:
        time_step += 1

        print("\\n" + "=" * 70)
        print(f"                    TIME STEP {time_step}")
        print("=" * 70)
        print(f"Elevator currently at Floor {elevator.current_floor}")

        print("\\nPending Requests:")
        for request in requests:
            print(
                f"  Floor {request['floor']} | "
                f"Skipped: {request['skipped']}"
            )

        # Calculate the latest scores for every pending request.
        results = [
            calculate_request_score(request)
            for request in requests
        ]

        print()
        print(
            f"{'Floor':<10}{'PCS':<10}{'QFI':<10}"
            f"{'DBOS':<10}{'Decision':<10}{'MWW':<15}"
        )
        print("-" * 70)

        for result in results:
            print(
                f"{result['floor']:<10}"
                f"{result['pcs']:<10}"
                f"{result['qfi']:<10}"
                f"{result['dbos']:<10}"
                f"{result['decision']:<10}"
                f"{result['mww']:<15}"
            )

        # IMPORTANT: request selection must remain inside the while loop.
        # Fairness-triggered requests take priority over ordinary DBOS.
        fairness_requests = [
            result for result in results
            if result["qfi"] >= 0.80
        ]

        if fairness_requests:
            best = max(
                fairness_requests,
                key=lambda result: (result["qfi"], result["dbos"]),
            )
            print("\\nFAIRNESS PRIORITY: selecting a request with QFI >= 0.80")
        else:
            best = max(results, key=lambda result: result["dbos"])

        print(f"AI Selected Floor: {best['floor']}")
        print(f"DBOS: {best['dbos']}")
        print(f"Action: {best['decision']}")

        # Locate the original request for the selected floor.
        selected_request = next(
            request for request in requests
            if request["floor"] == best["floor"]
        )

        if best["decision"] in ("STOP", "WAIT"):
            print("\\nAI COMMAND -> ELEVATOR")
            elevator.move_to(best["floor"])

            if best["decision"] == "WAIT":
                wait_time = max(0.0, min(float(best["arrival_time"]), 1.0))
                print(
                    f"MWW ACTIVE -> Waiting {wait_time:.2f} seconds "
                    "for passenger..."
                )
                time.sleep(wait_time)
                print("Passenger arrived -> Boarding opportunity confirmed.")

            print("\\nPassenger boarding...")
            boarded = elevator.board_passengers(1)

            if boarded == 1:
                print(f"Floor {best['floor']} request SERVED.")
                # Remove only the request that was actually served.
                requests.remove(selected_request)
            else:
                # Avoid endlessly retrying a request if boarding fails.
                print("Boarding failed; removing this request to avoid a loop.")
                requests.remove(selected_request)

        else:
            print(f"Floor {best['floor']} skipped.")
            selected_request["skipped"] += 1
            print(
                f"Updated skipped count for Floor {best['floor']}: "
                f"{selected_request['skipped']}"
            )

    print("\\n" + "=" * 70)
    if requests:
        print("SIMULATION STOPPED: maximum time steps reached.")
        print("Unserved floors:", [request["floor"] for request in requests])
    else:
        print("             SIMULATION COMPLETED")
    print("=" * 70)
    print(f"Elevator final position: Floor {elevator.current_floor}")
    print(f"Final occupancy: {elevator.passengers}/{elevator.capacity}")
'''
path = Path("/mnt/data/simulation_updated.py")
path.write_text(content, encoding="utf-8")
print(f"Created updated simulation file: {path}")
