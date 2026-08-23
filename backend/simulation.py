from pcs import calculate_pcs
from qfi import calculate_qfi
from dbos import calculate_dbos
from elevator import Elevator
from mww import calculate_mww

def make_decision(dbos, pcs, qfi):
    """
    Decide whether the elevator should STOP, WAIT, or SKIP.

    Fairness override prevents a floor from being
    skipped indefinitely.
    """

    # Fairness protection:
    # If a floor has been skipped repeatedly,
    # it must eventually be served.
    if qfi >= 0.80:
        return "STOP"

    if dbos >= 0.70:
        return "STOP"

    elif dbos >= 0.50 and pcs >= 0.70:
        return "WAIT"

    else:
        return "SKIP"


def calculate_request_score(request):

    pcs = calculate_pcs(
        distance_score=request["distance"],
        direction_score=request["direction_score"],
        speed_score=request["speed"],
        facing_score=request["facing"],
        button_pressed=request["button"]
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
        door_cost=request["door"]
    )

    decision = make_decision(
    dbos,
    pcs,
    qfi
    )
    mww = calculate_mww(
        distance=request["distance"],
        walking_speed=request["walking_speed"],
        direction=request["direction"],
        pcs=pcs
    )

    return {
        "floor": request["floor"],
        "pcs": pcs,
        "qfi": qfi,
        "dbos": dbos,
        "decision": decision,
        "arrival_time": mww["arrival_time"],
        "mww": mww["recommendation"]
    }


# --------------------------------------------------
# CREATE ELEVATOR
# --------------------------------------------------

elevator = Elevator(
    current_floor=1,
    capacity=12
)


# --------------------------------------------------
# INITIAL REQUESTS
# --------------------------------------------------

requests = [

    {
        "floor": 3,

        # PCS features
        "distance": 0.95,
        "direction_score": 1.0,
        "speed": 0.90,
        "facing": 1.0,
        "button": True,

        # DBOS features
        "waiting": 0.70,
        "capacity": 0.80,
        "skipped": 1,
        "energy": 0.20,
        "door": 0.10,

        # MWW features
        "walking_speed": 1.0,
        "direction": "toward"
    },


    {
        "floor": 5,

        # PCS features
        "distance": 0.70,
        "direction_score": 0.80,
        "speed": 0.70,
        "facing": 1.0,
        "button": True,

        # DBOS features
        "waiting": 0.90,
        "capacity": 0.80,
        "skipped": 3,
        "energy": 0.30,
        "door": 0.15,

        # MWW features
        "walking_speed": 0.8,
        "direction": "toward"
    },


    {
        "floor": 7,

        # PCS features
        "distance": 0.40,
        "direction_score": 0.40,
        "speed": 0.30,
        "facing": 0.0,
        "button": True,

        # DBOS features
        "waiting": 0.60,
        "capacity": 0.50,
        "skipped": 4,
        "energy": 0.40,
        "door": 0.20,

        # MWW features
        "walking_speed": 0.4,
        "direction": "toward"
    }
]


# --------------------------------------------------
# SIMULATION
# --------------------------------------------------

time_step = 0

while requests:

    time_step += 1

    print()
    print("=" * 70)
    print(f"                    TIME STEP {time_step}")
    print("=" * 70)

    print()
    print(f"Elevator currently at Floor {elevator.current_floor}")

    print()
    print("Pending Requests:")

    for request in requests:
        print(
            f"  Floor {request['floor']} | "
            f"Skipped: {request['skipped']}"
        )


    # --------------------------------------------------
    # CALCULATE SCORES
    # --------------------------------------------------

    results = []

    for request in requests:

        result = calculate_request_score(request)

        results.append(result)


    # --------------------------------------------------
    # DISPLAY SCORES
    # --------------------------------------------------

    print()
    print(
        f"{'Floor':<10}"
        f"{'PCS':<10}"
        f"{'QFI':<10}"
        f"{'DBOS':<10}"
        f"{'Decision':<10}"
        f"{'MWW':<15}"
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


    # --------------------------------------------------
    # AI SELECTS BEST REQUEST
    # --------------------------------------------------

    best = max(
        results,
        key=lambda x: x["dbos"]
    )
    f"{result['mww']:<15}"

    print()
    print("AI Selected Floor:", best["floor"])
    print("DBOS:", best["dbos"])
    print("Action:", best["decision"])


    # --------------------------------------------------
    # EXECUTE DECISION
    # --------------------------------------------------

    if best["decision"] in ["STOP", "WAIT"]:

        print()
        print("AI COMMAND → ELEVATOR")

        elevator.move_to(
            best["floor"]
        )

        print()
        print(f"Floor {best['floor']} request SERVED.")

        # Remove served request
        requests = [
            request
            for request in requests
            if request["floor"] != best["floor"]
        ]


    else:

        print()
        print(
            f"Floor {best['floor']} skipped."
        )

        # Increase fairness priority
        for request in requests:

            if request["floor"] == best["floor"]:

                request["skipped"] += 1


print()
print("=" * 70)
print("             SIMULATION COMPLETED")
print("=" * 70)

print()
print(
    f"Elevator final position: "
    f"Floor {elevator.current_floor}"
)