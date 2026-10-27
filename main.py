"""Локальная игра. Управление: стрелки."""
import pygame
from game import HEIGHT, WIDTH, Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snow Maze Runner")
    clock = pygame.time.Clock()
    game = Game()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP: game.move("up")
                elif e.key == pygame.K_DOWN: game.move("down")
                elif e.key == pygame.K_LEFT: game.move("left")
                elif e.key == pygame.K_RIGHT: game.move("right")
        game.draw(screen)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
