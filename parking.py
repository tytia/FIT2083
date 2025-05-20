from enum import Enum
from numpy import random
from typing import List

class CellType(Enum):
    ROAD = 0
    RAMP = 1
    UNOCCUPIED = 2
    OCCUPIED = 3
    VOID = 4

class MultiLevelCarPark:
    def __init__(self, levels: int, rows: int, cols: int) -> None:
        self.levels = self._construct_carpark(levels, rows, cols)
        self.length = len(self.levels[0])
        self.width = len(self.levels[0][0])
        self.south_entrance = (self.length - 2, 1)
        self.north_entrance = (1, self.width-2)

        self.parking_cells = []
        for i, row in enumerate(self.levels[-1]):
            for j, cell in enumerate(row):
                if cell == CellType.OCCUPIED:
                    self.parking_cells.append((i, j))

    def _construct_carpark(self, levels: int, rows: int, cols: int) -> List[List[List[CellType]]]:
        carpark = []
        for _ in range(levels):
            level = [
                [CellType.VOID] + [CellType.RAMP] * cols + [CellType.VOID],
                [CellType.OCCUPIED, CellType.ROAD] + [CellType.OCCUPIED] * (cols - 2) + [CellType.ROAD, CellType.OCCUPIED]
            ]
            for _ in range(rows // 2 - 1):
                level += [
                    [CellType.OCCUPIED] + [CellType.ROAD] * cols + [CellType.OCCUPIED],
                    [CellType.OCCUPIED, CellType.ROAD] + [CellType.OCCUPIED] * (cols - 2) + [CellType.ROAD, CellType.OCCUPIED],
                    [CellType.OCCUPIED, CellType.ROAD] + [CellType.OCCUPIED] * (cols - 2) + [CellType.ROAD, CellType.OCCUPIED]
                ]
            level += [
                [CellType.OCCUPIED] + [CellType.ROAD] * cols + [CellType.OCCUPIED],
                [CellType.OCCUPIED, CellType.ROAD] + [CellType.OCCUPIED] * (cols - 2) + [CellType.ROAD, CellType.OCCUPIED],
                [CellType.VOID] + [CellType.RAMP] * cols + [CellType.VOID]
            ]
            carpark.append(level)

        carpark[-1][1][1] = CellType.OCCUPIED
        carpark[-1][-2][-2] = CellType.OCCUPIED
        
        return carpark
    
    def set_capacity(self, capacity: float, seed: int = 0) -> None:
        self.reset_capacity()
        random.seed(seed)
        visited = [set([1, len(self.parking_cells) - 2]) for _ in range(len(self.levels) - 1)] + [set()]
        unnoccupied_count = round((1.0 - capacity) * len(self.parking_cells))
        for _ in range(unnoccupied_count):
            # randomly select a level, favoring the top levels
            k = max(0, len(self.levels) - 1 - round(abs(random.normal(0, len(self.levels) / 3))))
            # randomly select a cell in the level, favoring the middle rows
            c = max(0, min(round(random.normal(len(self.parking_cells) / 2, len(self.parking_cells) / 4)), len(self.parking_cells) - 1))
            # check if the cell is already unoccupied - if it is, linearly search for the next unoccupied cell
            l, r = c - 1, c + 1
            while c in visited[k]:
                if l not in visited[k]:
                    c = l
                    break
                if r not in visited[k]:
                    c = r
                    break
                l = (l - 1) % len(self.parking_cells)
                r = (r + 1) % len(self.parking_cells)

            i, j = self.parking_cells[c]
            self.levels[k][i][j] = CellType.UNOCCUPIED
            visited[k].add(c)
    
    def reset_capacity(self) -> None:
        for level in self.levels:
            for row in level:
                for i in range(len(row)):
                    if row[i] == CellType.UNOCCUPIED:
                        row[i] = CellType.OCCUPIED
    

if __name__ == "__main__":
    carpark = MultiLevelCarPark(3, 6, 10)
    for level in carpark.levels:
        for row in level:
            print(" ".join([cell.name[0] for cell in row]))
        print()

    # carpark.set_capacity(0.8)

    # for level in carpark.levels:
    #     for row in level:
    #         print(" ".join([cell.name[0] for cell in row]))
    #     print()
