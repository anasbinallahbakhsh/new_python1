"""
EGG INVADERS
-------------
An original formation-shooter game built with pure Python + Pygame.
All graphics are drawn using Pygame shapes only - no external images,
fonts, or sound files are required. This is an original re-imagining
of the classic "invaders" genre and does not copy any existing game's
characters, code, or assets.

Controls:
    A / D or LEFT / RIGHT   - move the ship
    SPACE or Left Click     - shoot (hold for continuous fire)
    E or Right Click        - Nova Blast special attack (needs full meter)
    ESC                     - pause / resume
    ENTER                   - start from menu
    R                       - restart after game over

Install:  pip install pygame
Run:      python egg_invaders.py
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

FONT_BIG = pygame.font.SysFont("arial", 50, bold=True)
FONT_MED = pygame.font.SysFont("arial", 28, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 18, bold=True)
FONT_TINY = pygame.font.SysFont("arial", 14)

# Colors
SPACE_TOP = (20, 15, 40)
SPACE_BOTTOM = (55, 30, 70)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)
RED = (230, 60, 60)
YELLOW = (250, 210, 70)
ORANGE = (240, 140, 50)
TEAL = (70, 200, 190)
PURPLE = (170, 100, 220)
GREEN = (90, 210, 120)
CYAN = (100, 220, 230)
GRAY = (150, 155, 165)

HUD_HEIGHT = 56


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def vec_len(dx, dy):
    return math.hypot(dx, dy)


def darken(c, amt):
    return tuple(clamp(x - amt, 0, 255) for x in c)


def lighten(c, amt):
    return tuple(clamp(x + amt, 0, 255) for x in c)


def circles_collide(x1, y1, r1, x2, y2, r2):
    return vec_len(x1 - x2, y1 - y2) < (r1 + r2)


# --------------------------------------------------------------------------
# PARTICLES / FLOATING SCORE TEXT
# --------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color, speed=140, life=0.5, size=4):
        angle = random.uniform(0, math.tau)
        spd = random.uniform(speed * 0.4, speed)
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
        self.vy += 60 * dt
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


def spawn_burst(x, y, color, n=16, speed=160, life=0.5):
    for _ in range(n):
        particles.append(Particle(x, y, color, speed=speed, life=life, size=random.uniform(3, 6)))


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
        s = FONT_SMALL.render(self.text, True, self.color)
        s.set_alpha(int(255 * t))
        surf.blit(s, (self.x - s.get_width() / 2, self.y))


floating_texts = []


# --------------------------------------------------------------------------
# PLAYER SHIP
# --------------------------------------------------------------------------
class Player:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT - 70
        self.radius = 20
        self.speed = 300
        self.lives = 3
        self.shoot_cooldown = 0.0
        self.base_cooldown = 0.22
        self.special_meter = 0.0
        self.hit_flash = 0.0
        self.engine_flicker = 0.0

    def update(self, dt, keys):
        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        self.x += dx * self.speed * dt
        self.x = clamp(self.x, self.radius + 10, WIDTH - self.radius - 10)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        self.engine_flicker += dt * 20

    def try_shoot(self):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.base_cooldown
            bullets.append(PlayerBullet(self.x, self.y - self.radius))

    def take_hit(self):
        self.lives -= 1
        self.hit_flash = 0.4
        spawn_burst(self.x, self.y, RED, n=18, speed=180)

    def add_meter(self, amount):
        self.special_meter = clamp(self.special_meter + amount, 0, 100)

    def draw(self, surf):
        flash = self.hit_flash > 0 and int(self.hit_flash * 20) % 2 == 0
        nose_color = RED if flash else (230, 80, 60)
        body_color = (60, 150, 220) if not flash else RED

        flick = abs(math.sin(self.engine_flicker))
        r = self.radius

        # twin engine flames
        for ex in (-r * 0.5, r * 0.5):
            pygame.draw.polygon(surf, ORANGE, [
                (self.x + ex - 6, self.y + r * 0.9),
                (self.x + ex + 6, self.y + r * 0.9),
                (self.x + ex, self.y + r * 0.9 + 14 + flick * 10),
            ])
            pygame.draw.polygon(surf, YELLOW, [
                (self.x + ex - 3, self.y + r * 0.9),
                (self.x + ex + 3, self.y + r * 0.9),
                (self.x + ex, self.y + r * 0.9 + 8 + flick * 6),
            ])

        # swept-back wings
        pygame.draw.polygon(surf, darken(body_color, 15), [
            (self.x - r * 0.5, self.y),
            (self.x - r * 1.9, self.y + r * 0.9),
            (self.x - r * 0.9, self.y + r * 0.5),
            (self.x - r * 0.3, self.y + r * 0.7),
        ])
        pygame.draw.polygon(surf, darken(body_color, 15), [
            (self.x + r * 0.5, self.y),
            (self.x + r * 1.9, self.y + r * 0.9),
            (self.x + r * 0.9, self.y + r * 0.5),
            (self.x + r * 0.3, self.y + r * 0.7),
        ])
        pygame.draw.polygon(surf, RED, [
            (self.x - r * 1.9, self.y + r * 0.9),
            (self.x - r * 1.5, self.y + r * 0.75),
            (self.x - r * 1.6, self.y + r * 1.05),
        ])
        pygame.draw.polygon(surf, RED, [
            (self.x + r * 1.9, self.y + r * 0.9),
            (self.x + r * 1.5, self.y + r * 0.75),
            (self.x + r * 1.6, self.y + r * 1.05),
        ])

        # main fuselage
        pygame.draw.polygon(surf, body_color, [
            (self.x, self.y - r * 1.7),
            (self.x - r * 0.55, self.y + r * 0.9),
            (self.x + r * 0.55, self.y + r * 0.9),
        ])
        pygame.draw.polygon(surf, lighten(body_color, 25), [
            (self.x, self.y - r * 1.4),
            (self.x - r * 0.3, self.y + r * 0.3),
            (self.x + r * 0.3, self.y + r * 0.3),
        ])

        # nose tip
        pygame.draw.polygon(surf, nose_color, [
            (self.x, self.y - r * 1.7),
            (self.x - r * 0.18, self.y - r * 0.9),
            (self.x + r * 0.18, self.y - r * 0.9),
        ])

        # cockpit
        pygame.draw.circle(surf, CYAN, (int(self.x), int(self.y - r * 0.3)), max(4, int(r * 0.34)))
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y - r * 0.3)), max(4, int(r * 0.34)), 1)

        # side guns
        pygame.draw.line(surf, GRAY, (self.x - r * 0.7, self.y + r * 0.1),
                          (self.x - r * 0.7, self.y - r * 0.5), 4)
        pygame.draw.line(surf, GRAY, (self.x + r * 0.7, self.y + r * 0.1),
                          (self.x + r * 0.7, self.y - r * 0.5), 4)


player = Player()


# --------------------------------------------------------------------------
# BULLETS / EGG BOMBS
# --------------------------------------------------------------------------
class PlayerBullet:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 560
        self.radius = 5
        self.alive = True

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < -20:
            self.alive = False
        return self.alive

    def draw(self, surf):
        pygame.draw.line(surf, CYAN, (self.x, self.y), (self.x, self.y + 14), 4)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.radius)


bullets = []


class EggBomb:
    def __init__(self, x, y, speed):
        self.x, self.y = x, y
        self.speed = speed
        self.radius = 8
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
        pygame.draw.ellipse(surf, (250, 245, 225),
                             (self.x - self.radius * 0.7, self.y - self.radius, self.radius * 1.4, self.radius * 2))
        pygame.draw.ellipse(surf, (210, 200, 170),
                             (self.x - self.radius * 0.7, self.y - self.radius, self.radius * 1.4, self.radius * 2), 1)


eggs = []


class EnergyOrb:
    """A glowing bonus that drifts down from the top. Touching it with the
    ship refills the special-attack meter - an original power-up, not tied
    to any particular enemy."""

    def __init__(self):
        self.x = random.uniform(40, WIDTH - 40)
        self.y = HUD_HEIGHT - 10
        self.radius = 13
        self.speed = 90
        self.pulse = random.uniform(0, math.tau)
        self.alive = True

    def update(self, dt):
        self.y += self.speed * dt
        self.pulse += dt * 6
        if self.y > HEIGHT + 20:
            self.alive = False
        return self.alive

    def draw(self, surf):
        glow = 6 + math.sin(self.pulse) * 3
        s = pygame.Surface((int((self.radius + glow) * 2), int((self.radius + glow) * 2)), pygame.SRCALPHA)
        c = s.get_width() // 2
        pygame.draw.circle(s, (*GREEN, 90), (c, c), int(self.radius + glow))
        surf.blit(s, (self.x - c, self.y - c))
        pygame.draw.circle(surf, GREEN, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        bolt = FONT_TINY.render("E", True, BLACK)
        surf.blit(bolt, bolt.get_rect(center=(self.x, self.y)))

    def apply(self, player):
        player.add_meter(35)
        floating_texts.append(FloatingText(self.x, self.y, "+ENERGY", GREEN))


energy_orbs = []
energy_orb_timer = 0.0


# --------------------------------------------------------------------------
# ENEMIES (grid formation) + BOSS
# --------------------------------------------------------------------------
ENEMY_TYPES = {
    "grunt": {"hp": 1, "points": 10, "radius": 18, "color": TEAL},
    "elite": {"hp": 2, "points": 25, "radius": 20, "color": PURPLE},
}

GRUNT_PALETTE = [
    (70, 200, 190),   # teal
    (230, 90, 90),    # red
    (240, 190, 70),   # gold
    (110, 200, 110),  # green
]

SPACING_X = 50
SPACING_Y = 46

formation_anchor_x = 0.0
formation_anchor_y = 0.0
formation_offset = 0.0
formation_dir = 1
formation_speed = 40.0
formation_drop = 0.0


class Enemy:
    def __init__(self, row, col, kind="grunt"):
        self.row, self.col = row, col
        data = ENEMY_TYPES[kind]
        self.kind = kind
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.points = data["points"]
        self.radius = data["radius"]
        self.color = random.choice(GRUNT_PALETTE) if kind == "grunt" else data["color"]
        self.alive = True
        self.bob = random.uniform(0, math.tau)
        self.shoot_timer = random.uniform(2.0, 5.0)

    def base_pos(self):
        x = formation_anchor_x + self.col * SPACING_X + formation_offset
        y = formation_anchor_y + self.row * SPACING_Y + formation_drop
        return x, y

    def get_pos(self):
        return self.base_pos()

    def update(self, dt):
        self.bob += dt * 4
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = max(1.2, random.uniform(3.0, 6.0) - min(wave_number * 0.15, 2.5))
            x, y = self.base_pos()
            if random.random() < 0.5:
                eggs.append(EggBomb(x, y + self.radius, 130 + wave_number * 10))

    def take_damage(self, dmg=1):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surf):
        x, y = self.base_pos()
        y += math.sin(self.bob) * 4
        flap = math.sin(self.bob * 2) * 10
        r = self.radius

        wing_color = lighten(self.color, 25)
        trim_color = darken(self.color, 40)

        # wide-spread wings (chevron / V shape like the reference formation art)
        pygame.draw.polygon(surf, wing_color, [
            (x - r * 0.3, y - r * 0.1),
            (x - r * 2.1, y - r * 0.9 - flap * 0.4),
            (x - r * 1.7, y - r * 0.1 - flap * 0.2),
            (x - r * 1.0, y + r * 0.3),
        ])
        pygame.draw.polygon(surf, wing_color, [
            (x + r * 0.3, y - r * 0.1),
            (x + r * 2.1, y - r * 0.9 + flap * 0.4),
            (x + r * 1.7, y - r * 0.1 + flap * 0.2),
            (x + r * 1.0, y + r * 0.3),
        ])
        pygame.draw.polygon(surf, trim_color, [
            (x - r * 2.1, y - r * 0.9 - flap * 0.4),
            (x - r * 1.7, y - r * 0.1 - flap * 0.2),
            (x - r * 1.9, y - r * 0.35 - flap * 0.3),
        ])
        pygame.draw.polygon(surf, trim_color, [
            (x + r * 2.1, y - r * 0.9 + flap * 0.4),
            (x + r * 1.7, y - r * 0.1 + flap * 0.2),
            (x + r * 1.9, y - r * 0.35 + flap * 0.3),
        ])

        # helmet / head shape
        pygame.draw.circle(surf, self.color, (int(x), int(y)), r)
        pygame.draw.circle(surf, trim_color, (int(x), int(y)), r, max(1, int(r * 0.12)))

        # antenna crest on top
        pygame.draw.line(surf, trim_color, (x, y - r), (x, y - r * 1.6), max(1, int(r * 0.14)))
        pygame.draw.circle(surf, RED, (int(x), int(y - r * 1.65)), max(2, int(r * 0.18)))

        # big goggle eyes (like the reference art's wide eyes)
        eye_r = max(3, int(r * 0.42))
        pygame.draw.circle(surf, WHITE, (int(x - r * 0.4), int(y)), eye_r)
        pygame.draw.circle(surf, WHITE, (int(x + r * 0.4), int(y)), eye_r)
        pygame.draw.circle(surf, CYAN, (int(x - r * 0.4), int(y)), max(2, int(eye_r * 0.6)))
        pygame.draw.circle(surf, CYAN, (int(x + r * 0.4), int(y)), max(2, int(eye_r * 0.6)))
        pygame.draw.circle(surf, BLACK, (int(x - r * 0.4), int(y)), max(1, int(eye_r * 0.28)))
        pygame.draw.circle(surf, BLACK, (int(x + r * 0.4), int(y)), max(1, int(eye_r * 0.28)))

        # beak / chin plate
        pygame.draw.polygon(surf, ORANGE, [
            (x - r * 0.35, y + r * 0.55),
            (x + r * 0.35, y + r * 0.55),
            (x, y + r * 0.95),
        ])

        if self.max_hp > 1:
            bar_w = self.radius * 2
            ratio = clamp(self.hp / self.max_hp, 0, 1)
            pygame.draw.rect(surf, BLACK, (x - bar_w / 2, y - self.radius - 22, bar_w, 4))
            pygame.draw.rect(surf, GREEN, (x - bar_w / 2, y - self.radius - 22, bar_w * ratio, 4))


enemies = []


class Boss:
    def __init__(self, wave):
        self.x = WIDTH / 2
        self.y = 90
        self.radius = 42
        self.hp = 20 + wave * 4
        self.max_hp = self.hp
        self.points = 300
        self.color = ORANGE
        self.dir = 1
        self.speed = 90
        self.shoot_timer = 1.5
        self.bob = 0.0
        self.alive = True
        self.shield_hp = 8 + wave * 2
        self.max_shield = self.shield_hp
        self.shield_angle = 0.0

    def update(self, dt):
        self.bob += dt * 3
        self.shield_angle += dt * 90
        self.x += self.dir * self.speed * dt
        if self.x < 60 or self.x > WIDTH - 60:
            self.dir *= -1
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = random.uniform(1.0, 1.6)
            for off in (-30, 0, 30):
                eggs.append(EggBomb(self.x + off, self.y + self.radius, 170))

    def take_damage(self, dmg=1):
        if self.shield_hp > 0:
            self.shield_hp -= dmg
            if self.shield_hp <= 0:
                self.shield_hp = 0
                spawn_burst(self.x, self.y, CYAN, n=24, speed=180)
                floating_texts.append(FloatingText(self.x, self.y - 60, "SHIELD DOWN", CYAN))
            return False
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surf):
        y = self.y + math.sin(self.bob) * 6
        flap = math.sin(self.bob * 2) * 10

        pygame.draw.ellipse(surf, darken(self.color, 25),
                             (self.x - self.radius - 14, y - 8 + flap, self.radius * 1.1, self.radius * 0.8))
        pygame.draw.ellipse(surf, darken(self.color, 25),
                             (self.x + self.radius - self.radius * 0.1, y - 8 - flap, self.radius * 1.1, self.radius * 0.8))

        # rotating shield ring (must be broken before the boss takes real damage)
        if self.shield_hp > 0:
            shield_r = self.radius + 14
            for i in range(6):
                a = math.radians(self.shield_angle + i * 60)
                sx = self.x + math.cos(a) * shield_r
                sy = y + math.sin(a) * shield_r
                pygame.draw.circle(surf, CYAN, (int(sx), int(sy)), 4)
            pygame.draw.circle(surf, CYAN, (int(self.x), int(y)), shield_r, 2)

        pygame.draw.circle(surf, self.color, (int(self.x), int(y)), self.radius)
        pygame.draw.circle(surf, RED, (int(self.x - 10), int(y - self.radius)), 8)
        pygame.draw.circle(surf, RED, (int(self.x + 10), int(y - self.radius)), 8)
        pygame.draw.circle(surf, WHITE, (int(self.x - 14), int(y - 6)), 9)
        pygame.draw.circle(surf, BLACK, (int(self.x - 12), int(y - 6)), 4)
        pygame.draw.circle(surf, WHITE, (int(self.x + 14), int(y - 6)), 9)
        pygame.draw.circle(surf, BLACK, (int(self.x + 16), int(y - 6)), 4)

        # shield bar (cyan) shown above the hp bar while shield is up
        bar_w = self.radius * 2.4
        if self.shield_hp > 0:
            s_ratio = clamp(self.shield_hp / self.max_shield, 0, 1)
            pygame.draw.rect(surf, BLACK, (self.x - bar_w / 2, y - self.radius - 30, bar_w, 6))
            pygame.draw.rect(surf, CYAN, (self.x - bar_w / 2, y - self.radius - 30, bar_w * s_ratio, 6))

        ratio = clamp(self.hp / self.max_hp, 0, 1)
        pygame.draw.rect(surf, BLACK, (self.x - bar_w / 2, y - self.radius - 18, bar_w, 8))
        pygame.draw.rect(surf, RED, (self.x - bar_w / 2, y - self.radius - 18, bar_w * ratio, 8))


boss = None


def spawn_wave(wave):
    global enemies, boss, formation_anchor_x, formation_anchor_y
    global formation_offset, formation_dir, formation_speed, formation_drop

    rows = min(3 + wave // 2, 6)
    cols = min(6 + wave // 2, 9)
    formation_anchor_x = (WIDTH - (cols - 1) * SPACING_X) / 2
    formation_anchor_y = 100
    formation_offset = 0.0
    formation_dir = 1
    formation_speed = 40 + wave * 6
    formation_drop = 0.0

    enemies = []
    for r in range(rows):
        for c in range(cols):
            kind = "elite" if r == 0 else "grunt"
            enemies.append(Enemy(r, c, kind))

    boss = None
    if wave % 3 == 0:
        boss = Boss(wave)


def update_formation(dt):
    global formation_offset, formation_dir, formation_drop

    alive_enemies = [e for e in enemies if e.alive]
    if not alive_enemies:
        return

    formation_offset += formation_dir * formation_speed * dt

    xs = [e.base_pos()[0] for e in alive_enemies]
    min_x, max_x = min(xs), max(xs)
    if min_x < 24 or max_x > WIDTH - 24:
        formation_dir *= -1
        formation_offset += formation_dir * formation_speed * dt * 2
        formation_drop += 18


# --------------------------------------------------------------------------
# SCORE / SPECIAL ATTACK
# --------------------------------------------------------------------------
def score_add(points):
    global score
    score += points


class LaserBeam:
    """A brief, wide golden beam blast effect - purely visual, fired
    straight up from the player when Nova Blast triggers."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 0.35
        self.max_life = 0.35

    def update(self, dt):
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        t = clamp(self.life / self.max_life, 0, 1)
        w = 34 * t + 6
        s = pygame.Surface((int(w) + 20, HUD_HEIGHT + 50), pygame.SRCALPHA)
        pygame.draw.rect(s, (*YELLOW, int(200 * t)), (10, 0, w, s.get_height()), border_radius=int(w / 2))
        pygame.draw.rect(s, (*WHITE, int(230 * t)), (10 + w * 0.3, 0, w * 0.4, s.get_height()), border_radius=6)
        surf.blit(s, (self.x - s.get_width() / 2, self.y - s.get_height()))


beams = []


def nova_blast():
    global eggs
    eggs = []
    beams.append(LaserBeam(player.x, player.y - 20))
    spawn_burst(player.x, player.y - 40, CYAN, n=40, speed=260, life=0.6)
    for e in enemies:
        if e.alive:
            x, y = e.get_pos()
            if e.take_damage(1):
                score_add(e.points)
                floating_texts.append(FloatingText(x, y, f"+{e.points}"))
                spawn_burst(x, y, e.color, n=10, speed=120)
    if boss is not None and boss.alive:
        if boss.take_damage(3):
            score_add(boss.points)
            floating_texts.append(FloatingText(boss.x, boss.y, f"+{boss.points}"))
            spawn_burst(boss.x, boss.y, boss.color, n=30, speed=200)


# --------------------------------------------------------------------------
# GAME STATE
# --------------------------------------------------------------------------
def reset_game():
    global player, bullets, eggs, particles, floating_texts, level_badges
    global score, wave_number, game_state, energy_orbs, energy_orb_timer, beams

    player = Player()
    bullets = []
    eggs = []
    particles = []
    floating_texts = []
    level_badges = []
    energy_orbs = []
    energy_orb_timer = random.uniform(4.0, 7.0)
    beams = []
    score = 0
    wave_number = 1
    spawn_wave(wave_number)
    game_state = "PLAYING"


score = 0
wave_number = 1
game_state = "MENU"
best_score = 0


# --------------------------------------------------------------------------
# DRAWING: BACKGROUND / HUD / SCREENS
# --------------------------------------------------------------------------
def draw_background():
    for i in range(HEIGHT):
        t = i / HEIGHT
        c = (
            int(SPACE_TOP[0] + (SPACE_BOTTOM[0] - SPACE_TOP[0]) * t),
            int(SPACE_TOP[1] + (SPACE_BOTTOM[1] - SPACE_TOP[1]) * t),
            int(SPACE_TOP[2] + (SPACE_BOTTOM[2] - SPACE_TOP[2]) * t),
        )
        pygame.draw.line(screen, c, (0, i), (WIDTH, i))

    rng = random.Random(42)
    for _ in range(70):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT)
        r = rng.choice([1, 1, 1, 2])
        pygame.draw.circle(screen, WHITE, (x, y), r)

    # a couple of distant planets for depth (purely decorative, original design)
    pygame.draw.circle(screen, (90, 60, 120), (WIDTH - 70, 560), 60)
    pygame.draw.circle(screen, (110, 75, 140), (WIDTH - 90, 545), 60, 0)
    pygame.draw.circle(screen, (70, 45, 100), (WIDTH - 70, 560), 60, 3)
    pygame.draw.circle(screen, (50, 30, 70), (95, 640), 26)
    pygame.draw.circle(screen, (65, 40, 85), (95, 640), 26, 2)


def draw_ship_icon(surf, x, y, scale=1.0, color=WHITE):
    r = 8 * scale
    pygame.draw.polygon(surf, color, [
        (x, y - r * 1.6), (x - r, y + r * 0.8), (x + r, y + r * 0.8)
    ])
    pygame.draw.polygon(surf, darken(color, 40), [
        (x - r * 0.6, y + r * 0.6), (x - r * 1.3, y + r * 1.4), (x - r * 0.1, y + r * 1.0)
    ])
    pygame.draw.polygon(surf, darken(color, 40), [
        (x + r * 0.6, y + r * 0.6), (x + r * 1.3, y + r * 1.4), (x + r * 0.1, y + r * 1.0)
    ])


def draw_hud():
    pygame.draw.rect(screen, (10, 10, 20), (0, 0, WIDTH, HUD_HEIGHT))

    s = FONT_MED.render(f"Score: {score}", True, WHITE)
    screen.blit(s, (12, 14))

    wave_box_w = 110
    pygame.draw.rect(screen, (25, 20, 45), (WIDTH - wave_box_w - 10, 4, wave_box_w, 22), border_radius=6)
    w = FONT_SMALL.render(f"WAVE {wave_number}", True, YELLOW)
    screen.blit(w, w.get_rect(center=(WIDTH - wave_box_w / 2 - 10, 15)))

    for i in range(player.lives):
        draw_ship_icon(screen, WIDTH - wave_box_w - 4 - i * 24, 44, scale=1.0, color=(220, 230, 255))

    meter_w = 90
    ratio = player.special_meter / 100
    pygame.draw.rect(screen, (40, 40, 50), (14, HEIGHT - 34, meter_w, 14), border_radius=6)
    color = GREEN if ratio >= 1 else CYAN
    pygame.draw.rect(screen, color, (14, HEIGHT - 34, meter_w * ratio, 14), border_radius=6)
    lbl = FONT_TINY.render("NOVA (E)", True, WHITE)
    screen.blit(lbl, (14, HEIGHT - 52))


class LevelBadge:
    """A chevron-style level-up badge that pops in the corner for a
    couple of seconds whenever a new wave begins."""

    def __init__(self, wave):
        self.wave = wave
        self.life = 2.2
        self.max_life = 2.2
        self.spin = 0.0

    def update(self, dt):
        self.spin += dt * 120
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        t = clamp(self.life / self.max_life, 0, 1)
        pop = 1.0 if t < 0.85 else (1 - t) / 0.15
        size = 34 * (0.6 + 0.4 * pop)
        cx, cy = 46, HEIGHT - 90

        alpha_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        glow = int(140 * t)
        pygame.draw.circle(alpha_surf, (*CYAN, glow), center, size + 10)

        for i in range(3):
            off = i * 10 - 10
            pygame.draw.polygon(alpha_surf, (*GREEN, int(255 * t)), [
                (center[0] - size * 0.5, center[1] + off),
                (center[0], center[1] - size * 0.35 + off),
                (center[0] + size * 0.5, center[1] + off),
                (center[0], center[1] - size * 0.05 + off),
            ])

        surf.blit(alpha_surf, (cx - 60, cy - 60))
        label = FONT_TINY.render(f"WAVE {self.wave}", True, WHITE)
        label.set_alpha(int(255 * t))
        surf.blit(label, label.get_rect(center=(cx, cy + 46)))


level_badges = []


def draw_menu():
    t = FONT_BIG.render("EGG INVADERS", True, WHITE)
    sh = FONT_BIG.render("EGG INVADERS", True, BLACK)
    screen.blit(sh, t.get_rect(center=(WIDTH / 2 + 3, 220 + 3)))
    screen.blit(t, t.get_rect(center=(WIDTH / 2, 220)))

    hint = FONT_MED.render("Press ENTER to start", True, WHITE)
    screen.blit(hint, hint.get_rect(center=(WIDTH / 2, 300)))

    lines = [
        "A/D or Arrows - Move     Space/Click - Shoot",
        "E / Right-click - Nova Blast (when meter is full)",
        "Don't let the flock reach the bottom!",
    ]
    for i, line in enumerate(lines):
        s = FONT_TINY.render(line, True, (230, 230, 230))
        screen.blit(s, s.get_rect(center=(WIDTH / 2, 360 + i * 26)))

    if best_score > 0:
        b = FONT_SMALL.render(f"Best Score: {best_score}", True, YELLOW)
        screen.blit(b, b.get_rect(center=(WIDTH / 2, 460)))


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
    screen.blit(s, s.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20)))

    w = FONT_SMALL.render(f"Reached Wave: {wave_number}", True, YELLOW)
    screen.blit(w, w.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 15)))

    b = FONT_SMALL.render(f"Best Score: {best_score}", True, ORANGE)
    screen.blit(b, b.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50)))

    r = FONT_SMALL.render("Press R to Restart", True, WHITE)
    screen.blit(r, r.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 90)))


# --------------------------------------------------------------------------
# MAIN LOOP
# --------------------------------------------------------------------------
def main():
    global game_state, best_score, wave_number, energy_orb_timer

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

                if event.key == pygame.K_e and game_state == "PLAYING":
                    if player.special_meter >= 100:
                        player.special_meter = 0
                        nova_blast()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and game_state == "PLAYING":
                    if player.special_meter >= 100:
                        player.special_meter = 0
                        nova_blast()

        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if game_state == "PLAYING":
            player.update(dt, keys)

            if keys[pygame.K_SPACE] or mouse_pressed[0]:
                player.try_shoot()

            for b in bullets:
                b.update(dt)
            bullets[:] = [b for b in bullets if b.alive]

            for eg in eggs:
                eg.update(dt)
            eggs[:] = [eg for eg in eggs if eg.alive]

            energy_orb_timer -= dt
            if energy_orb_timer <= 0:
                energy_orb_timer = random.uniform(5.0, 8.0)
                energy_orbs.append(EnergyOrb())

            for orb in energy_orbs:
                orb.update(dt)
            energy_orbs[:] = [orb for orb in energy_orbs if orb.alive]

            for e in enemies:
                if e.alive:
                    e.update(dt)

            update_formation(dt)

            if boss is not None and boss.alive:
                boss.update(dt)

            # bullet vs enemy / boss
            for b in list(bullets):
                hit_something = False
                for e in enemies:
                    if not e.alive:
                        continue
                    ex, ey = e.get_pos()
                    if circles_collide(b.x, b.y, b.radius, ex, ey, e.radius):
                        if b in bullets:
                            bullets.remove(b)
                        if e.take_damage(1):
                            score_add(e.points)
                            floating_texts.append(FloatingText(ex, ey, f"+{e.points}"))
                            spawn_burst(ex, ey, e.color, n=16, speed=140)
                            player.add_meter(6)
                        else:
                            spawn_burst(ex, ey, WHITE, n=5, speed=80, life=0.15)
                        hit_something = True
                        break

                if hit_something:
                    continue

                if boss is not None and boss.alive:
                    if circles_collide(b.x, b.y, b.radius, boss.x, boss.y, boss.radius):
                        if b in bullets:
                            bullets.remove(b)
                        if boss.take_damage(1):
                            score_add(boss.points)
                            floating_texts.append(FloatingText(boss.x, boss.y, f"+{boss.points}"))
                            spawn_burst(boss.x, boss.y, boss.color, n=30, speed=200)
                            player.add_meter(30)
                        else:
                            spawn_burst(b.x, b.y, WHITE, n=5, speed=80, life=0.15)
                            player.add_meter(2)

            # eggs vs player
            for eg in list(eggs):
                if circles_collide(eg.x, eg.y, eg.radius, player.x, player.y, player.radius):
                    eggs.remove(eg)
                    player.take_hit()

            # energy orb vs player
            for orb in list(energy_orbs):
                if circles_collide(orb.x, orb.y, orb.radius, player.x, player.y, player.radius):
                    orb.apply(player)
                    energy_orbs.remove(orb)
                    spawn_burst(orb.x, orb.y, GREEN, n=14, speed=140)

            # invasion check - formation or boss reaching the player line ends the run
            alive_enemies = [e for e in enemies if e.alive]
            if alive_enemies:
                lowest_y = max(e.get_pos()[1] for e in alive_enemies)
                if lowest_y > player.y - 40:
                    player.lives = 0

            if boss is not None and boss.alive and boss.y > player.y - 60:
                player.lives = 0

            if player.lives <= 0:
                best_score = max(best_score, score)
                game_state = "GAME_OVER"

            # wave clear -> next wave
            if not alive_enemies and (boss is None or not boss.alive) and game_state == "PLAYING":
                wave_number += 1
                floating_texts.append(FloatingText(WIDTH / 2, HEIGHT / 2, f"WAVE {wave_number}", GREEN))
                level_badges.append(LevelBadge(wave_number))
                spawn_wave(wave_number)

        particles[:] = [p for p in particles if p.update(dt)]
        floating_texts[:] = [f for f in floating_texts if f.update(dt)]
        level_badges[:] = [b for b in level_badges if b.update(dt)]
        beams[:] = [beam for beam in beams if beam.update(dt)]

        # ---------------- DRAW ----------------
        draw_background()

        if game_state == "MENU":
            draw_menu()
        else:
            for e in enemies:
                if e.alive:
                    e.draw(screen)
            if boss is not None and boss.alive:
                boss.draw(screen)
            for eg in eggs:
                eg.draw(screen)
            for orb in energy_orbs:
                orb.draw(screen)
            for b in bullets:
                b.draw(screen)
            for p in particles:
                p.draw(screen)
            for ft in floating_texts:
                ft.draw(screen)

            player.draw(screen)
            for beam in beams:
                beam.draw(screen)
            draw_hud()
            for badge in level_badges:
                badge.draw(screen)

            if game_state == "PAUSED":
                draw_pause()
            elif game_state == "GAME_OVER":
                draw_game_over()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()