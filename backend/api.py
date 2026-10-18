from elevator import Elevator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pcs import calculate_pcs
from qfi import calculate_qfi
from dbos import calculate_dbos
from mww import calculate_mww


app = FastAPI(
    title="Adaptive Intent-Aware Smart Elevator API",
    description="API for AI-based elevator dispatch decisions",
    version="1.0.0",
)
# Shared elevator state for the running backend.
elevators = {
    "E1": Elevator(current_floor=1, capacity=12),
    "E2": Elevator(current_floor=7, capacity=12),
}
# Allow the local React development server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ElevatorRequest(BaseModel):
    floor: int = Field(ge=1, le=10)
    distance: float = Field(ge=0, le=1)
    direction: float = Field(ge=0, le=1)
    speed: float = Field(ge=0, le=1)
    facing: float = Field(ge=0, le=1)
    button: bool
    waiting: float = Field(ge=0, le=1)
    capacity: float = Field(ge=0, le=1)
    skipped: int = Field(ge=0)
    energy: float = Field(ge=0, le=1)
    door: float = Field(ge=0, le=1)
    walking_speed: float = Field(default=1.0, gt=0)


def make_decision(dbos, pcs, qfi):
    # Match the fairness override used by the simulation.
    if qfi >= 0.80:
        return "STOP"
    if dbos >= 0.70:
        return "STOP"
    if dbos >= 0.50 and pcs >= 0.70:
        return "WAIT"
    return "SKIP"


@app.get("/")
def root():
    return {
        "message": "Adaptive AI Elevator API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "online"}


@app.post("/evaluate")
def evaluate_request(request: ElevatorRequest):
    pcs = calculate_pcs(
        distance_score=request.distance,
        direction_score=request.direction,
        speed_score=request.speed,
        facing_score=request.facing,
        button_pressed=request.button,
    )

    qfi = calculate_qfi(
        skipped_count=request.skipped,
    )

    dbos = calculate_dbos(
        pcs=pcs,
        waiting_score=request.waiting,
        capacity_score=request.capacity,
        qfi=qfi,
        energy_cost=request.energy,
        door_cost=request.door,
    )

    decision = make_decision(dbos, pcs, qfi)

    mww = calculate_mww(
        distance=request.distance,
        walking_speed=request.walking_speed,
        pcs=pcs,
    )

    return {
        "floor": request.floor,
        "pcs": pcs,
        "qfi": qfi,
        "dbos": dbos,
        "decision": decision,
        "mww": mww,
    }

@app.post("/run-simulation")
def run_simulation():
    from simulation_updated import calculate_request_score

    requests = [
        {
            "floor": 3,
            "distance": 0.9,
            "direction_score": 0.9,
            "speed": 0.9,
            "facing": 0.9,
            "button": True,
            "waiting": 0.5,
            "capacity": 0.8,
            "skipped": 1,
            "energy": 0.3,
            "door": 0.2,
            "walking_speed": 1.0,
        },
        {
            "floor": 5,
            "distance": 0.8,
            "direction_score": 0.8,
            "speed": 0.8,
            "facing": 0.8,
            "button": True,
            "waiting": 0.7,
            "capacity": 0.7,
            "skipped": 3,
            "energy": 0.4,
            "door": 0.3,
            "walking_speed": 1.0,
        },
        {
            "floor": 7,
            "distance": 0.4,
            "direction_score": 0.5,
            "speed": 0.5,
            "facing": 0.4,
            "button": True,
            "waiting": 0.8,
            "capacity": 0.5,
            "skipped": 4,
            "energy": 0.6,
            "door": 0.4,
            "walking_speed": 1.0,
        },
    ]

    results = [
        calculate_request_score(request)
        for request in requests
    ]

    fairness_requests = [
        result for result in results
        if result["qfi"] >= 0.80
    ]

    if fairness_requests:
        selected = max(
            fairness_requests,
            key=lambda result: (result["qfi"], result["dbos"]),
        )
    else:
        selected = max(results, key=lambda result: result["dbos"])

    return {
        "status": "success",
        "requests_evaluated": len(results),
        "selected_floor": selected["floor"],
        "selected_decision": selected["decision"],
        "results": results,
    }

from typing import Literal


class ElevatorState(BaseModel):
    elevator_id: Literal["E1", "E2"]
    current_floor: int = Field(ge=1, le=10)
    available: bool = True


class EmergencyRequest(BaseModel):
    emergency_floor: int = Field(ge=1, le=10)
    elevators: list[ElevatorState] = Field(min_length=1)


@app.post("/emergency-dispatch")
def emergency_dispatch(request: EmergencyRequest):
    available_elevators = [
        elevator
        for elevator in request.elevators
        if elevator.available
    ]

    if not available_elevators:
        return {
            "status": "unavailable",
            "message": "No available elevators for emergency dispatch.",
            "emergency_floor": request.emergency_floor,
            "selected_elevator": None,
            "distance": None,
        }

    selected = min(
        available_elevators,
        key=lambda elevator: (
            abs(elevator.current_floor - request.emergency_floor),
            elevator.elevator_id,
        ),
    )

    return {
        "status": "success",
        "message": "Emergency priority override activated.",
        "emergency_floor": request.emergency_floor,
        "selected_elevator": selected.elevator_id,
        "elevator_current_floor": selected.current_floor,
        "distance": abs(
            selected.current_floor - request.emergency_floor
        ),
        "decision": "EMERGENCY_PRIORITY",
        "normal_dbos_bypassed": True,
    }
@app.get("/elevators")
def get_elevators():
    return {
        "elevators": {
            elevator_id: elevator.get_state()
            for elevator_id, elevator in elevators.items()
        }
    }

class MoveElevatorRequest(BaseModel):
    elevator_id: Literal["E1", "E2"]
    target_floor: int = Field(ge=1, le=10)


@app.post("/elevators/move")
def move_elevator(request: MoveElevatorRequest):
    elevator = elevators[request.elevator_id]

    if elevator.is_moving:
        return {
            "status": "busy",
            "message": f"{request.elevator_id} is already moving.",
            "state": elevator.get_state(),
        }

    elevator.move_to(request.target_floor)

    return {
        "status": "success",
        "message": f"{request.elevator_id} arrived at floor {request.target_floor}.",
        "elevator_id": request.elevator_id,
        "state": elevator.get_state(),
    }


# ---------------- TRAFFIC SCENARIO SIMULATION ----------------
# These endpoints extend the existing API without changing its current routes.
from fastapi import HTTPException
from traffic_engine import TrafficSimulation

traffic_simulation = TrafficSimulation(elevators)

@app.get("/traffic/scenarios")
def get_traffic_scenarios():
    return {"scenarios": traffic_simulation.list_scenarios()}

@app.get("/traffic/status")
def get_traffic_status():
    return traffic_simulation.status()

@app.post("/traffic/configure/{scenario}")
def configure_traffic_scenario(scenario: str):
    try:
        return traffic_simulation.configure(scenario)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.post("/traffic/step")
def step_traffic_simulation():
    return traffic_simulation.step()

@app.post("/traffic/run/{steps}")
def run_traffic_simulation(steps: int):
    if steps < 1 or steps > 20:
        raise HTTPException(status_code=400, detail="steps must be between 1 and 20")
    return traffic_simulation.run(steps)

@app.post("/traffic/reset")
def reset_traffic_simulation():
    return traffic_simulation.reset()
