class Elevator:
    def __init__(self, current_floor=1, capacity=12):
        self.current_floor = current_floor
        self.capacity = capacity
        self.passengers = 0

    def move_to(self, target_floor):
        print()
        print(f"Elevator moving: Floor {self.current_floor} → Floor {target_floor}")

        if target_floor > self.current_floor:
            for floor in range(self.current_floor + 1, target_floor + 1):
                print(f"  Passing Floor {floor}")

        elif target_floor < self.current_floor:
            for floor in range(self.current_floor - 1, target_floor - 1, -1):
                print(f"  Passing Floor {floor}")

        self.current_floor = target_floor

        print(f"Elevator arrived at Floor {self.current_floor}")

    def board_passengers(self, count):
        available_space = self.capacity - self.passengers

        boarded = min(count, available_space)

        self.passengers += boarded

        print(f"Passengers boarded: {boarded}")
        print(f"Elevator occupancy: {self.passengers}/{self.capacity}")

    def leave_passengers(self, count):
        leaving = min(count, self.passengers)

        self.passengers -= leaving

        print(f"Passengers exited: {leaving}")
        print(f"Elevator occupancy: {self.passengers}/{self.capacity}")
