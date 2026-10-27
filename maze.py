"""Генерация лабиринта DFS. Без зависимостей от pygame/telegram."""
from random import choice


class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False

    def check_cell(self, x, y, grid, cols, rows):
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid[x + y * cols]

    def check_neighbours(self, grid, cols, rows):
        ns = []
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            n = self.check_cell(self.x + dx, self.y + dy, grid, cols, rows)
            if n and not n.visited:
                ns.append(n)
        return choice(ns) if ns else False


def remove_walls(a, b):
    dx, dy = a.x - b.x, a.y - b.y
    if dx == 1: a.walls["left"] = b.walls["right"] = False
    elif dx == -1: a.walls["right"] = b.walls["left"] = False
    if dy == 1: a.walls["top"] = b.walls["bottom"] = False
    elif dy == -1: a.walls["bottom"] = b.walls["top"] = False


def check_wall(grid, x, y, cols):
    if x % 2 == 0 and y % 2 == 0: return False
    if x % 2 == 1 and y % 2 == 1: return True
    if x % 2 == 0:
        return grid[x // 2 + ((y - 1) // 2) * cols].walls["bottom"]
    return grid[(x - 1) // 2 + (y // 2) * cols].walls["right"]


def generate_maze(cols, rows):
    grid = [Cell(x, y) for y in range(rows) for x in range(cols)]
    cur = grid[0]
    cur.visited = True
    stack = []
    while True:
        n = cur.check_neighbours(grid, cols, rows)
        if n:
            n.visited = True
            remove_walls(cur, n)
            stack.append(cur)
            cur = n
        elif stack:
            cur = stack.pop()
        else:
            break
    return grid
