
class Elevator:
    def __init__(self, current_floor=1, capacity=12):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero.")
        if current_floor < 1:
            raise ValueError("Current floor must be at least 1.")

        self.current_floor = current_floor
        self.capacity = capacity
        self.passengers = 0
        self.direction = "IDLE"
        self.is_moving = False
        self.destinations = []

    def move_to(self, target_floor):
        if target_floor < 1:
            raise ValueError("Target floor must be at least 1.")

        if target_floor == self.current_floor:
            self.direction = "IDLE"
            self.is_moving = False
            print(f"Elevator already at Floor {self.current_floor}")
            self._process_exits()
            return

        start_floor = self.current_floor
        self.direction = "UP" if target_floor > start_floor else "DOWN"
        self.is_moving = True

        print(
            f"\nElevator moving: Floor {start_floor} "
            f"→ Floor {target_floor} ({self.direction})"
        )

        step = 1 if target_floor > start_floor else -1

        for floor in range(start_floor + step, target_floor + step, step):
            print(f"  Passing Floor {floor}")
            self.current_floor = floor
            self._process_exits()

        self.direction = "IDLE"
        self.is_moving = False
        print(f"Elevator arrived at Floor {self.current_floor}")

    def board_passengers(self, count, destination_floor=None):
        if count < 0:
            raise ValueError("Passenger count cannot be negative.")

        if count == 0:
            return 0

        if destination_floor is not None:
            if destination_floor < 1:
                raise ValueError("Destination must be at least floor 1.")
            if destination_floor == self.current_floor:
                raise ValueError("Destination must differ from current floor.")

        available_space = self.available_capacity()
        boarded = min(count, available_space)

        if boarded == 0:
            print("No passengers boarded: elevator is full.")
            return 0

        if destination_floor is None:
            # Preserve compatibility with calls that don't supply destinations.
            self.passengers += boarded
        else:
            for _ in range(boarded):
                self.destinations.append(destination_floor)
            self.passengers += boarded

        print(f"Passengers boarded: {boarded}")
        if destination_floor is not None:
            print(f"Destination floor: {destination_floor}")

        print(f"Elevator occupancy: {self.passengers}/{self.capacity}")
        return boarded

    def _process_exits(self):
        exiting = self.destinations.count(self.current_floor)

        if exiting:
            self.destinations = [
                floor for floor in self.destinations
                if floor != self.current_floor
            ]
            self.passengers -= exiting
            print(f"Passengers exited at Floor {self.current_floor}: {exiting}")
            print(f"Elevator occupancy: {self.passengers}/{self.capacity}")

    def leave_passengers(self, count):
        if count < 0:
            raise ValueError("Passenger count cannot be negative.")

        # Remove destination-tracked passengers first.
        leaving = min(count, self.passengers)
        tracked_leaving = min(leaving, len(self.destinations))

        for _ in range(tracked_leaving):
            self.destinations.pop()

        self.passengers -= leaving

        print(f"Passengers exited: {leaving}")
        print(f"Elevator occupancy: {self.passengers}/{self.capacity}")
        return leaving

    def available_capacity(self):
        return self.capacity - self.passengers

    def is_full(self):
        return self.passengers >= self.capacity

    def get_state(self):
        return {
            "current_floor": self.current_floor,
            "capacity": self.capacity,
            "passengers": self.passengers,
            "available_capacity": self.available_capacity(),
            "direction": self.direction,
            "is_moving": self.is_moving,
            "destinations": self.destinations.copy(),
        }
