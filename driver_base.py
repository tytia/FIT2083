from parking import MultiLevelCarPark, CellType
from abc import ABC, abstractmethod
from collections import deque
from time import sleep
import sys
from typing import Tuple, Deque

class Style():
    RESET = '\033[0m'
    _colors = {
        "red": '\033[31m',     # occupied parking
        "green": '\033[32m',   # unoccupied parking
        "yellow": '\033[33m',  # fov
        "blue": '\033[34m',    # path
        "purple": '\033[35m'   # ramp
    }

    @staticmethod
    def colorize(text: str, color: str) -> str:
        return f"{Style._colors[color]}{text}{Style.RESET}"

class DriverBase(ABC):
    _directions = (
        (-1, 0),  # north
        (0, 1),  # east
        (1, 0),  # south
        (0, -1),  # west
    )

    _display_map_uncolored = (
        "◇", # road
        "◇", # ramp
        "▢", # unoccupied
        "▣", # occupied
        " ", # void
    )
    _display_map_colored = (
        "◇", # road
        Style.colorize("◇", "purple"), # ramp
        Style.colorize("▢", "green"), # unoccupied
        Style.colorize("▣", "red"), # occupied
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
        self.pathing_to_park = False
        self.completed = False
        self.path = self._generate_path()

    def _check_fov(self) -> Tuple[int, int] | None:
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
        return 0 <= pos[0] < self.carpark.length and 0 <= pos[1] < self.carpark.width
    
    def _calculate_path_to_park(self, pos: Tuple[int, int]) -> Deque[Tuple[int, int]]:
        """
        Calculates a path to the parking space using BFS.
        
        Args:
            pos: A tuple of (row, column) representing the position of the parking space.
        
        Returns:
            A deque of tuples representing the path to the parking space.
        """
        visited = set([self.pos])
        q = deque([[self.pos]])
        grid = self.carpark.levels[self.current_level]
        while q:
            path = q.popleft()
            current = path[-1]
            for dy, dx in self._directions:
                new_pos = (current[0] + dy, current[1] + dx)
                if self._within_bounds(new_pos):
                    if new_pos == pos:
                        path = deque(path)
                        path.popleft()
                        path.append(new_pos)
                        return path

                    if grid[new_pos[0]][new_pos[1]] == CellType.ROAD and new_pos not in visited:
                        visited.add(new_pos)
                        q.append(path + [new_pos])
        
        return deque()

    def search_for_parking(self, visualize=False, delay=0.5) -> int:
        """
        Search for a parking space in the carpark.
        This method will keep moving in the current direction until a parking space is found.
        
        Args:
            visualize: Whether to visualize the driver's actions in the carpark.
            delay: The delay in seconds between each tick of the driver's actions.
        
        Returns:
            The time taken to find a parking space.
        """
        if visualize:
            self.display()
            while not self.completed:
                # clear display
                for _ in range(self.carpark.length + 3):
                    sys.stdout.write("\x1b[1A\x1b[2K")
                self.display()
                self._tick()
                sleep(delay)
        else:
            while not self.completed:
                self._tick()
        
        return self.time

    def _tick(self) -> None:
        if not self.path:
            if self.pos == (self.carpark.north_entrance[0] - 1, self.carpark.north_entrance[1]):
                # go up a level
                self.current_level += 1
                self.pos = self.carpark.north_entrance
                self.direction = (1, 0) # south
                self.path = self._generate_path()
            elif self.pos == (self.carpark.south_entrance[0] + 1, self.carpark.south_entrance[1]):
                # go up a level
                self.current_level += 1
                self.pos = self.carpark.south_entrance
                self.direction = (-1, 0) # north
                self.path = self._generate_path()
            elif self.pos == (self.carpark.north_ramp[0] - 1, self.carpark.north_ramp[1]):
                # go down a level
                self.current_level -= 1
                self.pos = self.carpark.north_ramp
                self.direction = (1, 0) # south
                self.path = self._generate_path()
            elif self.pos == (self.carpark.south_ramp[0] + 1, self.carpark.south_ramp[1]):
                # go down a level
                self.current_level -= 1
                self.pos = self.carpark.south_ramp
                self.direction = (-1, 0) # north
                self.path = self._generate_path()
            else:
                # search complete
                self.completed = True
                return
            
        # continue along path
        next_pos = self.path.popleft()
        self.direction = (next_pos[0] - self.pos[0], next_pos[1] - self.pos[1])
        self.pos = next_pos
        
        # check for parking spaces within FOV
        parking_space = self._check_fov()
        if not self.pathing_to_park:
            if parking_space:
                self.path = self._calculate_path_to_park(parking_space)
                self.pathing_to_park = True
        
        self.time += 1

    @abstractmethod
    def _generate_path(self) -> None:
        """
        Generate a path for the current floor.
        """
        pass

    def reset(self) -> None:
        """
        Reset the driver to the initial state.
        """
        self.current_level = 0
        self.pos = self.carpark.south_entrance
        self.direction = (-1, 0)
        self.fov = []
        self.time = 0
        self.pathing_to_park = False
        self.completed = False
        self.path = self._generate_path()

    def display(self) -> None:
        path, fov = set(self.path), set(self.fov)
        grid = self.carpark.levels[self.current_level]
        n, m = len(grid), len(grid[0])
        print(f"┌{"─"*m*3}─┐")
        for i in range(n):
            s = "│"
            for j in range(m):
                s += " "
                if (i, j) == self.pos:
                    s += self._cur_pos_symbol
                elif (i, j) in fov and (grid[i][j] == CellType.OCCUPIED or grid[i][j] == CellType.UNOCCUPIED):
                    s += Style.colorize(self._display_map_uncolored[grid[i][j].value], "yellow")
                elif (i, j) in path:
                    s += Style.colorize(self._display_map_uncolored[grid[i][j].value], "blue")
                else:
                    s += self._display_map_colored[grid[i][j].value]
                s += " "
            s += " │"
            print(s)
        print(f"└{"─"*m*3}─┘")
        print(f"t = {self.time}{" "*(m*3-(3+len(str(self.time))))}L{self.current_level}")