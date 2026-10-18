
from elevator import Elevator

def run_test(name, operation):
    print(f"\nTEST: {name}")
    try:
        operation()
        print("FAIL: Invalid input was accepted")
    except ValueError as error:
        print(f"PASS: {error}")

elevator = Elevator()

run_test(
    "Negative passenger count",
    lambda: elevator.board_passengers(-1)
)

run_test(
    "Floor zero",
    lambda: elevator.move_to(0)
)

run_test(
    "Negative floor",
    lambda: elevator.move_to(-2)
)
