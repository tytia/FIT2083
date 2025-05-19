from typing import List, Tuple

# horizontal ─
# vertial │
# top-left corner ┌
# top-right corner ┐
# bottom-left corner └
# bottom-right corner ┘
# path #
# road ◇
# car ◈
# occupied ▣
# free ▢

def print_grid(grid: List[List[str]], pos: Tuple[int, int]) -> None:
    n, m = len(grid), len(grid[0])
    print(f"┌{"─"*n*3}─┐")
    for i in range(n):
        s = "│"
        for j in range(m):
            s += " "
            s += grid[i][j] if (i, j) != pos else "◈"
            s += " "
        s += " │"
        print(s)
    print(f"└{"─"*n*3}─┘")


if __name__ == "__main__":
    print_grid([
        [" ", "◇", "▣", "▣", "▢"],
        [" ", "◇", "▣", "▢", "▣"],
        ["◇", "◇", "◇", "◇", "◇"],
        [" ", "◇", " ", " ", " "],
        [" ", "◇", " ", " ", " "],
    ], (2, 1))