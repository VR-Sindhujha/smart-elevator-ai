
import time

from elevator import Elevator
from simulation import calculate_request_score
from performance_metrics import generate_performance_report


# ==========================================================
# ADAPTIVE INTENT-AWARE SMART ELEVATOR — EVALUATION
# ==========================================================

TRAVEL_TIME_PER_FLOOR = 1.0

# ==========================================================
# 1. CREATE ELEVATORS
# ==========================================================

elevators = {
    "E1": Elevator(current_floor=1, capacity=12),
    "E2": Elevator(current_floor=6, capacity=12),
}

# ==========================================================
# 2. FIXED TEST REQUESTS
# ==========================================================

requests = [
    {
        "floor": 3,
        "destination_floor": 7,
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
        "walking_speed": 1.0,
    },
    {
        "floor": 7,
        "destination_floor": 2,
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
        "walking_speed": 0.4,
    },
    {
        "floor": 9,
        "destination_floor": 1,
        "type": "EMERGENCY",
    },
]

# ==========================================================
# 3. METRIC STORAGE
# ==========================================================

waiting_times = []
travel_distances = []
qfi_values = []
served_requests = 0
total_requests = len(requests)
emergency_response_times = []


# ==========================================================
# 4. SELECT BEST ELEVATOR FOR NORMAL REQUEST
# ==========================================================

def select_best_elevator(elevators, request, dbos):
    best_elevator = None
    best_score = float("-inf")

    for elevator_id, elevator in elevators.items():
        if elevator.is_full():
            print(f"{elevator_id} | FULL | Not available")
            continue

        distance = abs(elevator.current_floor - request["floor"])
        capacity_ratio = elevator.available_capacity() / elevator.capacity
        capacity_bonus = capacity_ratio * 0.10
        travel_cost = distance * 0.05

        score = dbos + capacity_bonus - travel_cost

        print(
            f"{elevator_id} | Floor: {elevator.current_floor} | "
            f"Distance: {distance} | "
            f"Available: {elevator.available_capacity()}/"
            f"{elevator.capacity} | Score: {score:.2f}"
        )

        if score > best_score:
            best_score = score
            best_elevator = elevator_id

    return best_elevator


# ==========================================================
# 5. SELECT NEAREST AVAILABLE ELEVATOR FOR EMERGENCY
# ==========================================================

def select_emergency_elevator(elevators, request):
    best_elevator = None
    shortest_distance = float("inf")

    for elevator_id, elevator in elevators.items():
        if elevator.is_full():
            print(f"{elevator_id} | FULL | Not available")
            continue

        distance = abs(elevator.current_floor - request["floor"])

        print(
            f"{elevator_id} | Floor: {elevator.current_floor} | "
            f"Distance to emergency: {distance}"
        )

        if distance < shortest_distance:
            shortest_distance = distance
            best_elevator = elevator_id

    return best_elevator


# ==========================================================
# 6. MOVE, BOARD AND COMPLETE A PASSENGER JOURNEY
# ==========================================================

def complete_passenger_journey(elevator, pickup_floor, destination_floor):
    """Move to pickup, board one passenger, then travel to destination."""

    if pickup_floor == destination_floor:
        raise ValueError("Pickup and destination floors must differ.")

    if elevator.is_full():
        print("Cannot board passenger: elevator is full.")
        return False

    pickup_distance = abs(elevator.current_floor - pickup_floor)
    travel_distances.append(pickup_distance)

    elevator.move_to(pickup_floor)

    boarded = elevator.board_passengers(
        1,
        destination_floor=destination_floor,
    )

    if boarded != 1:
        return False

    destination_distance = abs(destination_floor - pickup_floor)
    travel_distances.append(destination_distance)

    print(f"Passenger destination: Floor {destination_floor}")
    elevator.move_to(destination_floor)

    return True


# ==========================================================
# 7. RUN EVALUATION
# ==========================================================

print("\n" + "=" * 70)
print("                 AI SYSTEM EVALUATION")
print("=" * 70)

evaluation_start = time.time()

for index, request in enumerate(requests, start=1):
    pickup_floor = request["floor"]
    destination_floor = request["destination_floor"]
    request_type = request["type"]

    print("\n" + "-" * 70)
    print(f"Processing Request {index} -> Floor {pickup_floor}")
    print(f"Request Type -> {request_type}")
    print("-" * 70)

    # ------------------------------------------------------
    # EMERGENCY REQUEST
    # ------------------------------------------------------

    if request_type == "EMERGENCY":
        print("\nEMERGENCY REQUEST DETECTED")
        print("PRIORITY OVERRIDE ACTIVATED")
        print("Normal DBOS prioritization bypassed.")

        selected_elevator = select_emergency_elevator(
            elevators, request
        )

        if selected_elevator is None:
            print("No available elevator for emergency.")
            continue

        elevator = elevators[selected_elevator]
        distance = abs(elevator.current_floor - pickup_floor)

        print(f"\nEmergency Elevator -> {selected_elevator}")
        print(f"Current Floor -> {elevator.current_floor}")
        print(f"Pickup Floor -> {pickup_floor}")
        print(f"Travel Distance to Pickup -> {distance} floors")

        # Record travel to the emergency pickup.
        travel_distances.append(distance)
        elevator.move_to(pickup_floor)

        emergency_response_time = distance * TRAVEL_TIME_PER_FLOOR
        emergency_response_times.append(emergency_response_time)
        waiting_times.append(emergency_response_time)

        # Board emergency passenger.
        boarded = elevator.board_passengers(
            1,
            destination_floor=destination_floor,
        )

        if boarded != 1:
            print("Emergency passenger could not board.")
            continue

        # Travel to the emergency passenger's destination.
        destination_distance = abs(pickup_floor - destination_floor)
        travel_distances.append(destination_distance)

        print(f"Emergency passenger destination -> Floor {destination_floor}")
        elevator.move_to(destination_floor)

        served_requests += 1

        print("Emergency request SERVED.")
        print(
            f"Emergency Response Time -> "
            f"{emergency_response_time:.2f} sec"
        )
        continue

    # ------------------------------------------------------
    # NORMAL REQUEST — CALCULATE AI SCORES
    # ------------------------------------------------------

    result = calculate_request_score(request)

    pcs = result["pcs"]
    qfi = result["qfi"]
    dbos = result["dbos"]
    decision = result["decision"]
    mww = result["mww"]
    arrival_time = result["arrival_time"]

    qfi_values.append(qfi)

    print(f"\nPCS -> {pcs}")
    print(f"QFI -> {qfi}")
    print(f"DBOS -> {dbos}")
    print(f"AI Decision -> {decision}")
    print(f"MWW -> {mww}")

    # ------------------------------------------------------
    # SELECT ELEVATOR
    # ------------------------------------------------------

    print("\nEvaluating available elevators...")

    selected_elevator = select_best_elevator(
        elevators, request, dbos
    )

    if selected_elevator is None:
        print("No available elevator.")
        continue

    elevator = elevators[selected_elevator]
    distance_to_pickup = abs(elevator.current_floor - pickup_floor)

    print(f"\nAI Selected -> {selected_elevator}")

    # ------------------------------------------------------
    # WAITING TIME ESTIMATE
    # ------------------------------------------------------

    simulated_mww = 0.0

    if decision == "WAIT":
        simulated_mww = min(max(float(arrival_time), 0.0), 1.0)
        print(f"MWW ACTIVE -> Waiting {simulated_mww:.2f} sec")
        time.sleep(simulated_mww)

    # This is a simplified estimate, not wall-clock measurement.
    estimated_waiting_time = (
        distance_to_pickup * TRAVEL_TIME_PER_FLOOR
        + simulated_mww
    )
    waiting_times.append(estimated_waiting_time)

    # ------------------------------------------------------
    # COMPLETE NORMAL PASSENGER JOURNEY
    # ------------------------------------------------------

    completed = complete_passenger_journey(
        elevator,
        pickup_floor,
        destination_floor,
    )

    if not completed:
        print("Request could not be completed.")
        continue

    served_requests += 1
    print(f"Request {index} SERVED by {selected_elevator}.")


# ==========================================================
# 8. CALCULATE PERFORMANCE METRICS
# ==========================================================

total_capacity = sum(e.capacity for e in elevators.values())
occupied_capacity = sum(e.passengers for e in elevators.values())

average_emergency_response = (
    sum(emergency_response_times) / len(emergency_response_times)
    if emergency_response_times
    else 0.0
)

report = generate_performance_report(
    waiting_times=waiting_times,
    travel_distances=travel_distances,
    total_requests=total_requests,
    served_requests=served_requests,
    occupied_capacity=occupied_capacity,
    total_capacity=total_capacity,
    qfi_values=qfi_values,
    emergency_request_time=0,
    emergency_arrival_time=average_emergency_response,
)


# ==========================================================
# 9. DISPLAY RESULTS
# ==========================================================

print("\n" + "=" * 70)
print("                 PERFORMANCE RESULTS")
print("=" * 70)

print(f"Total Requests            : {total_requests}")
print(f"Requests Served           : {served_requests}")
print(f"Average Estimated Waiting : {report['average_waiting_time']} sec")
print(f"Total Travel Distance     : {report['total_travel_distance']} floors")
print(f"Requests Served (%)       : {report['requests_served_percentage']}%")
print(f"Occupancy Snapshot        : {report['elevator_utilization']}%")
print(f"Fairness Proxy Score      : {report['fairness_score']}%")
print(f"Emergency Response Time   : {report['emergency_response_time']} sec")

print("\nFINAL ELEVATOR STATES")
print("-" * 70)

for elevator_id, elevator in elevators.items():
    print(
        f"{elevator_id} | Floor: {elevator.current_floor} | "
        f"Occupancy: {elevator.passengers}/{elevator.capacity} | "
        f"Destinations: {elevator.destinations}"
    )

print("\n" + "=" * 70)
print("                 EVALUATION COMPLETE")
print("=" * 70)
print(f"Execution Time: {time.time() - evaluation_start:.2f} sec")
