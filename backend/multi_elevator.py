from elevator import Elevator
from simulation import calculate_request_score
import time


# ==================================================
# ELEVATOR SCORE FOR NORMAL REQUESTS
# ==================================================

def calculate_elevator_score(elevator, request, dbos):

    request_floor = request["floor"]

    # Distance from elevator to passenger
    distance = abs(
        elevator.current_floor - request_floor
    )

    # Available capacity
    available_capacity = (
        elevator.capacity - elevator.passengers
    )

    capacity_ratio = (
        available_capacity / elevator.capacity
    )

    # Travel cost
    travel_cost = distance * 0.05

    # Capacity advantage
    capacity_bonus = capacity_ratio * 0.10

    # Final score
    score = (
        dbos
        + capacity_bonus
        - travel_cost
    )

    return round(score, 2)


# ==================================================
# NORMAL REQUEST → SELECT BEST ELEVATOR
# ==================================================

def select_best_elevator(elevators, request):

    best_elevator = None
    best_score = float("-inf")

    result = calculate_request_score(request)
    dbos = result["dbos"]

    print()
    print("Elevator Evaluation")
    print("-" * 70)

    for elevator_id, elevator in elevators.items():

        # Capacity check
        if elevator.passengers >= elevator.capacity:

            print(
                f"{elevator_id} | FULL | "
                f"Not available"
            )

            continue

        distance = abs(
            elevator.current_floor
            - request["floor"]
        )

        available_capacity = (
            elevator.capacity
            - elevator.passengers
        )

        capacity_ratio = (
            available_capacity
            / elevator.capacity
        )

        travel_cost = distance * 0.05

        capacity_bonus = (
            capacity_ratio * 0.10
        )

        elevator_score = calculate_elevator_score(
            elevator,
            request,
            dbos
        )

        print(
            f"{elevator_id} | "
            f"Floor: {elevator.current_floor} | "
            f"Distance: {distance} | "
            f"Available: "
            f"{available_capacity}/"
            f"{elevator.capacity} | "
            f"Travel Cost: {travel_cost:.2f} | "
            f"Capacity Bonus: {capacity_bonus:.2f} | "
            f"Score: {elevator_score}"
        )

        if elevator_score > best_score:

            best_score = elevator_score
            best_elevator = elevator_id

    return best_elevator


# ==================================================
# EMERGENCY REQUEST
# ==================================================

def select_emergency_elevator(elevators, request):

    best_elevator = None
    shortest_distance = float("inf")

    request_floor = request["floor"]

    print()
    print("EMERGENCY ELEVATOR EVALUATION")
    print("-" * 70)

    for elevator_id, elevator in elevators.items():

        # Full elevators cannot be selected
        if elevator.passengers >= elevator.capacity:

            print(
                f"{elevator_id} | FULL | "
                f"Not available"
            )

            continue

        distance = abs(
            elevator.current_floor
            - request_floor
        )

        print(
            f"{elevator_id} | "
            f"Current Floor: "
            f"{elevator.current_floor} | "
            f"Distance: {distance}"
        )

        # Emergency → nearest available elevator
        if distance < shortest_distance:

            shortest_distance = distance
            best_elevator = elevator_id

    return best_elevator


# ==================================================
# CREATE ELEVATORS
# ==================================================

elevators = {

    "E1": Elevator(
        current_floor=1,
        capacity=12
    ),

    "E2": Elevator(
        current_floor=6,
        capacity=12
    )
}


# ==================================================
# PASSENGER REQUESTS
# ==================================================

requests = [

    # ----------------------------------------------
    # NORMAL REQUEST — FLOOR 3
    # ----------------------------------------------

    {
        "floor": 3,
        "type": "NORMAL",

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

        "walking_speed": 1.0
    },

    # ----------------------------------------------
    # NORMAL REQUEST — FLOOR 7
    # ----------------------------------------------

    {
        "floor": 7,
        "type": "NORMAL",

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

        "walking_speed": 0.4
    },

    # ----------------------------------------------
    # EMERGENCY REQUEST — FLOOR 9
    # ----------------------------------------------

    {
        "floor": 9,
        "type": "EMERGENCY"
    }
]


# ==================================================
# SIMULATION
# ==================================================

print()
print("=" * 70)
print("             MULTI-ELEVATOR AI DISPATCH")
print("=" * 70)


for request in requests:

    print()
    print("=" * 70)

    print(
        f"Passenger Request → "
        f"Floor {request['floor']}"
    )

    print(
        f"Request Type → "
        f"{request['type']}"
    )

    print("=" * 70)

    # ==================================================
    # EMERGENCY REQUEST
    # ==================================================

    if request["type"] == "EMERGENCY":

        print()
        print("🚨 EMERGENCY REQUEST DETECTED")

        print()
        print(
            "PRIORITY OVERRIDE ACTIVATED"
        )

        print(
            "Normal DBOS prioritization bypassed."
        )

        print(
            "Selecting nearest available elevator..."
        )

        selected_elevator = select_emergency_elevator(
            elevators,
            request
        )

        if selected_elevator is None:

            print()
            print(
                "No available elevator "
                "for emergency!"
            )

            continue

        print()
        print(
            f"EMERGENCY → "
            f"Elevator {selected_elevator} "
            f"selected"
        )

        elevator = elevators[
            selected_elevator
        ]

        print()
        print(
            "Emergency elevator dispatching..."
        )

        elevator.move_to(
            request["floor"]
        )

        print()
        print(
            f"Emergency request at Floor "
            f"{request['floor']} SERVED "
            f"by {selected_elevator}"
        )

        continue

    # ==================================================
    # NORMAL REQUEST
    # ==================================================

    result = calculate_request_score(
        request
    )

    print()
    print("Passenger Request Metrics")
    print("-" * 70)

    print(
        f"PCS          : "
        f"{result['pcs']}"
    )

    print(
        f"QFI          : "
        f"{result['qfi']}"
    )

    print(
        f"DBOS         : "
        f"{result['dbos']}"
    )

    print(
        f"AI Decision  : "
        f"{result['decision']}"
    )

    print(
        f"MWW          : "
        f"{result['mww']}"
    )

    # ==================================================
    # SELECT ELEVATOR
    # ==================================================

    selected_elevator = select_best_elevator(
        elevators,
        request
    )

    if selected_elevator is None:

        print()
        print(
            "No available elevator."
        )

        continue

    print()
    print(
        f"AI Selected Elevator: "
        f"{selected_elevator}"
    )

    elevator = elevators[
        selected_elevator
    ]

    # ==================================================
    # MOVE
    # ==================================================

    print()

    elevator.move_to(
        request["floor"]
    )

    # ==================================================
    # MICRO WAIT
    # ==================================================

    if result["decision"] == "WAIT":

        wait_time = result["arrival_time"]

        print()
        print(
            f"MWW ACTIVE → Waiting "
            f"{wait_time} seconds..."
        )

        time.sleep(wait_time)

        print(
            "Passenger arrived."
        )

    # ==================================================
    # BOARD
    # ==================================================

    print()

    print(
        f"Passenger boarding "
        f"Elevator {selected_elevator}..."
    )

    elevator.board_passengers(1)

    print()
    print(
        f"Request for Floor "
        f"{request['floor']} SERVED by "
        f"{selected_elevator}"
    )


# ==================================================
# FINAL STATE
# ==================================================

print()
print("=" * 70)
print("             FINAL ELEVATOR STATES")
print("=" * 70)

for elevator_id, elevator in elevators.items():

    print(
        f"{elevator_id} | "
        f"Floor: {elevator.current_floor} | "
        f"Occupancy: "
        f"{elevator.passengers}/"
        f"{elevator.capacity}"
    )

print()
print("=" * 70)
print("          MULTI-ELEVATOR SIMULATION DONE")
print("=" * 70)