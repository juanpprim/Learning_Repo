"""Pygame starter: window, game loop, one movable sprite.

Run with:
    python src/main.py
"""
import pygame

WIDTH, HEIGHT = 640, 480
FPS = 60
PLAYER_SPEED = 300  # pixels per second


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((70, 130, 180))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.pos = pygame.Vector2(self.rect.center)

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        direction = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_s] - keys[pygame.K_w],
        )
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.pos += direction * PLAYER_SPEED * dt
        self.rect.center = self.pos


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("pygame starter")
    clock = pygame.time.Clock()

    player = Player()
    sprites = pygame.sprite.Group(player)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # seconds since last frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        sprites.update(dt, keys)

        screen.fill((20, 20, 30))
        sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
