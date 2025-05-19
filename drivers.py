from abc import ABC, abstractmethod
from parking import MultiLevelCarPark

class Driver(ABC):
    def __init__(self, carpark: MultiLevelCarPark) -> None:
        self.carpark = carpark
        self.current_level = 0
        self.pos = carpark.south_entrance
        self.direction = (-1, 0)  # north

    def check_fov(self) -> None:
        """
        Check within the field of view (FOV) of the driver for parking spaces.
        The FOV is a cone in the direction the driver is facing along with a 1 cell wide ring
        around the driver's current position.
        """
        n, m = len(self.carpark.levels[0]), len(self.carpark.levels[0][0])
        fov = []
        for i in range(max(0, self.pos[0] - 1), min(n, self.pos[0] + 2)):
            row = []
            for j in range(max(0, self.pos[1] - 1), min(m, self.pos[1] + 2)):
                row.append(self.carpark.levels[i][j])
            fov.append(row)
        return fov
    
    @abstractmethod
    def search_for_parking(self) -> None:
        pass