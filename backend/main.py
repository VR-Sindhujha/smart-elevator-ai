from pcs import calculate_pcs
from qfi import calculate_qfi
from dbos import calculate_dbos
from elevator import Elevator


def make_decision(dbos, pcs):
    if dbos >= 0.70:
        return "STOP"

    elif dbos >= 0.50 and pcs >= 0.70:
        return "WAIT"

    else:
        return "SKIP"


# --------------------------------------------------
# CREATE ELEVATOR
# --------------------------------------------------

elevator = Elevator(
    current_floor=1,
    capacity=12
)


# --------------------------------------------------
# SIMULATED FLOOR REQUESTS
# --------------------------------------------------

floors = [
    {
        "floor": 3,
        "distance": 0.95,
        "direction": 1.0,
        "speed": 0.90,
        "facing": 1.0,
        "button": True,
        "waiting": 0.70,
        "capacity": 0.80,
        "skipped": 1,
        "energy": 0.20,
        "door": 0.10
    },

    {
        "floor": 5,
        "distance": 0.70,
        "direction": 0.80,
        "speed": 0.70,
        "facing": 1.0,
        "button": True,
        "waiting": 0.90,
        "capacity": 0.80,
        "skipped": 3,
        "energy": 0.30,
        "door": 0.15
    },

    {
        "floor": 7,
        "distance": 0.40,
        "direction": 0.40,
        "speed": 0.30,
        "facing": 0.0,
        "button": True,
        "waiting": 0.60,
        "capacity": 0.50,
        "skipped": 4,
        "energy": 0.40,
        "door": 0.20
    },

    {
        "floor": 10,
        "distance": 0.20,
        "direction": 0.10,
        "speed": 0.20,
        "facing": 0.0,
        "button": False,
        "waiting": 0.20,
        "capacity": 0.50,
        "skipped": 0,
        "energy": 0.80,
        "door": 0.30
    }
]


# --------------------------------------------------
# CALCULATE AI SCORES
# --------------------------------------------------

results = []

for request in floors:

    pcs = calculate_pcs(
        distance_score=request["distance"],
        direction_score=request["direction"],
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
        pcs
    )

    results.append({
        "floor": request["floor"],
        "pcs": pcs,
        "qfi": qfi,
        "dbos": dbos,
        "decision": decision
    })


# --------------------------------------------------
# DISPLAY AI ANALYSIS
# --------------------------------------------------

print()
print("=" * 70)
print("              AI ELEVATOR DECISION ENGINE")
print("=" * 70)

print()

print(
    f"{'Floor':<10}"
    f"{'PCS':<10}"
    f"{'QFI':<10}"
    f"{'DBOS':<10}"
    f"{'Decision':<10}"
)

print("-" * 70)

for result in results:

    print(
        f"{result['floor']:<10}"
        f"{result['pcs']:<10}"
        f"{result['qfi']:<10}"
        f"{result['dbos']:<10}"
        f"{result['decision']:<10}"
    )


# --------------------------------------------------
# AI SELECTS BEST FLOOR
# --------------------------------------------------

best_floor = max(
    results,
    key=lambda x: x["dbos"]
)


# --------------------------------------------------
# FINAL AI DECISION
# --------------------------------------------------

print()
print("=" * 70)
print("                 AI FINAL DECISION")
print("=" * 70)

print()

print(f"Current Elevator Floor : {elevator.current_floor}")
print(f"Selected Floor         : {best_floor['floor']}")
print(f"DBOS                   : {best_floor['dbos']}")
print(f"PCS                    : {best_floor['pcs']}")
print(f"QFI                    : {best_floor['qfi']}")
print(f"Action                 : {best_floor['decision']}")


# --------------------------------------------------
# ELEVATOR EXECUTES AI DECISION
# --------------------------------------------------

if best_floor["decision"] in ["STOP", "WAIT"]:

    print()
    print("=" * 70)
    print("                 ELEVATOR ACTION")
    print("=" * 70)

    elevator.move_to(
        best_floor["floor"]
    )

    print()
    print("AI decision successfully executed.")