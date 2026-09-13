import pygame
import random
import math
import sys

pygame.init()

# ---------------- CONSTANTS ----------------
WIDTH, HEIGHT = 720, 1280
FPS = 60

WHITE = (255, 255, 255)
BLACK = (10, 5, 15)
RED = (220, 40, 40)
DARK_RED = (150, 20, 20)
TEAL = (60, 200, 190)
DARK_TEAL = (30, 140, 130)
PURPLE = (190, 70, 190)
YELLOW = (255, 200, 40)
ORANGE = (255, 140, 30)
CYAN = (80, 230, 220)
GREEN = (60, 200, 120)
BG_PURPLE = (40, 10, 35)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Chicken Attack")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont("arial", 64, bold=True)
font_mid = pygame.font.SysFont("arial", 40, bold=True)
font_small = pygame.font.SysFont("arial", 28)

# ---------------- BACKGROUND STARS ----------------
stars = []
for _ in range(120):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)])


def draw_background():
    screen.fill(BG_PURPLE)
    for s in stars:
        pygame.draw.circle(screen, (200, 180, 220), (s[0], s[1]), s[2])
        s[1] += s[2]
        if s[1] > HEIGHT:
            s[1] = 0
            s[0] = random.randint(0, WIDTH)


# ---------------- DRAW HELPERS ----------------
def draw_wing(surf, cx, cy, side, color):
    """side = -1 (left) or 1 (right)"""
    points = [
        (cx, cy),
        (cx + side * 34, cy - 14),
        (cx + side * 40, cy + 4),
        (cx + side * 18, cy + 14),
    ]
    pygame.draw.polygon(surf, WHITE, points)
    pygame.draw.polygon(surf, color, points, 2)


def draw_chick(surf, x, y, body_color, wing_color, boss=False):
    """A small chicken-alien enemy, centered at (x,y)."""
    r = 26 if not boss else 34
    # wings
    draw_wing(surf, x, y, -1, wing_color)
    draw_wing(surf, x, y, 1, wing_color)
    # body
    pygame.draw.circle(surf, body_color, (x, y + 4), r)
    # belly/vest
    if boss:
        pygame.draw.ellipse(surf, RED, (x - 16, y - 4, 32, 30))
        txt = font_small.render("Z", True, WHITE)
        surf.blit(txt, (x - txt.get_width() // 2, y + 2))
    else:
        pygame.draw.circle(surf, ORANGE if body_color != PURPLE else PURPLE, (x, y + 8), r - 10)
    # head crest
    pygame.draw.polygon(surf, RED, [(x - 6, y - r), (x + 6, y - r), (x, y - r - 14)])
    # eyes (goggles)
    pygame.draw.circle(surf, (30, 30, 40), (x - 9, y - 4), 8)
    pygame.draw.circle(surf, (30, 30, 40), (x + 9, y - 4), 8)
    pygame.draw.circle(surf, CYAN, (x - 9, y - 4), 4)
    pygame.draw.circle(surf, CYAN, (x + 9, y - 4), 4)
    # feet
    pygame.draw.line(surf, ORANGE, (x - 8, y + r), (x - 8, y + r + 10), 3)
    pygame.draw.line(surf, ORANGE, (x + 8, y + r), (x + 8, y + r + 10), 3)


def draw_player(surf, x, y):
    # engine flames
    pygame.draw.polygon(surf, YELLOW, [(x - 26, y + 55), (x - 14, y + 55), (x - 20, y + 90)])
    pygame.draw.polygon(surf, ORANGE, [(x - 26, y + 55), (x - 14, y + 55), (x - 20, y + 80)])
    pygame.draw.polygon(surf, YELLOW, [(x + 14, y + 55), (x + 26, y + 55), (x + 20, y + 90)])
    pygame.draw.polygon(surf, ORANGE, [(x + 14, y + 55), (x + 26, y + 55), (x + 20, y + 80)])

    # body (ship)
    pygame.draw.polygon(surf, GREEN, [(x, y - 70), (x - 45, y + 40), (x - 15, y + 30),
                                        (x, y + 45), (x + 15, y + 30), (x + 45, y + 40)])
    pygame.draw.polygon(surf, DARK_TEAL, [(x, y - 70), (x - 45, y + 40), (x - 15, y + 30),
                                            (x, y + 45), (x + 15, y + 30), (x + 45, y + 40)], 3)
    # cockpit
    pygame.draw.ellipse(surf, ORANGE, (x - 12, y - 30, 24, 34))
    # engines
    pygame.draw.rect(surf, (90, 90, 100), (x - 32, y + 30, 20, 30), border_radius=6)
    pygame.draw.rect(surf, (90, 90, 100), (x + 12, y + 30, 20, 30), border_radius=6)
    # wing tips glow
    pygame.draw.line(surf, YELLOW, (x - 45, y + 40), (x - 60, y + 10), 3)
    pygame.draw.line(surf, YELLOW, (x + 45, y + 40), (x + 60, y + 10), 3)


def draw_bullet(surf, x, y):
    pygame.draw.polygon(surf, CYAN, [(x, y), (x - 6, y + 20), (x, y + 14), (x + 6, y + 20)])


def draw_egg(surf, x, y):
    pygame.draw.ellipse(surf, (250, 250, 240), (x - 12, y - 16, 24, 32))
    pygame.draw.ellipse(surf, (210, 210, 200), (x - 12, y - 16, 24, 32), 2)


def draw_explosion(surf, x, y, radius):
    for i in range(8):
        ang = i * (math.pi / 4)
        ex = x + math.cos(ang) * radius
        ey = y + math.sin(ang) * radius
        pygame.draw.circle(surf, YELLOW, (int(ex), int(ey)), max(2, radius // 3))
    pygame.draw.circle(surf, ORANGE, (x, y), radius)
    pygame.draw.circle(surf, YELLOW, (x, y), max(2, radius - 8))


# ---------------- ENEMY CLASS ----------------
class Enemy:
    def __init__(self, x, y, row_type):
        self.x = x
        self.y = y
        self.row_type = row_type  # "teal", "purple", "red", "boss"
        self.alive = True
        self.hp = 3 if row_type == "boss" else 1

    def draw(self, surf):
        if self.row_type == "teal":
            draw_chick(surf, self.x, self.y, TEAL, TEAL)
        elif self.row_type == "purple":
            draw_chick(surf, self.x, self.y, TEAL, PURPLE)
        elif self.row_type == "red":
            draw_chick(surf, self.x, self.y, RED, WHITE)
        elif self.row_type == "boss":
            draw_chick(surf, self.x, self.y, WHITE, WHITE, boss=True)

    def rect(self):
        r = 40 if self.row_type == "boss" else 32
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)


# ---------------- GAME SETUP ----------------
def build_formation():
    enemies = []
    rows = [
        ("teal", 7),
        ("purple_boss", 7),
        ("red", 7),
        ("red2", 7),
    ]
    start_y = 200
    spacing_x = 88
    spacing_y = 90
    start_x = (WIDTH - (7 - 1) * spacing_x) // 2

    # Row 0: teal
    for i in range(7):
        enemies.append(Enemy(start_x + i * spacing_x, start_y, "teal"))

    # Row 1: purple with two boss chickens in middle-ish positions
    row1_y = start_y + spacing_y
    for i in range(7):
        if i == 1 or i == 4:
            enemies.append(Enemy(start_x + i * spacing_x, row1_y, "boss"))
        else:
            enemies.append(Enemy(start_x + i * spacing_x, row1_y, "purple"))

    # Row 2: red
    row2_y = row1_y + spacing_y
    for i in range(7):
        enemies.append(Enemy(start_x + i * spacing_x, row2_y, "red"))

    # Row 3: red (partial like screenshot)
    row3_y = row2_y + spacing_y
    for i in range(7):
        enemies.append(Enemy(start_x + i * spacing_x, row3_y, "red"))

    return enemies


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 160
        self.player_speed = 8
        self.bullets = []
        self.enemy_bullets = []  # eggs
        self.enemies = build_formation()
        self.explosions = []
        self.score = 0
        self.lives = 3
        self.energy = 1.0  # circular meter bottom-left
        self.direction = 1
        self.move_timer = 0
        self.shoot_cooldown = 0
        self.enemy_shoot_cooldown = 60
        self.game_over = False
        self.win = False

    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.bullets.append([self.player_x - 18, self.player_y - 50])
            self.bullets.append([self.player_x + 18, self.player_y - 50])
            self.shoot_cooldown = 12

    def update(self, keys):
        if self.game_over:
            return

        # player movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= self.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += self.player_speed
        self.player_x = max(50, min(WIDTH - 50, self.player_x))

        if keys[pygame.K_SPACE]:
            self.shoot()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # bullets move
        for b in self.bullets:
            b[1] -= 14
        self.bullets = [b for b in self.bullets if b[1] > -20]

        # eggs move
        for e in self.enemy_bullets:
            e[1] += 6
        self.enemy_bullets = [e for e in self.enemy_bullets if e[1] < HEIGHT + 20]

        # enemy formation movement
        self.move_timer += 1
        move_every = max(6, 20 - self.score // 200)
        if self.move_timer >= move_every:
            self.move_timer = 0
            edge_hit = False
            for en in self.enemies:
                if not en.alive:
                    continue
                if en.x + 20 * self.direction > WIDTH - 30 or en.x + 20 * self.direction < 30:
                    edge_hit = True
            for en in self.enemies:
                if not en.alive:
                    continue
                en.x += 14 * self.direction
                if edge_hit:
                    en.y += 22
            if edge_hit:
                self.direction *= -1

        # enemy shooting
        self.enemy_shoot_cooldown -= 1
        if self.enemy_shoot_cooldown <= 0:
            alive_enemies = [en for en in self.enemies if en.alive]
            if alive_enemies:
                shooter = random.choice(alive_enemies)
                self.enemy_bullets.append([shooter.x, shooter.y + 30])
            self.enemy_shoot_cooldown = max(20, 70 - self.score // 100)

        # collisions: player bullets vs enemies
        for b in self.bullets[:]:
            brect = pygame.Rect(b[0] - 6, b[1] - 10, 12, 20)
            for en in self.enemies:
                if en.alive and en.rect().colliderect(brect):
                    en.hp -= 1
                    if b in self.bullets:
                        self.bullets.remove(b)
                     if en.hp