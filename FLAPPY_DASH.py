"""
FLAPPY DASH
------------
An original Flappy-Bird-style game made with Python + Pygame only.
No external images or sounds are needed - everything is drawn with
Pygame shapes.

Controls:
    SPACE / Left Click / UP Arrow   - flap (jump up)
    ENTER                            - start / restart
    ESC                              - quit

Run:
    pip install pygame
    python flappy_dash.py
"""

import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 420, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Dash")
clock = pygame.time.Clock()
FPS = 60

FONT_BIG = pygame.font.SysFont("arial", 50, bold=True)
FONT_MED = pygame.font.SysFont("arial", 28, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 18, bold=True)

SKY_TOP = (110, 200, 250)
SKY_BOTTOM = (200, 235, 255)
GROUND_COLOR = (210, 180, 100)
GROUND_LINE = (170, 140, 70)
PIPE_COLOR = (60, 180, 90)
PIPE_DARK = (40, 140, 65)
BIRD_BODY = (255, 200, 50)
BIRD_WING = (230, 160, 30)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (220, 60, 60)
YELLOW = (250, 210, 60)

GROUND_HEIGHT = 90
GRAVITY = 0.45
FLAP_STRENGTH = -8.5
PIPE_GAP = 165
PIPE_WIDTH = 62
PIPE_SPEED = 3


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class Bird:
    def __init__(self):
        self.x = 90
        self.y = HEIGHT // 2
        self.radius = 16
        self.velocity = 0
        self.rotation = 0
        self.alive = True
        self.wing_flap = 0.0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.velocity = clamp(self.velocity, -12, 12)
        self.y += self.velocity

        self.rotation = clamp(-self.velocity * 4, -30, 70)
        self.wing_flap += 0.3

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.velocity = 0

        if self.y + self.radius >= HEIGHT - GROUND_HEIGHT:
            self.y = HEIGHT - GROUND_HEIGHT - self.radius
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                            self.radius * 2, self.radius * 2)

    def draw(self, surf):
        wing_offset = 4 * abs(pygame.math.Vector2(1, 0).rotate(self.wing_flap * 60).y)

        # body
        pygame.draw.circle(surf, BIRD_BODY, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), self.radius, 2)

        # wing (flapping animation)
        wing_y = self.y + wing_offset - 2
        pygame.draw.ellipse(surf, BIRD_WING,
                             (self.x - self.radius * 0.6, wing_y - 5, self.radius * 1.1, self.radius * 0.8))

        # eye
        pygame.draw.circle(surf, WHITE, (int(self.x + 5), int(self.y - 4)), 5)
        pygame.draw.circle(surf, BLACK, (int(self.x + 6), int(self.y - 4)), 2)

        # beak
        pygame.draw.polygon(surf, (255, 140, 40), [
            (self.x + self.radius - 2, self.y - 2),
            (self.x + self.radius + 10, self.y + 2),
            (self.x + self.radius - 2, self.y + 6),
        ])


class PipePair:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(140, HEIGHT - GROUND_HEIGHT - 140)
        self.passed = False
        self.width = PIPE_WIDTH

    def update(self):
        self.x -= PIPE_SPEED

    def off_screen(self):
        return self.x + self.width < 0

    def top_rect(self):
        return pygame.Rect(self.x, 0, self.width, self.gap_y - PIPE_GAP // 2)

    def bottom_rect(self):
        top_h = self.gap_y - PIPE_GAP // 2
        bottom_y = self.gap_y + PIPE_GAP // 2
        return pygame.Rect(self.x, bottom_y, self.width, HEIGHT - GROUND_HEIGHT - bottom_y)

    def draw(self, surf):
        top = self.top_rect()
        bottom = self.bottom_rect()

        pygame.draw.rect(surf, PIPE_COLOR, top)
        pygame.draw.rect(surf, PIPE_DARK, top, 3)
        pygame.draw.rect(surf, PIPE_COLOR, (top.x - 5, top.height - 24, top.width + 10, 24))
        pygame.draw.rect(surf, PIPE_DARK, (top.x - 5, top.height - 24, top.width + 10, 24), 3)

        pygame.draw.rect(surf, PIPE_COLOR, bottom)
        pygame.draw.rect(surf, PIPE_DARK, bottom, 3)
        pygame.draw.rect(surf, PIPE_COLOR, (bottom.x - 5, bottom.y, bottom.width + 10, 24))
        pygame.draw.rect(surf, PIPE_DARK, (bottom.x - 5, bottom.y, bottom.width + 10, 24), 3)


def draw_background(scroll):
    for i in range(HEIGHT - GROUND_HEIGHT):
        t = i / (HEIGHT - GROUND_HEIGHT)
        c = (
            int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t),
            int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t),
            int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t),
        )
        pygame.draw.line(screen, c, (0, i), (WIDTH, i))

    for cx, cy in [(60, 100), (250, 70), (350, 140)]:
        cx = (cx - scroll * 0.3) % (WIDTH + 100) - 50
        for dx, dy, r in [(0, 0, 22), (18, 6, 16), (-18, 6, 16)]:
            pygame.draw.circle(screen, WHITE, (int(cx + dx), int(cy + dy)), r)

    ground_y = HEIGHT - GROUND_HEIGHT
    pygame.draw.rect(screen, GROUND_COLOR, (0, ground_y, WIDTH, GROUND_HEIGHT))
    pygame.draw.rect(screen, GROUND_LINE, (0, ground_y, WIDTH, 6))

    stripe_offset = int(scroll) % 30
    for x in range(-30 + stripe_offset, WIDTH, 30):
        pygame.draw.line(screen, GROUND_LINE, (x, ground_y + 20), (x + 15, ground_y + 20), 4)


def draw_center_text(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(surf, rect)


def draw_menu(best_score):
    draw_center_text("FLAPPY DASH", FONT_BIG, WHITE, HEIGHT // 2 - 160)
    draw_center_text("Press ENTER to Start", FONT_MED, WHITE, HEIGHT // 2 - 80)
    draw_center_text("SPACE / Click / UP - Flap", FONT_SMALL, BLACK, HEIGHT // 2 - 30)
    if best_score > 0:
        draw_center_text(f"Best Score: {best_score}", FONT_SMALL, (255, 230, 0), HEIGHT // 2 + 10)


def draw_game_over(score, best_score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    draw_center_text("GAME OVER", FONT_BIG, RED, HEIGHT // 2 - 80)
    draw_center_text(f"Score: {score}", FONT_MED, WHITE, HEIGHT // 2 - 20)
    draw_center_text(f"Best: {best_score}", FONT_SMALL, YELLOW, HEIGHT // 2 + 15)
    draw_center_text("Press ENTER to Restart", FONT_SMALL, WHITE, HEIGHT // 2 + 55)


def draw_score(score):
    text = FONT_BIG.render(str(score), True, WHITE)
    shadow = FONT_BIG.render(str(score), True, BLACK)
    rect = text.get_rect(center=(WIDTH // 2, 60))
    screen.blit(shadow, rect.move(2, 2))
    screen.blit(text, rect)


def reset():
    global bird, pipes, score, spawn_timer, scroll, game_state
    bird = Bird()
    pipes = [PipePair(WIDTH + 100)]
    score = 0
    spawn_timer = 0
    scroll = 0
    game_state = "PLAYING"


bird = Bird()
pipes = [PipePair(WIDTH + 100)]
score = 0
best_score = 0
spawn_timer = 0
scroll = 0
game_state = "MENU"


def main():
    global game_state, best_score, spawn_timer, scroll, score

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            flap_pressed = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    flap_pressed = True
                if event.key == pygame.K_RETURN:
                    if game_state in ("MENU", "GAME_OVER"):
                        reset()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                flap_pressed = True

            if flap_pressed and game_state == "PLAYING":
                bird.flap()

        if game_state == "PLAYING":
            bird.update()
            scroll += PIPE_SPEED

            for pipe in pipes:
                pipe.update()
            pipes[:] = [p for p in pipes if not p.off_screen()]

            spawn_timer += 1
            if spawn_timer > 95:
                spawn_timer = 0
                pipes.append(PipePair(WIDTH + 40))

            for pipe in pipes:
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1

                if bird.get_rect().colliderect(pipe.top_rect()) or \
                   bird.get_rect().colliderect(pipe.bottom_rect()):
                    bird.alive = False

            if not bird.alive:
                best_score = max(best_score, score)
                game_state = "GAME_OVER"

        draw_background(scroll)

        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)

        if game_state == "PLAYING":
            draw_score(score)
        elif game_state == "MENU":
            draw_menu(best_score)
        elif game_state == "GAME_OVER":
            draw_score(score)
            draw_game_over(score, best_score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()