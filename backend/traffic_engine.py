"""Deterministic traffic scenarios for the Adaptive Intent-Aware Smart Elevator prototype.
All positions are software simulation state; no physical elevator is controlled.
"""
from dataclasses import dataclass
from typing import Dict, Any
from pcs import calculate_pcs
from qfi import calculate_qfi
from dbos import calculate_dbos
from mww import calculate_mww

SCENARIOS = {
    "low": {
        "label": "Low Traffic",
        "description": "A few requests spread across the building.",
        "requests": [(2, 0.85, 1, 0.25), (6, 0.70, 1, 0.35), (9, 0.60, 2, 0.45)],
    },
    "up_peak": {
        "label": "Morning Up-Peak",
        "description": "Concentrated upward demand from the lower floors.",
        "requests": [(1, 0.95, 1, 0.25), (2, 0.90, 2, 0.35), (3, 0.82, 2, 0.45), (4, 0.78, 1, 0.55), (5, 0.68, 1, 0.65)],
    },
    "down_peak": {
        "label": "Evening Down-Peak",
        "description": "Concentrated downward demand from the upper floors.",
        "requests": [(10, 0.94, 2, 0.25), (9, 0.88, 1, 0.35), (8, 0.74, 2, 0.45), (7, 0.64, 1, 0.55), (6, 0.57, 1, 0.65)],
    },
    "interfloor": {
        "label": "Inter-Floor Traffic",
        "description": "Requests distributed across different floors.",
        "requests": [(3, 0.90, 1, 0.25), (5, 0.82, 1, 0.35), (7, 0.72, 2, 0.45), (8, 0.55, 1, 0.55), (4, 0.48, 1, 0.65)],
    },
}

class TrafficSimulation:
    def __init__(self, elevators: Dict[str, Any]):
        self.elevators = elevators
        self.configure("low")

    @staticmethod
    def list_scenarios():
        return [{"id": k, "label": v["label"], "description": v["description"]} for k, v in SCENARIOS.items()]

    def configure(self, scenario: str):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Choose one of: {', '.join(SCENARIOS)}")
        self.scenario = scenario
        # Each scenario starts from the same reproducible elevator state.
        for elevator_id, elevator in self.elevators.items():
            elevator.current_floor = 1 if elevator_id == "E1" else 7
            elevator.passengers = 0
            elevator.destinations = []
            elevator.direction = "IDLE"
            elevator.is_moving = False
        self.tick = 0
        self.history = []
        self.metrics = {"served_requests": 0, "total_wait_seconds": 0.0, "travel_floors": 0, "stops": 0, "fairness_overrides": 0}
        # Deterministic request list makes the demo repeatable.
        self.requests = []
        for i, (floor, commitment, group, waiting) in enumerate(SCENARIOS[scenario]["requests"], 1):
            self.requests.append({"id": f"R{i}", "floor": floor, "commitment": commitment, "group_size": group,
                                  "waiting_score": waiting, "waiting_seconds": round(waiting * 60, 1), "skipped": 0,
                                  "status": "PENDING"})
        self.last_decision = None
        self.last_message = f"Scenario loaded: {SCENARIOS[scenario]['label']}"
        return self.status()

    def reset(self):
        return self.configure(self.scenario)

    def _score_request(self, request):
        usable = [e for e in self.elevators.values() if e.available_capacity() >= request["group_size"]]
        candidates = usable or list(self.elevators.values())
        car = min(candidates, key=lambda e: abs(e.current_floor - request["floor"]))
        distance_floors = abs(car.current_floor - request["floor"])
        pcs = calculate_pcs(request["commitment"], request["commitment"], 0.8, 1.0, True)
        qfi = calculate_qfi(request["skipped"])
        capacity_score = car.available_capacity() / car.capacity
        dbos = calculate_dbos(pcs, request["waiting_score"], capacity_score, qfi,
                               min(distance_floors / 9, 1.0), 0.15)
        mww = calculate_mww(distance=1.5, walking_speed=1.0, pcs=pcs)
        if qfi >= 0.8 or dbos >= 0.7:
            action = "STOP"
        elif dbos >= 0.5 and pcs >= 0.7:
            action = "WAIT"
        else:
            action = "SKIP"
        return {"request_id": request["id"], "floor": request["floor"], "group_size": request["group_size"],
                "assigned_elevator": next(k for k, v in self.elevators.items() if v is car),
                "pcs": pcs, "qfi": qfi, "dbos": dbos, "action": action,
                "waiting_seconds": request["waiting_seconds"], "arrival_time": mww["arrival_time"]}

    def status(self):
        scored = [self._score_request(r) for r in self.requests]
        served = self.metrics["served_requests"]
        average_wait = round(self.metrics["total_wait_seconds"] / served, 2) if served else 0.0
        total = served + len(self.requests)
        return {
            "scenario": self.scenario, "scenario_label": SCENARIOS[self.scenario]["label"], "tick": self.tick,
            "elevators": {k: v.get_state() for k, v in self.elevators.items()},
            "requests": [{**r, "score": next((s for s in scored if s["request_id"] == r["id"]), None)} for r in self.requests],
            "last_decision": self.last_decision, "last_message": self.last_message,
            "complete": len(self.requests) == 0,
            "metrics": {"total_requests": total, "served_requests": served, "pending_requests": len(self.requests),
                        "average_wait_seconds": average_wait, "travel_floors": self.metrics["travel_floors"],
                        "service_rate_percent": round(served / total * 100, 1) if total else 0.0,
                        "stops": self.metrics["stops"], "fairness_overrides": self.metrics["fairness_overrides"]},
            "history": self.history[-12:],
        }

    def step(self):
        self.tick += 1
        if not self.requests:
            self.last_message = "Simulation complete — no pending requests."
            return self.status()
        scored = [self._score_request(r) for r in self.requests]
        # Fairness requests win first; otherwise choose the highest DBOS.
        chosen = max(scored, key=lambda s: (s["qfi"] >= 0.8, s["qfi"], s["dbos"]))
        request = next(r for r in self.requests if r["id"] == chosen["request_id"])
        car = self.elevators[chosen["assigned_elevator"]]
        if chosen["action"] == "SKIP":
            request["skipped"] += 1
            request["waiting_seconds"] = round(request["waiting_seconds"] + 5, 1)
            request["waiting_score"] = min(1.0, request["waiting_score"] + 0.1)
            self.last_message = f"{request['id']} at Floor {request['floor']} skipped; fairness priority increased."
        else:
            origin = car.current_floor
            distance = abs(origin - request["floor"])
            # Advance simulated car state directly to destination (discrete simulation tick).
            car.move_to(request["floor"])
            boarded = min(request["group_size"], car.available_capacity())
            # Track boarded passengers without destination assumptions; the next simulation reset clears state.
            if boarded:
                car.board_passengers(boarded)
            self.metrics["served_requests"] += 1
            self.metrics["total_wait_seconds"] += request["waiting_seconds"] + distance * 2
            self.metrics["travel_floors"] += distance
            self.metrics["stops"] += 1
            if chosen["qfi"] >= 0.8:
                self.metrics["fairness_overrides"] += 1
            request["status"] = "SERVED"
            self.last_message = f"{chosen['assigned_elevator']} served {request['id']} at Floor {request['floor']} ({chosen['action']})."
            self.requests.remove(request)
        self.last_decision = chosen
        self.history.append({"tick": self.tick, "message": self.last_message, "decision": chosen})
        return self.status()

    def run(self, steps=5):
        for _ in range(max(1, min(int(steps), 20))):
            self.step()
            if not self.requests:
                break
        return self.status()
