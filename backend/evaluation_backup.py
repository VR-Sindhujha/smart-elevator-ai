import time

from elevator import Elevator
from simulation import calculate_request_score
from performance_metrics import generate_performance_report


# ==========================================================
# AI SYSTEM EVALUATION
# Adaptive Intent-Aware Smart Elevator Dispatch System
# ==========================================================


# ----------------------------------------------------------
# 1. CREATE ELEVATORS
# ----------------------------------------------------------

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


# ----------------------------------------------------------
# 2. TEST REQUESTS
# ----------------------------------------------------------

requests = [

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

    {
        "floor": 9,
        "type": "EMERGENCY"
    }
]


# ----------------------------------------------------------
# 3. METRIC STORAGE
# ----------------------------------------------------------

waiting_times = []

travel_distances = []

qfi_values = []

served_requests = 0

total_requests = len(requests)

emergency_response_times = []


# ----------------------------------------------------------
# 4. ELEVATOR SELECTION
# ----------------------------------------------------------

def select_best_elevator(elevators, request, dbos):

    best_elevator = None
    best_score = float("-inf")

    for elevator_id, elevator in elevators.items():

        # Ignore full elevators
        if elevator.passengers >= elevator.capacity:
            continue

        distance = abs(
            elevator.current_floor -
            request["floor"]
        )

        # Available capacity
        available_capacity = (
            elevator.capacity -
            elevator.passengers
        )

        # Capacity ratio
        capacity_ratio = (
            available_capacity /
            elevator.capacity
        )

        # Capacity bonus
        capacity_bonus = (
            capacity_ratio * 0.10
        )

        # Travel cost
        travel_cost = distance * 0.05

        # Final elevator score
        score = (
            dbos
            + capacity_bonus
            - travel_cost
        )

        print(
            f"{elevator_id} | "
            f"Current Floor: {elevator.current_floor} | "
            f"Distance: {distance} | "
            f"Capacity: "
            f"{available_capacity}/"
            f"{elevator.capacity} | "
            f"Score: {round(score, 2)}"
        )

        if score > best_score:

            best_score = score

            best_elevator = elevator_id

    return best_elevator


# ----------------------------------------------------------
# 5. EMERGENCY ELEVATOR SELECTION
# ----------------------------------------------------------

def select_emergency_elevator(elevators, request):

    best_elevator = None
    shortest_distance = float("inf")

    for elevator_id, elevator in elevators.items():

        # Ignore full elevators
        if elevator.passengers >= elevator.capacity:
            continue

        distance = abs(
            elevator.current_floor -
            request["floor"]
        )

        if distance < shortest_distance:

            shortest_distance = distance

            best_elevator = elevator_id

    return best_elevator


# ----------------------------------------------------------
# 6. START EVALUATION
# ----------------------------------------------------------

print()

print("=" * 70)

print(
    "                 AI SYSTEM EVALUATION"
)

print("=" * 70)


evaluation_start = time.time()


# ----------------------------------------------------------
# 7. PROCESS EVERY REQUEST
# ----------------------------------------------------------

for index, request in enumerate(
    requests,
    start=1
):

    print()

    print("-" * 70)

    print(
        f"Processing Request {index} "
        f"→ Floor {request['floor']}"
    )

    print(
        f"Request Type → "
        f"{request['type']}"
    )

    print("-" * 70)


    # ======================================================
    # EMERGENCY REQUEST
    # ======================================================

    if request["type"] == "EMERGENCY":

        print()

        print(
            "🚨 EMERGENCY REQUEST DETECTED"
        )

        print(
            "PRIORITY OVERRIDE ACTIVATED"
        )

        print(
            "Normal DBOS prioritization bypassed."
        )



        selected_elevator = (
            select_emergency_elevator(
                elevators,
                request
            )
        )


        if selected_elevator is None:

            print(
                "No available elevator."
            )

            continue


        elevator = elevators[
            selected_elevator
        ]


        distance = abs(
            elevator.current_floor -
            request["floor"]
        )


        print()

        print(
            f"Emergency Elevator → "
            f"{selected_elevator}"
        )

        print(
            f"Current Floor → "
            f"{elevator.current_floor}"
        )

        print(
            f"Target Floor → "
            f"{request['floor']}"
        )

        print(
            f"Travel Distance → "
            f"{distance} floors"
        )


        # Move elevator
        elevator.move_to(
            request["floor"]
        )


        # Simulated emergency response time
        # Assume 1 second of elevator travel per floor
        TRAVEL_TIME_PER_FLOOR = 1.0

        emergency_response_time = (
            distance * TRAVEL_TIME_PER_FLOOR
        )


        emergency_response_times.append(
            emergency_response_time
        )


        travel_distances.append(
            distance
        )


        elevator.board_passengers(1)


        served_requests += 1


        print()

        print(
            "Emergency request SERVED."
        )

        print(
            f"Emergency Response Time → "
            f"{round(emergency_response_time, 2)} sec"
        )


        continue


    # ======================================================
    # NORMAL REQUEST
    # ======================================================

    result = calculate_request_score(
        request
    )


    pcs = result["pcs"]

    qfi = result["qfi"]

    dbos = result["dbos"]

    decision = result["decision"]

    mww = result["mww"]

    arrival_time = result[
        "arrival_time"
    ]


    # Store QFI
    qfi_values.append(qfi)


    print()

    print(
        f"PCS  → {pcs}"
    )

    print(
        f"QFI  → {qfi}"
    )

    print(
        f"DBOS → {dbos}"
    )

    print(
        f"AI Decision → {decision}"
    )

    print(
        f"MWW → {mww}"
    )


    # ------------------------------------------------------
    # SELECT BEST ELEVATOR
    # ------------------------------------------------------

    print()

    print(
        "Evaluating available elevators..."
    )


    selected_elevator = (
        select_best_elevator(
            elevators,
            request,
            dbos
        )
    )


    if selected_elevator is None:

        print(
            "No available elevator."
        )

        continue


    elevator = elevators[
        selected_elevator
    ]


    print()

    print(
        f"AI Selected → "
        f"{selected_elevator}"
    )


    # ------------------------------------------------------
    # TRAVEL DISTANCE
    # ------------------------------------------------------

    distance = abs(
        elevator.current_floor -
        request["floor"]
    )


    travel_distances.append(
        distance
    )


    # ------------------------------------------------------
    # WAITING TIME
    # ------------------------------------------------------

    if decision == "WAIT":

        waiting_time = arrival_time

        print()

        print(
            f"MWW ACTIVE → "
            f"Passenger arrival "
            f"in {arrival_time} sec"
        )

        # Simulated wait.
        # Kept short for evaluation.
        simulated_wait = min(
            arrival_time,
            1.0
        )

        time.sleep(
            simulated_wait
        )

    else:

        waiting_time = 0


    waiting_times.append(
        waiting_time
    )


    # ------------------------------------------------------
    # MOVE ELEVATOR
    # ------------------------------------------------------

    elevator.move_to(
        request["floor"]
    )


    # ------------------------------------------------------
    # BOARD PASSENGER
    # ------------------------------------------------------

    elevator.board_passengers(1)


    served_requests += 1


    print()

    print(
        f"Request {index} SERVED."
    )


# ==========================================================
# 8. FINAL SYSTEM STATE
# ==========================================================

total_capacity = sum(
    elevator.capacity
    for elevator in elevators.values()
)


occupied_capacity = sum(
    elevator.passengers
    for elevator in elevators.values()
)


# ==========================================================
# 9. CALCULATE METRICS
# ==========================================================

if emergency_response_times:

    emergency_response_time = (
        sum(emergency_response_times)
        /
        len(emergency_response_times)
    )

else:

    emergency_response_time = 0


report = generate_performance_report(

    waiting_times=waiting_times,

    travel_distances=travel_distances,

    total_requests=total_requests,

    served_requests=served_requests,

    occupied_capacity=occupied_capacity,

    total_capacity=total_capacity,

    qfi_values=qfi_values,

    emergency_request_time=0,

    emergency_arrival_time=
        emergency_response_time
)


# ==========================================================
# 10. PERFORMANCE RESULTS
# ==========================================================

print()

print("=" * 70)

print(
    "                 PERFORMANCE RESULTS"
)

print("=" * 70)

print()

print(
    f"Total Requests           : "
    f"{total_requests}"
)

print(
    f"Requests Served          : "
    f"{served_requests}"
)

print(
    f"Average Waiting Time     : "
    f"{report['average_waiting_time']} sec"
)

print(
    f"Total Travel Distance    : "
    f"{report['total_travel_distance']} floors"
)

print(
    f"Requests Served (%)      : "
    f"{report['requests_served_percentage']}%"
)

print(
    f"Elevator Utilization     : "
    f"{report['elevator_utilization']}%"
)

print(
    f"Fairness Score           : "
    f"{report['fairness_score']}%"
)

print(
    f"Emergency Response Time  : "
    f"{report['emergency_response_time']} sec"
)


# ==========================================================
# 11. ELEVATOR FINAL STATE
# ==========================================================

print()

print(
    "FINAL ELEVATOR STATE"
)

print("-" * 70)


for elevator_id, elevator in elevators.items():

    print(
        f"{elevator_id} → "
        f"Floor {elevator.current_floor} | "
        f"Occupancy "
        f"{elevator.passengers}/"
        f"{elevator.capacity}"
    )


# ==========================================================
# 12. EVALUATION COMPLETE
# ==========================================================

total_evaluation_time = (
    time.time() -
    evaluation_start
)


print()

print("=" * 70)

print(
    "                 EVALUATION COMPLETE"
)

print("=" * 70)

print()

print(
    f"Evaluation Execution Time : "
    f"{round(total_evaluation_time, 2)} sec"
)

print()

print(
    "All evaluation metrics "
    "generated successfully."
)

print("=" * 70)