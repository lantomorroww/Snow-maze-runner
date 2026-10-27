import maze

def test_size(): assert len(maze.generate_maze(5, 5)) == 25
def test_visited(): assert all(c.visited for c in maze.generate_maze(6, 6))
def test_passage(): assert all(sum(1 for w in c.walls.values() if not w) >= 1 for c in maze.generate_maze(5, 5))
def test_remove_h():
    a, b = maze.Cell(0, 0), maze.Cell(1, 0); maze.remove_walls(a, b)
    assert a.walls["right"] is False and b.walls["left"] is False
def test_remove_v():
    a, b = maze.Cell(0, 0), maze.Cell(0, 1); maze.remove_walls(a, b)
    assert a.walls["bottom"] is False and b.walls["top"] is False
