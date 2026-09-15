"""
EGG INVADERS
-------------
An original Space-Invaders style shooter made with Python + Pygame only.
All graphics are drawn using Pygame shapes - no external images, sounds,
or fonts are used.

Install:
    pip install pygame

Run:
    python egg_invaders.py

Controls:
    LEFT / A / RIGHT / D  - move the ship
    SPACE                 - shoot
    ENTER                 - start / restart
    ESC                   - pause / resume
"""

import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 480, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Egg Invaders")
clock = pygame.time.Clock()
FPS = 60

FONT_BIG = pygame.font.SysFont("arial", 54, bold=True)
FONT_MED = pygame.font.SysFont("arial", 30, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 20, bold=True)
FONT_TINY = pygame.font.SysFont("arial", 15)

BG_TOP = (18, 10, 35)
BG_BOTTOM = (60, 20, 60)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
RED = (230, 60, 60)
YELLOW = (250, 220, 80)
GREEN = (90, 220, 140)
CYAN = (110, 220, 220)
PURPLE = (190, 120, 230)
ORANGE = (250, 160, 60)
GRAY = (150, 150, 160)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


# --------------------------------------------------------------------------
# STARFIELD BACKGROUND
# --------------------------------------------------------------------------
stars = [
    [random.uniform(0, WIDTH), random.uniform(0, HEIGHT), random.uniform(30, 120), random.uniform(1, 3)]
    for _ in range(90)
]


def update_stars(dt):
    for s in stars:
        s[1] += s[2] * dt
        if s[1] > HEIGHT:
            s[1] = 0
            s[0] = random.uniform(0, WIDTH)


def draw_background():
    for i in range(HEIGHT):
        t = i / HEIGHT
        c = (
            int(lerp(BG_TOP[0], BG_BOTTOM[0], t)),
            int(lerp(BG_TOP[1], BG_BOTTOM[1], t)),
            int(lerp(BG_TOP[2], BG_BOTTOM[2], t)),
        )
        pygame.draw.line(screen, c, (0, i), (WIDTH, i))

    for x, y, speed, size in stars:
        shade = clamp(int(150 + speed), 150, 255)
        pygame.draw.circle(screen, (shade, shade, shade), (int(x), int(y)), int(size))


# --------------------------------------------------------------------------
# PARTICLES
# --------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color, speed=140, life=0.5, size=4):
        angle = random.uniform(0, math.tau)
        spd = random.uniform(speed * 0.3, speed)
        self.x, self.y = x, y
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        t = clamp(self.life / self.max_life, 0, 1)
        size = max(1, int(self.size * t))
        alpha = int(255 * t)
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
        surf.blit(s, (self.x - size, self.y - size))


particles = []


def spawn_burst(x, y, color, n=20, speed=160, life=0.5):
    for _ in range(n):
        particles.append(Particle(x, y, color, speed=speed, life=life, size=random.uniform(3, 6)))


# --------------------------------------------------------------------------
# FLOATING SCORE TEXT
# --------------------------------------------------------------------------
class FloatingText:
    def __init__(self, x, y, text, color=YELLOW):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = 0.7
        self.max_life = 0.7

    def update(self, dt):
        self.y -= 35 * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        t = clamp(self.life / self.max_life, 0, 1)
        base = FONT_TINY.render(self.text, True, self.color)
        base.set_alpha(int(255 * t))
        surf.blit(base, base.get_rect(center=(self.x, self.y)))


floating_texts = []


# --------------------------------------------------------------------------
# PLAYER SHIP
# --------------------------------------------------------------------------
class Ship:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT - 80
        self.width = 46
        self.height = 40
        self.speed = 320
        self.lives = 3
        self.shoot_cooldown = 0.0
        self.base_cooldown = 0.32
        self.hit_flash = 0.0
        self.thruster_flicker = 0.0

    def update(self, dt, keys):
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1
        self.x += move * self.speed * dt
        self.x = clamp(self.x, self.width / 2, WIDTH - self.width / 2)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        self.thruster_flicker += dt * 20

    def try_shoot(self):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.base_cooldown
            player_bullets.append(PlayerBullet(self.x, self.y - self.height / 2))
            spawn_burst(self.x, self.y - self.height / 2, CYAN, n=5, speed=80, life=0.12)

    def take_hit(self):
        self.lives -= 1
        self.hit_flash = 0.3
        spawn_burst(self.x, self.y, RED, n=18, speed=170)

    def get_rect(self):
        return pygame.Rect(self.x - self.width / 2, self.y - self.height / 2, self.width, self.height)

    def draw(self, surf):
        flash = self.hit_flash > 0 and int(self.hit_flash * 20) % 2 == 0
        body_color = RED if flash else GREEN

        # thruster flame (animated flicker)
        flame_h = 14 + math.sin(self.thruster_flicker) * 5
        pygame.draw.polygon(surf, ORANGE, [
            (self.x - 8, self.y + self.height / 2),
            (self.x + 8, self.y + self.height / 2),
            (self.x, self.y + self.height / 2 + flame_h),
        ])
        pygame.draw.polygon(surf, YELLOW, [
            (self.x - 4, self.y + self.height / 2),
            (self.x + 4, self.y + self.height / 2),
            (self.x, self.y + self.height / 2 + flame_h * 0.6),
        ])

        # ship body (triangle-ish fighter jet shape)
        pygame.draw.polygon(surf, body_color, [
            (self.x, self.y - self.height / 2),
            (self.x - self.width / 2, self.y + self.height / 2),
            (self.x - self.width / 4, self.y + self.height / 3),
            (self.x, self.y + self.height / 4),
            (self.x + self.width / 4, self.y + self.height / 3),
            (self.x + self.width / 2, self.y + self.height / 2),
        ])
        # cockpit
        pygame.draw.circle(surf, CYAN, (int(self.x), int(self.y - 4)), 7)
        # wing tips
        pygame.draw.circle(surf, WHITE, (int(self.x - self.width / 2), int(self.y + self.height / 2)), 4)
        pygame.draw.circle(surf, WHITE, (int(self.x + self.width / 2), int(self.y + self.height / 2)), 4)


ship = Ship()


# --------------------------------------------------------------------------
# BULLETS
# --------------------------------------------------------------------------
class PlayerBullet:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 620
        self.radius = 5
        self.alive = True

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < -20:
            self.alive = False
        return self.alive

    def draw(self, surf):
        pygame.draw.line(surf, CYAN, (self.x, self.y - 8), (self.x, self.y + 8), 4)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y - 8)), 3)


class Egg:
    """The enemy's projectile - dropped from a random chicken."""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = random.uniform(180, 260)
        self.radius = 7
        self.wobble = random.uniform(0, math.tau)
        self.alive = True

    def update(self, dt):
        self.wobble += dt * 6
        self.x += math.sin(self.wobble) * 20 * dt
        self.y += self.speed * dt
        if self.y > HEIGHT + 20:
            self.alive = False
        return self.alive

    def draw(self, surf):
        pygame.draw.ellipse(surf, (240, 235, 210), (self.x - self.radius * 0.75, self.y - self.radius,
                                                      self.radius * 1.5, self.radius * 2))
        pygame.draw.ellipse(surf, WHITE, (self.x - self.radius * 0.4, self.y - self.radius * 0.6,
                                           self.radius * 0.6, self.radius * 0.8))


player_bullets = []
eggs = []


# --------------------------------------------------------------------------
# ENEMY CHICKENS (grid formation, Space-Invaders style)
# --------------------------------------------------------------------------
ENEMY_TYPES = {
    "small":  {"hp": 1, "points": 10, "color": (255, 235, 210), "radius": 16},
    "medium": {"hp": 2, "points": 20, "color": (255, 200, 150), "radius": 19},
    "elite":  {"hp": 4, "points": 40, "color": (230, 80, 90), "radius": 22},
}


class EnemyChicken:
    def __init__(self, col, row, kind):
        self.col, self.row = col, row
        data = ENEMY_TYPES[kind]
        self.kind = kind
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.points = data["points"]
        self.color = data["color"]
        self.radius = data["radius"]
        self.wobble = random.uniform(0, math.tau)
        self.alive = True
        self.offset_x = 0.0
        self.offset_y = 0.0

    def get_pos(self, formation_x, formation_y, spacing_x, spacing_y):
        return (formation_x + self.col * spacing_x + self.offset_x,
                formation_y + self.row * spacing_y + self.offset_y)

    def draw(self, surf, x, y):
        self.wobble += 0.12
        flap = math.sin(self.wobble) * 5

        # wings
        pygame.draw.ellipse(surf, darken(self.color, 25),
                             (x - self.radius - 6, y - 4 + flap, self.radius * 0.8, self.radius * 0.55))
        pygame.draw.ellipse(surf, darken(self.color, 25),
                             (x + self.radius - self.radius * 0.2, y - 4 - flap,
                              self.radius * 0.8, self.radius * 0.55))

        # body
        pygame.draw.circle(surf, self.color, (int(x), int(y)), self.radius)

        # comb
        pygame.draw.circle(surf, RED, (int(x - 3), int(y - self.radius)), max(2, int(self.radius * 0.2)))
        pygame.draw.circle(surf, RED, (int(x + 3), int(y - self.radius)), max(2, int(self.radius * 0.2)))

        # eyes
        pygame.draw.circle(surf, BLACK, (int(x - 6), int(y - 2)), max(2, int(self.radius * 0.12)))
        pygame.draw.circle(surf, BLACK, (int(x + 6), int(y - 2)), max(2, int(self.radius * 0.12)))

        # beak
        pygame.draw.polygon(surf, ORANGE, [
            (x - 4, y + 4), (x + 4, y + 4), (x, y + 10)
        ])

        if self.max_hp > 1:
            bar_w = self.radius * 2
            ratio = clamp(self.hp / self.max_hp, 0, 1)
            pygame.draw.rect(surf, BLACK, (x - bar_w / 2, y - self.radius - 10, bar_w, 4))
            pygame.draw.rect(surf, GREEN, (x - bar_w / 2, y - self.radius - 10, bar_w * ratio, 4))

    def take_damage(self, dmg=1):
        self.hp -= dmg
        return self.hp <= 0


def darken(color, amount):
    return tuple(clamp(c - amount, 0, 255) for c in color)


# --------------------------------------------------------------------------
# WAVE / FORMATION MANAGEMENT
# --------------------------------------------------------------------------
enemies = []
formation_x = 0.0
formation_y = 0.0
formation_dir = 1
formation_speed = 40.0
spacing_x = 46
spacing_y = 44
cols = 7
egg_drop_timer = 0.0
wave_number = 1


def build_wave(wave_num):
    """Creates a new grid of enemy chickens for the given wave number."""
    global enemies, formation_x, formation_y, formation_dir, formation_speed, cols

    enemies = []
    rows = min(3 + wave_num // 2, 6)
    cols_local = min(6 + wave_num // 3, 9)

    for row in range(rows):
        for col in range(cols_local):
            roll = random.random()
            if row == 0 and roll < 0.25:
                kind = "elite"
            elif roll < 0.55:
                kind = "medium"
            else:
                kind = "small"
            enemies.append(EnemyChicken(col, row, kind))

    globals()["cols"] = cols_local
    formation_x = (WIDTH - (cols_local - 1) * spacing_x) / 2
    formation_y = 90
    formation_dir = 1
    formation_speed = 35 + wave_num * 4


def update_formation(dt):
    """Moves the whole grid left/right, stepping down at the edges (classic
    Space-Invaders movement)."""
    global formation_x, formation_dir, formation_y

    if not enemies:
        return

    min_col = min(e.col for e in enemies)
    max_col = max(e.col for e in enemies)
    left_edge = formation_x + min_col * spacing_x
    right_edge = formation_x + max_col * spacing_x

    formation_x += formation_dir * formation_speed * dt

    if right_edge < WIDTH - 40 and left_edge > 40:
        pass  # still safely inside bounds, nothing special to do
    if left_edge <= 30 and formation_dir < 0:
        formation_dir = 1
        formation_y += 22
    elif right_edge >= WIDTH - 30 and formation_dir > 0:
        formation_dir = -1
        formation_y += 22


def maybe_drop_egg(dt):
    global egg_drop_timer
    egg_drop_timer -= dt
    if egg_drop_timer <= 0 and enemies:
        egg_drop_timer = random.uniform(0.5, 1.3)
        shooter = random.choice(enemies)
        x, y = shooter.get_pos(formation_x, formation_y, spacing_x, spacing_y)
        eggs.append(Egg(x, y + shooter.radius))


# --------------------------------------------------------------------------
# GAME STATE
# --------------------------------------------------------------------------
def reset_game():
    global ship, player_bullets, eggs, particles, floating_texts
    global score, game_state, wave_number, egg_drop_timer

    ship = Ship()
    player_bullets.clear()
    eggs.clear()
    particles.clear()
    floating_texts.clear()

    score = 0
    wave_number = 1
    egg_drop_timer = 1.0
    build_wave(wave_number)
    game_state = "PLAYING"


score = 0
game_state = "MENU"
best_score = 0


def kill_enemy(enemy, x, y):
    global score
    score += enemy.points
    floating_texts.append(FloatingText(x, y, f"+{enemy.points}", YELLOW))
    spawn_burst(x, y, enemy.color, n=22, speed=180)
    if enemy in enemies:
        enemies.remove(enemy)


# --------------------------------------------------------------------------
# UI SCREENS
# --------------------------------------------------------------------------
def draw_hud():
    pygame.draw.rect(screen, (20, 12, 30), (0, 0, WIDTH, 50))
    s = FONT_MED.render(f"Score: {score}", True, WHITE)
    screen.blit(s, (14, 10))

    w = FONT_SMALL.render(f"Wave {wave_number}", True, PURPLE)
    screen.blit(w, (WIDTH - w.get_width() - 14, 14))

    for i in range(ship.lives):
        pygame.draw.circle(screen, RED, (14 + i * 26 + 220, 25), 8)


def draw_menu():
    title = FONT_BIG.render("EGG INVADERS", True, WHITE)
    shadow = FONT_BIG.render("EGG INVADERS", True, BLACK)
    screen.blit(shadow, title.get_rect(center=(WIDTH / 2 + 3, 220 + 3)))
    screen.blit(title, title.get_rect(center=(WIDTH / 2, 220)))

    hint = FONT_MED.render("Press ENTER to start", True, WHITE)
    screen.blit(hint, hint.get_rect(center=(WIDTH / 2, 300)))

    lines = [
        "A/D or Arrows - Move       SPACE - Shoot",
        "ESC - Pause     Survive the chicken waves!",
    ]
    for i, line in enumerate(lines):
        t = FONT_TINY.render(line, True, GRAY)
        screen.blit(t, t.get_rect(center=(WIDTH / 2, 360 + i * 26)))

    if best_score > 0:
        b = FONT_SMALL.render(f"Best Score: {best_score}", True, YELLOW)
        screen.blit(b, b.get_rect(center=(WIDTH / 2, 440)))


def draw_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    t = FONT_BIG.render("PAUSED", True, WHITE)
    screen.blit(t, t.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30)))
    h = FONT_SMALL.render("Press ESC to resume", True, WHITE)
    screen.blit(h, h.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))


def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    t = FONT_BIG.render("GAME OVER", True, RED)
    screen.blit(t, t.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 80)))

    s = FONT_MED.render(f"Score: {score}", True, WHITE)
    screen.blit(s, s.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 15)))

    b = FONT_SMALL.render(f"Best Score: {best_score}", True, YELLOW)
    screen.blit(b, b.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 25)))

    r = FONT_SMALL.render("Press R to Restart", True, WHITE)
    screen.blit(r, r.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 70)))


# --------------------------------------------------------------------------
# COLLISION HELPERS
# --------------------------------------------------------------------------
def dist(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


# --------------------------------------------------------------------------
# MAIN LOOP
# --------------------------------------------------------------------------
def main():
    global game_state, best_score, wave_number

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "PLAYING":
                        game_state = "PAUSED"
                    elif game_state == "PAUSED":
                        game_state = "PLAYING"
                    elif game_state == "MENU":
                        running = False

                if event.key == pygame.K_RETURN and game_state == "MENU":
                    reset_game()

                if event.key == pygame.K_r and game_state == "GAME_OVER":
                    reset_game()

                if event.key == pygame.K_SPACE and game_state == "PLAYING":
                    ship.try_shoot()

        keys = pygame.key.get_pressed()
        update_stars(dt)

        if game_state == "PLAYING":
            ship.update(dt, keys)
            update_formation(dt)
            maybe_drop_egg(dt)

            for b in player_bullets:
                b.update(dt)
            player_bullets[:] = [b for b in player_bullets if b.alive]

            for e in eggs:
                e.update(dt)
            eggs[:] = [e for e in eggs if e.alive]

            # player bullets vs enemies
            for b in list(player_bullets):
                for enemy in list(enemies):
                    ex, ey = enemy.get_pos(formation_x, formation_y, spacing_x, spacing_y)
                    if dist(b.x, b.y, ex, ey) < enemy.radius:
                        if b in player_bullets:
                            player_bullets.remove(b)
                        if enemy.take_damage(1):
                            kill_enemy(enemy, ex, ey)
                        else:
                            spawn_burst(b.x, b.y, WHITE, n=5, speed=90, life=0.12)
                        break

            # eggs vs ship
            for e in list(eggs):
                if dist(e.x, e.y, ship.x, ship.y) < e.radius + ship.width / 3:
                    eggs.remove(e)
                    ship.take_hit()

            # enemies reaching the ship's row = instant hit + wave over-run
            for enemy in list(enemies):
                ex, ey = enemy.get_pos(formation_x, formation_y, spacing_x, spacing_y)
                if ey + enemy.radius > ship.y - ship.height:
                    ship.take_hit()
                    kill_enemy(enemy, ex, ey)

            if not enemies:
                wave_number += 1
                build_wave(wave_number)
                floating_texts.append(FloatingText(WIDTH / 2, HEIGHT / 2, f"WAVE {wave_number}!", GREEN))

            if ship.lives <= 0:
                best_score = max(best_score, score)
                game_state = "GAME_OVER"

        particles[:] = [p for p in particles if p.update(dt)]
        floating_texts[:] = [f for f in floating_texts if f.update(dt)]

        # ---------------- DRAW ----------------
        draw_background()

        if game_state == "MENU":
            draw_menu()
        else:
            for enemy in enemies:
                ex, ey = enemy.get_pos(formation_x, formation_y, spacing_x, spacing_y)
                enemy.draw(screen, ex, ey)

            for b in player_bullets:
                b.draw(screen)
            for e in eggs:
                e.draw(screen)
            for p in particles:
                p.draw(screen)
            for ft in floating_texts:
                ft.draw(screen)

            ship.draw(screen)
            draw_hud()

            if game_state == "PAUSED":
                draw_pause()
            elif game_state == "GAME_OVER":
                draw_game_over()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()