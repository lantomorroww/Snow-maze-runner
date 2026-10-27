"""Общая логика игры + чистая should_record_loss."""
import io
import threading

import pygame

from maze import generate_maze

WIDTH, HEIGHT, TILE = 750, 750, 50
SNOW_WHITE = (240, 255, 255)
ICE_BLUE = (200, 230, 255)

_lock = threading.Lock()
_init = False


def _ensure():
    global _init
    with _lock:
        if _init: return
        pygame.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1))
        _init = True


def _load(path, size, alpha=False):
    try:
        s = pygame.image.load(path)
        s = s.convert_alpha() if alpha else s.convert()
        return pygame.transform.scale(s, size)
    except (pygame.error, FileNotFoundError):
        s = pygame.Surface(size)
        s.fill((60, 120, 200) if alpha else (20, 30, 60))
        return s


def should_record_loss(game, won_this_game, first_move_ts):
    """True если: игра есть, не побеждена, был хотя бы один ход."""
    if game is None: return False
    if won_this_game: return False
    if first_move_ts is None: return False
    return True


class Game:
    def __init__(self):
        _ensure()
        self.cols = (WIDTH // TILE + 1) // 2
        self.rows = (HEIGHT // TILE + 1) // 2
        self.grid = generate_maze(self.cols, self.rows)
        self.player_x = TILE // 2
        self.player_y = TILE // 2
        self.player_speed = TILE // 2
        self.moves = 0
        self._bg = _load("images/background_1.png", (WIDTH, HEIGHT))
        self._pl = _load("images/char.png", (TILE + 30, TILE + 30), alpha=True)

    def move(self, direction):
        gx = (self.player_x + TILE // 2) // (2 * TILE)
        gy = (self.player_y + TILE // 2) // (2 * TILE)
        if not (0 <= gx < self.cols and 0 <= gy < self.rows):
            return False
        c = self.grid[gx + gy * self.cols]
        moved = False
        if direction == "up" and not c.walls["top"]:
            self.player_y = max(self.player_y - self.player_speed, 0); moved = True
        elif direction == "down" and not c.walls["bottom"]:
            self.player_y = min(self.player_y + self.player_speed, HEIGHT - TILE); moved = True
        elif direction == "left" and not c.walls["left"]:
            self.player_x = max(self.player_x - self.player_speed, 0); moved = True
        elif direction == "right" and not c.walls["right"]:
            self.player_x = min(self.player_x + self.player_speed, WIDTH - TILE); moved = True
        if moved: self.moves += 1
        return moved

    def is_won(self):
        gx = (self.player_x + TILE // 2) // (2 * TILE)
        gy = (self.player_y + TILE // 2) // (2 * TILE)
        return gx == self.cols - 1 and gy == self.rows - 1

    def _cell(self, surface, c):
        x, y = 2 * c.x * TILE, 2 * c.y * TILE
        if c.visited: pygame.draw.rect(surface, SNOW_WHITE, (x, y, TILE, TILE))
        if not c.walls["top"]: pygame.draw.rect(surface, ICE_BLUE, (x, y - TILE, TILE, TILE))
        if not c.walls["right"]: pygame.draw.rect(surface, ICE_BLUE, (x + TILE, y, TILE, TILE))
        if not c.walls["bottom"]: pygame.draw.rect(surface, ICE_BLUE, (x, y + TILE, TILE, TILE))
        if not c.walls["left"]: pygame.draw.rect(surface, ICE_BLUE, (x - TILE, y, TILE, TILE))

    def draw(self, surface):
        surface.blit(self._bg, (0, 0))
        for c in self.grid: self._cell(surface, c)
        surface.blit(self._pl, (self.player_x - 15, self.player_y - 15))

    def render(self):
        s = pygame.Surface((WIDTH, HEIGHT))
        self.draw(s)
        buf = io.BytesIO()
        pygame.image.save(s, buf, "PNG")
        return buf.getvalue()
