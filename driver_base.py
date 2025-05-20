from parking import MultiLevelCarPark, CellType
from abc import ABC, abstractmethod
from time import sleep
from typing import Tuple

class Driver(ABC):
    _directions = (
        (-1, 0),  # north
        (0, 1),  # east
        (1, 0),  # south
        (0, -1),  # west
    )

    _display_map = (
        "◇", # road
        "◇", # ramp
        "▢", # unoccupied
        "▣", # occupied
        " ", # void
    )
    _cur_pos_symbol = "◈"

    def __init__(self, carpark: MultiLevelCarPark) -> None:
        self.carpark = carpark
        self.current_level = 0
        self.pos = carpark.south_entrance
        self.direction = (-1, 0)  # north
        self.fov = []
        self.time = 0
        self.completed = False

    def check_fov(self) -> Tuple[int, int] | None:
        """
        Check within the field of view (FOV) of the driver for parking spaces.
        The FOV is a cone in the direction the driver is facing along with a 1 cell wide ring
        around the driver's current position.
        
        Returns:
            A tuple of (row, column) if a parking space is found, otherwise None.
        """

        self.fov.clear()
        # check perimeter of driver's current position
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if (dy, dx) == (0, 0):
                    continue
                i, j = self.pos[0] + dy, self.pos[1] + dx
                if self._within_bounds((i, j)):
                    self.fov.append((i, j))
        
        # check cone in the direction the driver is facing
        dir_index = self._directions.index(self.direction)
        left_dir, right_dir = self._directions[(dir_index - 1) % 4], self._directions[(dir_index + 1) % 4]
        for k in range(2, 4):
            mid = self.pos[0] + k * self.direction[0], self.pos[1] + k * self.direction[1]
            if self._within_bounds(mid):
                self.fov.append(mid)
            
            l = r = mid
            for _ in range(k):
                l = l[0] + left_dir[0], l[1] + left_dir[1]
                r = r[0] + right_dir[0], r[1] + right_dir[1]
                if self._within_bounds(l):
                    self.fov.append(l)
                if self._within_bounds(r):
                    self.fov.append(r)

        # check if any of the cells in the FOV are free parking spaces
        for cell in self.fov:
            if self.carpark.levels[self.current_level][cell[0]][cell[1]] == CellType.UNOCCUPIED:
                return cell
        return None
            
    def _within_bounds(self, pos: Tuple[int, int]) -> bool:
        """
        Check if the given position is within the bounds of the carpark.
        
        Args:
            pos: A tuple of (row, column) representing the position to check.
        
        Returns:
            True if the position is within bounds, False otherwise.
        """
        return 0 <= pos[0] < len(self.carpark.levels[0]) and 0 <= pos[1] < len(self.carpark.levels[0][0])
    
    def search_for_parking(self, delay = 0.3) -> None:
        """
        Search for a parking space in the carpark.
        This method will keep moving in the current direction until a parking space is found.
        
        Args:
            delay: The delay in seconds between each tick of the driver's actions.
        """
        while not self.completed:
            self.display()
            self.tick()
            sleep(delay)

    @abstractmethod
    def tick(self) -> None:
        """
        Perform a single tick of the driver's actions.
        This method should be implemented by subclasses to define the driver's behavior.
        """
        pass

    def display(self) -> None:
        grid = self.carpark.levels[self.current_level]
        n, m = len(grid), len(grid[0])
        print(f"┌{"─"*n*3}─┐")
        for i in range(n):
            s = "│"
            for j in range(m):
                s += " "
                s += self._display_map[grid[i][j].value] if (i, j) != self.pos else "◈"
                s += " "
            s += " │"
            print(s)
        print(f"└{"─"*n*3}─┘")
        print(f"t = {self.time}{" "*(n*3-4)}L{self.current_level}")