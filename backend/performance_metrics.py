
# ==========================================================
# PERFORMANCE METRICS
# Adaptive Intent-Aware Smart Elevator Dispatch System
# ==========================================================


def calculate_average_waiting_time(waiting_times):
    """Mean waiting time for all recorded requests, in seconds."""
    if not waiting_times:
        return 0.0

    return round(sum(waiting_times) / len(waiting_times), 2)


def calculate_total_travel_distance(travel_distances):
    """Total elevator travel distance, measured in floor transitions."""
    return sum(travel_distances)


def calculate_requests_served(total_requests, served_requests):
    """Percentage of requests successfully served."""
    if total_requests <= 0:
        return 0.0

    return round((served_requests / total_requests) * 100, 2)


def calculate_elevator_utilization(occupied_capacity, total_capacity):
    """
    Snapshot occupancy percentage.
    This is NOT time-based utilization.
    """
    if total_capacity <= 0:
        return 0.0

    return round((occupied_capacity / total_capacity) * 100, 2)


def calculate_fairness_score(qfi_values):
    """
    Approximate fairness score derived from average QFI.
    Higher scores mean lower average QFI.
    """
    if not qfi_values:
        return 0.0

    average_qfi = sum(qfi_values) / len(qfi_values)
    fairness = max(0.0, min(1.0, 1.0 - average_qfi))

    return round(fairness * 100, 2)


def calculate_emergency_response_time(request_time, arrival_time):
    """Elapsed time between emergency request and elevator arrival."""
    return round(max(0.0, arrival_time - request_time), 2)


def generate_performance_report(
    waiting_times,
    travel_distances,
    total_requests,
    served_requests,
    occupied_capacity,
    total_capacity,
    qfi_values,
    emergency_request_time,
    emergency_arrival_time
):
    return {
        "average_waiting_time": calculate_average_waiting_time(
            waiting_times
        ),
        "total_travel_distance": calculate_total_travel_distance(
            travel_distances
        ),
        "requests_served_percentage": calculate_requests_served(
            total_requests, served_requests
        ),
        "elevator_utilization": calculate_elevator_utilization(
            occupied_capacity, total_capacity
        ),
        "fairness_score": calculate_fairness_score(qfi_values),
        "emergency_response_time": calculate_emergency_response_time(
            emergency_request_time, emergency_arrival_time
        )
    }


if __name__ == "__main__":
    report = generate_performance_report(
        waiting_times=[0.95, 0.00, 0.00],
        travel_distances=[2, 1, 2],
        total_requests=3,
        served_requests=3,
        occupied_capacity=2,
        total_capacity=24,
        qfi_values=[0.20, 0.80],
        emergency_request_time=0,
        emergency_arrival_time=2
    )

    print("\n" + "=" * 60)
    print("       PERFORMANCE EVALUATION")
    print("=" * 60)

    for metric, value in report.items():
        print(f"{metric.replace('_', ' ').title():32}: {value}")

    print("=" * 60)
