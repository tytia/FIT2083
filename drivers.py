from driver_base import DriverBase
from parking import CellType
from collections import deque

class BottomUpDriver(DriverBase):
    """
    A driver that starts searching from the bottom up.
    """
    
    def __init__(self, carpark):
        super().__init__(carpark)

    def _generate_path(self):
        path = deque()
        reverse = self.pos == self.carpark.north_entrance
        grid = self.carpark.levels[self.current_level]
        _, m = len(grid), len(grid[0])
        
        for i in range(self.pos[0] + self.direction[0], len(grid) - 2 if self.direction[0] > 0 else 1, 3 * self.direction[0]):
            if not reverse:
                path.extend([(i, j) for j in range(1, m - 1)])
                path.extend([(k, m - 2) for k in range(i + 1 * self.direction[0], i + 3 * self.direction[0], self.direction[0])])
            else:
                path.extend([(i, j) for j in range(m - 2, 0, -1)])
                path.extend([(k, 1) for k in range(i + 1 * self.direction[0], i + 3 * self.direction[0], self.direction[0])])

            reverse = not reverse

        path.pop()
        if self.current_level != len(self.carpark.levels) - 1:
            if reverse != (self.pos == self.carpark.north_entrance):
                path.pop()
                if not reverse:
                    path.extend([(path[-1][0], j) for j in range(2, m - 1)])
                else:
                    path.extend([(path[-1][0], j) for j in range(m - 3, 0, -1)])
                reverse = not reverse
                path.append((path[-1][0] + 1 * self.direction[0], path[-1][1]))
            
            if not reverse:
                path.extend([(path[-1][0] + 1 * self.direction[0], j) for j in range(1, m - 1)])
            else:
                path.extend([(path[-1][0] + 1 * self.direction[0], j) for j in range(m - 2, 0, -1)])
        else:
            path.pop()
            
        return path
    

class TopDownDriver(DriverBase):
    """
    A driver that tries to reach the top as quickly as possible, then searches downwards.
    """
    
    def __init__(self, carpark):
        self.top_reached = False
        super().__init__(carpark)

    def _generate_path(self):
        if self.current_level == len(self.carpark.levels) - 1:
            self.top_reached = True

        path = deque()
        grid = self.carpark.levels[self.current_level]
        _, m = len(grid), len(grid[0])

        if not self.top_reached:
            path.extend([(self.pos[0] + self.direction[0], j) for j in range(1, m - 1)])
            path.append((self.pos[0], m - 2))
            path.extend([(self.pos[0] - self.direction[0], j) for j in range(m - 2, 0, -1)])
        else:
            reverse = self.pos == self.carpark.south_ramp
            for i in range(self.pos[0] + self.direction[0], len(grid) - 2 if self.direction[0] > 0 else 1, 3 * self.direction[0]):
                if not reverse:
                    path.extend([(i, j) for j in range(1, m - 1)])
                    path.extend([(k, m - 2) for k in range(i + 1 * self.direction[0], i + 3 * self.direction[0], self.direction[0])])
                else:
                    path.extend([(i, j) for j in range(m - 2, 0, -1)])
                    path.extend([(k, 1) for k in range(i + 1 * self.direction[0], i + 3 * self.direction[0], self.direction[0])])

                reverse = not reverse

            path.pop()
            if self.current_level != 0:
                if (reverse == (self.pos == self.carpark.south_ramp)) == (self.current_level == len(self.carpark.levels) - 1):
                    path.pop()
                    if not reverse:
                        path.extend([(path[-1][0], j) for j in range(2, m - 1)])
                    else:
                        path.extend([(path[-1][0], j) for j in range(m - 3, 0, -1)])
                    reverse = not reverse
                    path.append((path[-1][0] + 1 * self.direction[0], path[-1][1]))
                
                if not reverse:
                    path.extend([(path[-1][0] + 1 * self.direction[0], j) for j in range(1, m - 1)])
                else:
                    path.extend([(path[-1][0] + 1 * self.direction[0], j) for j in range(m - 2, 0, -1)])
            else:
                path.pop()
        
        return path
    
    def reset(self):
        self.top_reached = False
        super().reset()