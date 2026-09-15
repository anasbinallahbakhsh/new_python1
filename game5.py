"""
CHICKEN SHOOTER
----------------
A complete original single-file game made with Python + Pygame only.
All graphics are drawn using Pygame shapes - no external image, audio,
or font files are used. Sound effects are generated in code (if the
`numpy` package is available); the game works perfectly with no sound
at all if numpy or the audio device is unavailable.

Install:
    pip install pygame

Run:
    python chicken_shooter.py

Controls:
    WASD / Arrow Keys   - move the hunter
    Mouse               - aim
    Left Mouse Button   - shoot
    ESC                 - pause / resume
    R                   - restart after Game Over
    ENTER               - start game from the menu
"""

import pygame
import random
import math
import sys

# --------------------------------------------------------------------------
# TRY TO SET UP PROCEDURAL SOUND (completely optional)
# --------------------------------------------------------------------------
SOUND_ENABLED = True
try:
    import numpy as np

    pygame.mixer.pre_init(44100, -16, 1, 512)
except Exception:
    SOUND_ENABLED = False
    np = None

pygame.init()

try:
    pygame.mixer.init()
except Exception:
    SOUND_ENABLED = False


def make_tone(freq=440, duration=0.08, volume=0.4, kind="square"):
    """Generate a very small sound effect in memory. Returns None if
    sound generation is not possible on this system."""
    if not SOUND_ENABLED or np is None:
        return None
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)

        if kind == "square":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif kind == "noise":
            wave = np.random.uniform(-1, 1, n_samples)
        else:
            wave = np.sin(2 * np.pi * freq * t)

        # simple fade out so sounds don't click
        fade = np.linspace(1, 0, n_samples)
        wave = wave * fade * volume

        audio = np.int16(wave * 32767)
        sound = pygame.sndarray.make_sound(audio)
        return sound
    except Exception:
        return None


SND_SHOOT = make_tone(880, 0.06, 0.25, "square")
SND_HIT = make_tone(220, 0.10, 0.35, "noise")
SND_MISS = make_tone(140, 0.15, 0.3, "square")
SND_POWERUP = make_tone(660, 0.18, 0.35, "sine")
SND_BOSS = make_tone(110, 0.25, 0.4, "square")


def play_sound(snd):
    if snd is not None:
        try:
            snd.play()
        except Exception:
            pass


# --------------------------------------------------------------------------
# BASIC SETUP
# --------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chicken Shooter")
clock = pygame.time.Clock()
FPS = 60

FONT_BIG = pygame.font.SysFont("arial", 60, bold=True)
FONT_MED = pygame.font.SysFont("arial", 32, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 20, bold=True)
FONT_TINY = pygame.font.SysFont("arial", 15)

# Colors
SKY_TOP = (120, 190, 235)
SKY_BOTTOM = (200, 230, 210)
GROUND = (90, 160, 90)
WHITE = (255, 255, 255)
BLACK = (15, 15, 15)
RED = (220, 50, 50)
YELLOW = (250, 210, 60)
ORANGE = (240, 140, 40)
BROWN = (120, 80, 45)
GRAY = (120, 120, 130)
BLUE = (60, 140, 230)
GREEN = (60, 200, 100)
PURPLE = (160, 90, 220)

HUD_HEIGHT = 60


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def vec_len(dx, dy):
    return math.hypot(dx, dy)


# --------------------------------------------------------------------------
# PARTICLES
# --------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color, speed=120, life=0.5, size=4):
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
        self.vy += 220 * dt  # gravity
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


def spawn_burst(x, y, color, n=18, speed=150, life=0.5):
    for _ in range(n):
        particles.append(Particle(x, y, color, speed=speed, life=life, size=random.uniform(3, 6)))


def spawn_feathers(x, y, color, n=10):
    for _ in range(n):
        particles.append(Particle(x, y, color, speed=90, life=0.7, size=random.uniform(4, 7)))


# --------------------------------------------------------------------------
# FLOATING SCORE TEXT (score animation)
# --------------------------------------------------------------------------
class FloatingText:
    def __init__(self, x, y, text, color=YELLOW):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = 0.8
        self.max_life = 0.8

    def update(self, dt):
        self.y -= 40 * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        t = clamp(self.life / self.max_life, 0, 1)
        scale = 1.0 + (1 - t) * 0.4
        base = FONT_SMALL.render(self.text, True, self.color)
        w, h = base.get_size()
        scaled = pygame.transform.smoothscale(base, (int(w * scale), int(h * scale)))
        scaled.set_alpha(int(255 * t))
        surf.blit(scaled, (self.x - scaled.get_width() / 2, self.y))


floating_texts = []

# --------------------------------------------------------------------------
# PLAYER (the chicken hunter)
# --------------------------------------------------------------------------
class Player:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT - 90
        self.radius = 22
        self.speed = 260
        self.lives = 3
        self.shoot_cooldown = 0.0
        self.base_cooldown = 0.28
        self.rapidfire_timer = 0.0
        self.shield_timer = 0.0
        self.hit_flash = 0.0
        self.walk_cycle = 0.0

    def get_cooldown(self):
        return self.base_cooldown * (0.35 if self.rapidfire_timer > 0 else 1.0)

    def update(self, dt, keys):
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1

        if dx != 0 or dy != 0:
            length = vec_len(dx, dy)
            dx, dy = dx / length, dy / length
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
            self.walk_cycle += dt * 10

        self.x = clamp(self.x, self.radius, WIDTH - self.radius)
        self.y = clamp(self.y, HUD_HEIGHT + self.radius, HEIGHT - self.radius)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.rapidfire_timer > 0:
            self.rapidfire_timer -= dt
        if self.shield_timer > 0:
            self.shield_timer -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt

    def try_shoot(self, target_x, target_y):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.get_cooldown()
            angle = math.atan2(target_y - self.y, target_x - self.x)
            bullets.append(Bullet(self.x, self.y, angle, owner="player"))
            play_sound(SND_SHOOT)
            spawn_burst(
                self.x + math.cos(angle) * 26, self.y + math.sin(angle) * 26,
                YELLOW, n=5, speed=80, life=0.12
            )

    def take_hit(self):
        if self.shield_timer > 0:
            return
        self.lives -= 1
        self.hit_flash = 0.3
        spawn_burst(self.x, self.y, RED, n=14, speed=140)

    def draw(self, surf, aim_x, aim_y):
        flash = self.hit_flash > 0 and int(self.hit_flash * 20) % 2 == 0
        body_color = WHITE if not flash else RED

        # shield ring
        if self.shield_timer > 0:
            pygame.draw.circle(surf, (100, 200, 255), (int(self.x), int(self.y)), self.radius + 10, 3)

        # legs (simple walk animation)
        leg_off = math.sin(self.walk_cycle) * 6
        pygame.draw.line(surf, ORANGE, (self.x - 6, self.y + 16), (self.x - 6 + leg_off, self.y + 32), 5)
        pygame.draw.line(surf, ORANGE, (self.x + 6, self.y + 16), (self.x + 6 - leg_off, self.y + 32), 5)

        # body
        pygame.draw.circle(surf, body_color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (200, 200, 200), (int(self.x), int(self.y)), self.radius, 2)

        # hat (hunter cap)
        pygame.draw.polygon(surf, BROWN, [
            (self.x - 18, self.y - 12), (self.x + 18, self.y - 12), (self.x, self.y - 34)
        ])

        # gun pointing towards aim direction
        angle = math.atan2(aim_y - self.y, aim_x - self.x)
        gun_len = 34
        gx = self.x + math.cos(angle) * gun_len
        gy = self.y + math.sin(angle) * gun_len
        pygame.draw.line(surf, GRAY, (self.x, self.y), (gx, gy), 6)


player = Player()


# --------------------------------------------------------------------------
# BULLETS (player + boss)
# --------------------------------------------------------------------------
class Bullet:
    def __init__(self, x, y, angle, owner="player", speed=600):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = speed if owner == "player" else speed * 0.55
        self.owner = owner
        self.radius = 5 if owner == "player" else 7
        self.alive = True
        self.trail = []

    def update(self, dt):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        if self.x < -20 or self.x > WIDTH + 20 or self.y < -20 or self.y > HEIGHT + 20:
            self.alive = False
        return self.alive

    def draw(self, surf):
        color = YELLOW if self.owner == "player" else PURPLE
        for i, (tx, ty) in enumerate(self.trail):
            fade = int(120 * (i + 1) / max(len(self.trail), 1))
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, fade), (self.radius, self.radius), self.radius)
            surf.blit(s, (tx - self.radius, ty - self.radius))
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)


bullets = []


# --------------------------------------------------------------------------
# POWER-UPS
# --------------------------------------------------------------------------
class PowerUp:
    TYPES = {
        "shield": (100, 200, 255),
        "rapidfire": (255, 210, 60),
        "life": (255, 90, 120),
    }

    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind = kind
        self.color = PowerUp.TYPES[kind]
        self.radius = 14
        self.life = 6.0
        self.bob = random.uniform(0, math.tau)

    def update(self, dt):
        self.bob += dt * 4
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        y = self.y + math.sin(self.bob) * 5
        pygame.draw.circle(surf, self.color, (int(self.x), int(y)), self.radius)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(y)), self.radius, 2)
        letter = {"shield": "S", "rapidfire": "R", "life": "+"}[self.kind]
        text = FONT_TINY.render(letter, True, BLACK)
        surf.blit(text, text.get_rect(center=(self.x, y)))

    def apply(self, player):
        if self.kind == "shield":
            player.shield_timer = 5.0
        elif self.kind == "rapidfire":
            player.rapidfire_timer = 5.0
        elif self.kind == "life":
            player.lives = min(player.lives + 1, 5)
        play_sound(SND_POWERUP)


powerups = []


# --------------------------------------------------------------------------
# CHICKENS
# --------------------------------------------------------------------------
CHICKEN_TYPES = {
    "normal": {"speed": 110, "hp": 1, "points": 10, "radius": 20, "color": (255, 240, 230)},
    "fast":   {"speed": 210, "hp": 1, "points": 20, "radius": 16, "color": (255, 220, 150)},
    "tank":   {"speed": 70,  "hp": 3, "points": 35, "radius": 26, "color": (230, 200, 190)},
    "boss":   {"speed": 90,  "hp": 15, "points": 200, "radius": 46, "color": (255, 180, 90)},
}


class Chicken:
    def __init__(self, kind="normal"):
        self.kind = kind
        data = CHICKEN_TYPES[kind]
        self.speed = data["speed"]
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.points = data["points"]
        self.radius = data["radius"]
        self.color = data["color"]

        edge = random.choice(["top", "left", "right"])
        if edge == "top":
            self.x = random.uniform(self.radius, WIDTH - self.radius)
            self.y = HUD_HEIGHT - self.radius
        elif edge == "left":
            self.x = -self.radius
            self.y = random.uniform(HUD_HEIGHT + self.radius, HEIGHT - self.radius)
        else:
            self.x = WIDTH + self.radius
            self.y = random.uniform(HUD_HEIGHT + self.radius, HEIGHT - self.radius)

        target_x = random.uniform(self.radius, WIDTH - self.radius)
        target_y = HEIGHT + 40
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

        self.wobble = random.uniform(0, math.tau)
        self.alive = True
        self.shoot_timer = random.uniform(1.0, 2.0)

    def update(self, dt, difficulty_mult):
        self.wobble += dt * 8
        perp_x = -self.vy
        perp_y = self.vx
        p_len = max(vec_len(perp_x, perp_y), 0.001)
        offset = math.sin(self.wobble) * 18
        self.x += (self.vx * difficulty_mult) * dt + (perp_x / p_len) * offset * dt
        self.y += (self.vy * difficulty_mult) * dt + (perp_y / p_len) * offset * dt

        if self.kind == "boss":
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.shoot_timer = random.uniform(1.2, 2.0)
                angle = math.atan2(player.y - self.y, player.x - self.x)
                bullets.append(Bullet(self.x, self.y, angle, owner="boss"))
                play_sound(SND_BOSS)

        # missed: went past bottom of screen without dying
        if self.y - self.radius > HEIGHT:
            return "missed"
        return "alive"

    def take_damage(self, dmg=1):
        self.hp -= dmg
        return self.hp <= 0

    def draw(self, surf):
        flap = math.sin(self.wobble * 2) * 8

        # shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 60),
                             (self.x - self.radius * 0.8, self.y + self.radius * 0.6,
                              self.radius * 1.6, self.radius * 0.5))

        # wings (flap animation)
        pygame.draw.ellipse(surf, darken(self.color, 20),
                             (self.x - self.radius - 4, self.y - 6 + flap, self.radius * 0.9, self.radius * 0.6))
        pygame.draw.ellipse(surf, darken(self.color, 20),
                             (self.x + self.radius - self.radius * 0.4, self.y - 6 - flap,
                              self.radius * 0.9, self.radius * 0.6))

        # body
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

        # beak
        pygame.draw.polygon(surf, ORANGE, [
            (self.x + self.radius * 0.7, self.y - 4),
            (self.x + self.radius * 1.3, self.y),
            (self.x + self.radius * 0.7, self.y + 4),
        ])

        # comb (red crest on top)
        pygame.draw.circle(surf, RED, (int(self.x - 4), int(self.y - self.radius)), max(3, int(self.radius * 0.22)))
        pygame.draw.circle(surf, RED, (int(self.x + 4), int(self.y - self.radius)), max(3, int(self.radius * 0.22)))

        # eye
        pygame.draw.circle(surf, BLACK, (int(self.x + self.radius * 0.3), int(self.y - 4)), max(2, int(self.radius * 0.1)))

        # health bar for tougher chickens
        if self.max_hp > 1:
            bar_w = self.radius * 2
            ratio = clamp(self.hp / self.max_hp, 0, 1)
            pygame.draw.rect(surf, BLACK, (self.x - bar_w / 2, self.y - self.radius - 14, bar_w, 6))
            pygame.draw.rect(surf, GREEN, (self.x - bar_w / 2, self.y - self.radius - 14, bar_w * ratio, 6))


def darken(color, amount):
    return tuple(clamp(c - amount, 0, 255) for c in color)


chickens = []


# --------------------------------------------------------------------------
# GAME STATE
# --------------------------------------------------------------------------
def reset_game():
    global player, bullets, chickens, powerups, particles, floating_texts
    global score, coins, spawn_timer, spawn_interval, difficulty_mult
    global boss_active, next_boss_score, game_state

    player = Player()
    bullets = []
    chickens = []
    powerups = []
    particles = []
    floating_texts = []

    score = 0
    coins = 0
    spawn_timer = 0.0
    spawn_interval = 1.2
    difficulty_mult = 1.0
    boss_active = False
    next_boss_score = 300
    game_state = "PLAYING"


score = 0
coins = 0
spawn_timer = 0.0
spawn_interval = 1.2
difficulty_mult = 1.0
boss_active = False
next_boss_score = 300
game_state = "MENU"
best_score = 0


def spawn_chicken():
    global boss_active
    if boss_active:
        return
    roll = random.random()
    if roll < 0.55:
        kind = "normal"
    elif roll < 0.8:
        kind = "fast"
    else:
        kind = "tank"
    chickens.append(Chicken(kind))


def spawn_boss():
    global boss_active
    boss_active = True
    chickens.append(Chicken("boss"))


def kill_chicken(chicken):
    global score, coins, boss_active
    score += chicken.points
    floating_texts.append(FloatingText(chicken.x, chicken.y, f"+{chicken.points}", YELLOW))
    spawn_burst(chicken.x, chicken.y, chicken.color, n=22, speed=180)
    spawn_feathers(chicken.x, chicken.y, WHITE, n=8)
    play_sound(SND_HIT)

    if chicken.kind == "boss":
        boss_active = False

    # chance to drop a coin or power-up
    r = random.random()
    if r < 0.12:
        powerups.append(PowerUp(chicken.x, chicken.y, random.choice(list(PowerUp.TYPES.keys()))))
    elif r < 0.30:
        coins += 1
        floating_texts.append(FloatingText(chicken.x, chicken.y - 20, "+coin", ORANGE))


# --------------------------------------------------------------------------
# DRAWING: BACKGROUND / HUD / SCREENS
# --------------------------------------------------------------------------
def draw_background():
    for i in range(HEIGHT):
        t = i / HEIGHT
        c = (
            int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t),
            int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t),
            int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t),
        )
        pygame.draw.line(screen, c, (0, i), (WIDTH, i))

    pygame.draw.rect(screen, GROUND, (0, HEIGHT - 40, WIDTH, 40))

    # a few simple clouds
    for cx, cy in [(120, 110), (400, 80), (700, 130), (820, 90)]:
        for dx, dy, r in [(0, 0, 22), (18, 6, 16), (-18, 6, 16)]:
            pygame.draw.circle(screen, (255, 255, 255), (cx + dx, cy + dy), r)


def draw_hud():
    pygame.draw.rect(screen, (30, 30, 40), (0, 0, WIDTH, HUD_HEIGHT))

    score_text = FONT_MED.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (16, 14))

    coin_text = FONT_SMALL.render(f"Coins: {coins}", True, ORANGE)
    screen.blit(coin_text, (260, 20))

    for i in range(player.lives):
        pygame.draw.circle(screen, RED, (WIDTH - 30 - i * 34, 30), 12)

    if player.rapidfire_timer > 0:
        rf = FONT_TINY.render("RAPID FIRE", True, YELLOW)
        screen.blit(rf, (WIDTH / 2 - 40, 8))
    if player.shield_timer > 0:
        sh = FONT_TINY.render("SHIELD", True, (100, 200, 255))
        screen.blit(sh, (WIDTH / 2 - 40, 28))


def draw_crosshair(mx, my):
    pygame.draw.circle(screen, RED, (mx, my), 14, 2)
    pygame.draw.line(screen, RED, (mx - 20, my), (mx + 20, my), 2)
    pygame.draw.line(screen, RED, (mx, my - 20), (mx, my + 20), 2)


def draw_menu():
    title = FONT_BIG.render("CHICKEN SHOOTER", True, WHITE)
    shadow = FONT_BIG.render("CHICKEN SHOOTER", True, BLACK)
    screen.blit(shadow, title.get_rect(center=(WIDTH / 2 + 3, 180 + 3)))
    screen.blit(title, title.get_rect(center=(WIDTH / 2, 180)))

    hint = FONT_MED.render("Press ENTER to start", True, WHITE)
    screen.blit(hint, hint.get_rect(center=(WIDTH / 2, 280)))

    lines = [
        "WASD / Arrows - Move      Mouse - Aim      Left Click - Shoot",
        "ESC - Pause      R - Restart after Game Over",
        "Shoot chickens before they escape past the bottom!",
    ]
    for i, line in enumerate(lines):
        t = FONT_SMALL.render(line, True, (40, 40, 40))
        screen.blit(t, t.get_rect(center=(WIDTH / 2, 350 + i * 30)))

    if best_score > 0:
        b = FONT_SMALL.render(f"Best Score: {best_score}", True, ORANGE)
        screen.blit(b, b.get_rect(center=(WIDTH / 2, 460)))


def draw_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    t = FONT_BIG.render("PAUSED", True, WHITE)
    screen.blit(t, t.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
    h = FONT_SMALL.render("Press ESC to resume", True, WHITE)
    screen.blit(h, h.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))


def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    t = FONT_BIG.render("GAME OVER", True, RED)
    screen.blit(t, t.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 90)))

    s = FONT_MED.render(f"Score: {score}", True, WHITE)
    screen.blit(s, s.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20)))

    c = FONT_SMALL.render(f"Coins collected: {coins}", True, ORANGE)
    screen.blit(c, c.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))

    b = FONT_SMALL.render(f"Best Score: {best_score}", True, YELLOW)
    screen.blit(b, b.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 55)))

    r = FONT_SMALL.render("Press R to Restart", True, WHITE)
    screen.blit(r, r.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 100)))


# --------------------------------------------------------------------------
# COLLISION HELPERS
# --------------------------------------------------------------------------
def circles_collide(x1, y1, r1, x2, y2, r2):
    return vec_len(x1 - x2, y1 - y2) < (r1 + r2)


# --------------------------------------------------------------------------
# MAIN LOOP
# --------------------------------------------------------------------------
def main():
    global spawn_timer, spawn_interval, difficulty_mult, boss_active
    global next_boss_score, game_state, best_score

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        mx, my = pygame.mouse.get_pos()

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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "PLAYING":
                    player.try_shoot(mx, my)

        keys = pygame.key.get_pressed()

        # ---------------- UPDATE ----------------
        if game_state == "PLAYING":
            player.update(dt, keys)

            difficulty_mult = 1.0 + score / 800.0
            spawn_interval = max(0.35, 1.2 - score / 900.0)

            spawn_timer += dt
            if spawn_timer >= spawn_interval:
                spawn_timer = 0.0
                spawn_chicken()

            if not boss_active and score >= next_boss_score:
                spawn_boss()
                next_boss_score += 400

            for b in bullets:
                b.update(dt)
            bullets[:] = [b for b in bullets if b.alive]

            for c in list(chickens):
                status = c.update(dt, difficulty_mult)
                if status == "missed":
                    chickens.remove(c)
                    player.take_hit()
                    play_sound(SND_MISS)
                    if c.kind == "boss":
                        boss_active = False

            for p in powerups:
                p.update(dt)
            powerups[:] = [p for p in powerups if p.life > 0]

            # bullet vs chicken collisions
            for b in list(bullets):
                if b.owner != "player":
                    continue
                for c in list(chickens):
                    if circles_collide(b.x, b.y, b.radius, c.x, c.y, c.radius):
                        if b in bullets:
                            bullets.remove(b)
                        if c.take_damage(1):
                            if c in chickens:
                                chickens.remove(c)
                            kill_chicken(c)
                        else:
                            spawn_burst(b.x, b.y, WHITE, n=6, speed=90, life=0.15)
                        break

            # boss bullets vs player
            for b in list(bullets):
                if b.owner == "boss" and circles_collide(b.x, b.y, b.radius, player.x, player.y, player.radius):
                    bullets.remove(b)
                    player.take_hit()

            # chicken vs player (direct collision)
            for c in list(chickens):
                if circles_collide(c.x, c.y, c.radius, player.x, player.y, player.radius):
                    chickens.remove(c)
                    spawn_burst(c.x, c.y, c.color, n=16, speed=140)
                    player.take_hit()
                    if c.kind == "boss":
                        boss_active = False

            # power-up pickup
            for p in list(powerups):
                if circles_collide(p.x, p.y, p.radius, player.x, player.y, player.radius):
                    p.apply(player)
                    powerups.remove(p)

            if player.lives <= 0:
                best_score = max(best_score, score)
                game_state = "GAME_OVER"

        particles[:] = [p for p in particles if p.update(dt)]
        floating_texts[:] = [f for f in floating_texts if f.update(dt)]

        # ---------------- DRAW ----------------
        draw_background()

        if game_state == "MENU":
            draw_menu()
        else:
            for c in chickens:
                c.draw(screen)
            for b in bullets:
                b.draw(screen)
            for p in powerups:
                p.draw(screen)
            for pt in particles:
                pt.draw(screen)
            for ft in floating_texts:
                ft.draw(screen)

            player.draw(screen, mx, my)
            draw_hud()
            draw_crosshair(mx, my)

            if game_state == "PAUSED":
                draw_pause()
            elif game_state == "GAME_OVER":
                draw_game_over()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()