"""
Galaxy Guardian
================
An original Galaxian / Space-Invaders-inspired arcade shooter.

- Pure Python + Pygame.
- All graphics are drawn procedurally with Pygame shapes (no external
  images, no AI-generated assets, no copyrighted material).
- Blue / cyan colour scheme, original geometric alien designs and an
  original ship design, inspired only by the general "vertical shooter
  with a descending enemy formation" gameplay concept.

Run with:  python main.py
Requires:  pygame  (pip install pygame)
"""

import math
import random
import sys

import pygame

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
SCREEN_W, SCREEN_H = 480, 720
FPS = 60

# Colour palette (blue / cyan themed - intentionally different from the
# red/teal reference image)
COL_BG_TOP = (8, 10, 30)
COL_BG_BOTTOM = (20, 8, 40)
COL_STAR = (200, 220, 255)
COL_UI_TEXT = (220, 230, 255)
COL_UI_ACCENT = (90, 200, 255)
COL_PLAYER_BODY = (60, 200, 180)
COL_PLAYER_DARK = (30, 120, 110)
COL_PLAYER_COCKPIT = (180, 240, 255)
COL_PLAYER_BULLET = (120, 240, 255)
COL_ENEMY_BULLET = (255, 210, 90)
COL_DRONE_BODY = (90, 150, 255)
COL_DRONE_DARK = (50, 90, 190)
COL_SCOUT_BODY = (200, 90, 230)
COL_SCOUT_DARK = (130, 50, 160)
COL_ELITE_BODY = (255, 140, 90)
COL_ELITE_DARK = (190, 80, 50)
COL_EXPLOSION = [(255, 220, 90), (255, 150, 60), (255, 90, 60)]

PLAYER_SPEED = 6
PLAYER_BULLET_SPEED = -11
ENEMY_BULLET_SPEED = 5
PLAYER_MAX_HEALTH = 3
PLAYER_FIRE_COOLDOWN = 260  # ms

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# --------------------------------------------------------------------------- #
# Starfield background
# --------------------------------------------------------------------------- #
class Starfield:
    def __init__(self, count=90):
        self.stars = []
        for _ in range(count):
            x = random.uniform(0, SCREEN_W)
            y = random.uniform(0, SCREEN_H)
            speed = random.uniform(0.6, 3.2)
            size = 1 if speed < 1.8 else 2
            self.stars.append([x, y, speed, size])

    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_H:
                star[1] = 0
                star[0] = random.uniform(0, SCREEN_W)

    def draw(self, surf):
        # vertical gradient backdrop
        for y in range(0, SCREEN_H, 4):
            t = y / SCREEN_H
            color = lerp_color(COL_BG_TOP, COL_BG_BOTTOM, t)
            pygame.draw.rect(surf, color, (0, y, SCREEN_W, 4))
        for x, y, speed, size in self.stars:
            alpha_size = size
            pygame.draw.circle(surf, COL_STAR, (int(x), int(y)), alpha_size)


# --------------------------------------------------------------------------- #
# Player ship
# --------------------------------------------------------------------------- #
class Player:
    def __init__(self):
        self.w, self.h = 48, 42
        self.x = SCREEN_W // 2
        self.y = SCREEN_H - 90
        self.health = PLAYER_MAX_HEALTH
        self.last_shot = 0
        self.alive = True
        self.flame_phase = 0
        self.invuln_timer = 0  # brief invulnerability after being hit

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def update(self, keys, dt):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += PLAYER_SPEED
        self.x = clamp(self.x + dx, self.w // 2 + 6, SCREEN_W - self.w // 2 - 6)
        self.flame_phase += dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt

    def can_shoot(self, now):
        return now - self.last_shot >= PLAYER_FIRE_COOLDOWN

    def shoot(self, now):
        self.last_shot = now
        return [
            Bullet(self.x - 14, self.y - self.h // 2, PLAYER_BULLET_SPEED, COL_PLAYER_BULLET, owner="player"),
            Bullet(self.x + 14, self.y - self.h // 2, PLAYER_BULLET_SPEED, COL_PLAYER_BULLET, owner="player"),
        ]

    def hit(self):
        if self.invuln_timer <= 0:
            self.health -= 1
            self.invuln_timer = 1200
            if self.health <= 0:
                self.alive = False
            return True
        return False

    def draw(self, surf):
        if self.invuln_timer > 0 and (self.invuln_timer // 100) % 2 == 0:
            return  # flicker while invulnerable
        cx, cy = int(self.x), int(self.y)

        # engine flame
        flame_len = 10 + 4 * math.sin(self.flame_phase / 60.0)
        for ox in (-12, 12):
            pygame.draw.polygon(
                surf, (255, 180, 60),
                [(cx + ox - 5, cy + 18), (cx + ox + 5, cy + 18), (cx + ox, cy + 18 + flame_len)]
            )

        # hull (original angular design, teal/cyan)
        body = [
            (cx, cy - 22),
            (cx - 20, cy + 14),
            (cx - 10, cy + 10),
            (cx - 6, cy + 20),
            (cx + 6, cy + 20),
            (cx + 10, cy + 10),
            (cx + 20, cy + 14),
        ]
        pygame.draw.polygon(surf, COL_PLAYER_BODY, body)
        pygame.draw.polygon(surf, COL_PLAYER_DARK, body, 2)

        # side wings
        pygame.draw.polygon(surf, COL_PLAYER_DARK,
                             [(cx - 20, cy + 14), (cx - 26, cy + 2), (cx - 12, cy + 6)])
        pygame.draw.polygon(surf, COL_PLAYER_DARK,
                             [(cx + 20, cy + 14), (cx + 26, cy + 2), (cx + 12, cy + 6)])

        # cockpit
        pygame.draw.circle(surf, COL_PLAYER_COCKPIT, (cx, cy - 4), 6)


# --------------------------------------------------------------------------- #
# Enemies
# --------------------------------------------------------------------------- #
class Enemy:
    """An enemy in the formation. kind: 'drone', 'scout', 'elite'."""

    def __init__(self, col, row, kind, home_x, home_y):
        self.col = col
        self.row = row
        self.kind = kind
        self.home_x = home_x
        self.home_y = home_y
        self.x = home_x
        self.y = home_y
        self.w = 34
        self.h = 30
        self.alive = True
        self.diving = False
        self.dive_t = 0
        self.dive_path = []
        self.fire_cooldown = random.randint(1500, 5000)

        DRONE_PALETTE = [COL_DRONE_BODY, (90, 210, 190), (230, 90, 90), (110, 200, 110)]
        SCOUT_PALETTE = [COL_SCOUT_BODY, (240, 190, 70), (90, 150, 255), (230, 120, 60)]

        if kind == "drone":
            self.hp = 1
            self.body_col = random.choice(DRONE_PALETTE)
            self.dark_col = tuple(clamp(c - 45, 0, 255) for c in self.body_col)
            self.score = 50
        elif kind == "scout":
            self.hp = 1
            self.body_col = random.choice(SCOUT_PALETTE)
            self.dark_col = tuple(clamp(c - 45, 0, 255) for c in self.body_col)
            self.score = 80
        else:  # elite / flagship
            self.hp = 3
            self.body_col = COL_ELITE_BODY
            self.dark_col = COL_ELITE_DARK
            self.score = 150

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def start_dive(self, target_x, target_y):
        """Kick off a swooping dive attack toward roughly the player's x."""
        self.diving = True
        self.dive_t = 0
        sx, sy = self.x, self.y
        mid_x = sx + random.choice([-1, 1]) * random.randint(60, 160)
        self.dive_path = [
            (sx, sy),
            (mid_x, sy + (target_y - sy) * 0.35),
            (target_x + random.randint(-40, 40), sy + (target_y - sy) * 0.8),
            (target_x, target_y + 260),
        ]

    def update_dive(self, dt):
        self.dive_t += dt / 1000.0
        duration = 2.6
        t = clamp(self.dive_t / duration, 0, 1)
        p = self._bezier(t)
        self.x, self.y = p
        return t >= 1.0

    def _bezier(self, t):
        p0, p1, p2, p3 = self.dive_path
        u = 1 - t
        x = (u ** 3) * p0[0] + 3 * (u ** 2) * t * p1[0] + 3 * u * (t ** 2) * p2[0] + (t ** 3) * p3[0]
        y = (u ** 3) * p0[1] + 3 * (u ** 2) * t * p1[1] + 3 * u * (t ** 2) * p2[1] + (t ** 3) * p3[1]
        return x, y

    def take_hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surf, bob):
        cx = int(self.x)
        cy = int(self.y + bob)
        body_col = self.body_col
        dark_col = self.dark_col
        light_col = tuple(clamp(c + 30, 0, 255) for c in body_col)

        r = {"drone": 13, "scout": 16, "elite": 20}[self.kind]
        flap = 8 if self.kind == "elite" else 6

        # wide-spread wings (bird-like, mixed colours across the flock)
        pygame.draw.polygon(surf, light_col, [
            (cx - r * 0.3, cy - r * 0.1),
            (cx - r * 2.0, cy - r * 0.9 - flap * 0.3),
            (cx - r * 1.6, cy - r * 0.1 - flap * 0.15),
            (cx - r * 0.9, cy + r * 0.3),
        ])
        pygame.draw.polygon(surf, light_col, [
            (cx + r * 0.3, cy - r * 0.1),
            (cx + r * 2.0, cy - r * 0.9 + flap * 0.3),
            (cx + r * 1.6, cy - r * 0.1 + flap * 0.15),
            (cx + r * 0.9, cy + r * 0.3),
        ])
        pygame.draw.polygon(surf, dark_col, [
            (cx - r * 2.0, cy - r * 0.9 - flap * 0.3),
            (cx - r * 1.6, cy - r * 0.1 - flap * 0.15),
            (cx - r * 1.8, cy - r * 0.35 - flap * 0.2),
        ])
        pygame.draw.polygon(surf, dark_col, [
            (cx + r * 2.0, cy - r * 0.9 + flap * 0.3),
            (cx + r * 1.6, cy - r * 0.1 + flap * 0.15),
            (cx + r * 1.8, cy - r * 0.35 + flap * 0.2),
        ])

        # head / body
        pygame.draw.circle(surf, body_col, (cx, cy), r)
        pygame.draw.circle(surf, dark_col, (cx, cy), r, max(1, int(r * 0.12)))

        # antenna crest
        pygame.draw.line(surf, dark_col, (cx, cy - r), (cx, cy - int(r * 1.5)), max(1, int(r * 0.14)))
        pygame.draw.circle(surf, (255, 90, 90), (cx, cy - int(r * 1.55)), max(2, int(r * 0.18)))

        # big goggle eyes
        eye_r = max(3, int(r * 0.38))
        for ex in (-1, 1):
            pygame.draw.circle(surf, (255, 255, 255), (cx + int(ex * r * 0.4), cy), eye_r)
            pygame.draw.circle(surf, (255, 255, 255), (cx + int(ex * r * 0.4), cy), eye_r, 1)
            pygame.draw.circle(surf, dark_col, (cx + int(ex * r * 0.4), cy), max(1, int(eye_r * 0.5)))

        # beak / chin
        pygame.draw.polygon(surf, (255, 170, 60), [
            (cx - r * 0.3, cy + r * 0.55),
            (cx + r * 0.3, cy + r * 0.55),
            (cx, cy + r * 0.9),
        ])

        # elite flagship gets extra hp-light dots below
        if self.kind == "elite":
            for i in range(self.hp):
                pygame.draw.circle(surf, (255, 255, 255), (cx - 8 + i * 8, cy + int(r * 1.1)), 2)


class Bullet:
    def __init__(self, x, y, vy, color, owner="player", vx=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.owner = owner
        self.radius = 4 if owner == "player" else 5
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y < -20 or self.y > SCREEN_H + 20:
            self.alive = False

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                            self.radius * 2, self.radius * 2)

    def draw(self, surf):
        if self.owner == "player":
            pygame.draw.line(surf, self.color, (self.x, self.y - 8), (self.x, self.y + 8), 3)
            pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y - 8)), 2)
        else:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 1)


class Explosion:
    def __init__(self, x, y, big=False):
        self.x = x
        self.y = y
        self.t = 0
        self.duration = 420 if not big else 620
        self.big = big
        self.alive = True
        self.particles = []
        n = 14 if big else 8
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(1.2, 4.5 if big else 3.0)
            self.particles.append([x, y, math.cos(ang) * spd, math.sin(ang) * spd])

    def update(self, dt):
        self.t += dt
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
        if self.t >= self.duration:
            self.alive = False

    def draw(self, surf):
        progress = clamp(self.t / self.duration, 0, 1)
        for i, p in enumerate(self.particles):
            color = COL_EXPLOSION[i % len(COL_EXPLOSION)]
            radius = max(1, int((1 - progress) * (7 if self.big else 5)))
            pygame.draw.circle(surf, color, (int(p[0]), int(p[1])), radius)


# --------------------------------------------------------------------------- #
# Formation manager
# --------------------------------------------------------------------------- #
class Formation:
    ROWS = 5
    COLS = 8
    H_SPACING = 46
    V_SPACING = 42
    TOP_MARGIN = 70
    SIDE_MARGIN = 40

    def __init__(self, level=1):
        self.enemies = []
        self.direction = 1
        self.speed = 0.9 + (level - 1) * 0.18
        self.drop_amount = 16
        self.time_since_move = 0
        self.move_interval = max(180, 520 - level * 25)
        self.dive_cooldown = 2600
        self.offset_x = 0
        self.offset_y = 0
        self._build(level)

    def _build(self, level):
        for row in range(self.ROWS):
            for col in range(self.COLS):
                hx = self.SIDE_MARGIN + col * self.H_SPACING
                hy = self.TOP_MARGIN + row * self.V_SPACING
                if row == 0:
                    kind = "elite" if col in (0, self.COLS - 1) else "scout"
                elif row <= 2:
                    kind = "scout"
                else:
                    kind = "drone"
                self.enemies.append(Enemy(col, row, kind, hx, hy))

    def alive_enemies(self):
        return [e for e in self.enemies if e.alive]

    def update(self, dt, player, enemy_bullets, sounds):
        alive = self.alive_enemies()
        grounded = [e for e in alive if not e.diving]

        self.time_since_move += dt
        if self.time_since_move >= self.move_interval and grounded:
            self.time_since_move = 0
            min_x = min(e.home_x for e in grounded) + self.offset_x
            max_x = max(e.home_x for e in grounded) + self.offset_x
            if max_x + 20 >= SCREEN_W - 10 or min_x - 20 <= 10:
                if (max_x + 20 >= SCREEN_W - 10 and self.direction > 0) or \
                   (min_x - 20 <= 10 and self.direction < 0):
                    self.direction *= -1
                    self.offset_y += self.drop_amount
                else:
                    self.offset_x += self.direction * 10
            else:
                self.offset_x += self.direction * 10

            for e in grounded:
                e.x = e.home_x + self.offset_x
                e.y = e.home_y + self.offset_y

        # dive attacks
        self.dive_cooldown -= dt
        if self.dive_cooldown <= 0 and grounded and player.alive:
            self.dive_cooldown = random.randint(1400, 2600)
            diver = random.choice(grounded)
            diver.start_dive(player.x, player.y)

        for e in alive:
            if e.diving:
                finished = e.update_dive(dt)
                e.fire_cooldown -= dt
                if e.fire_cooldown <= 0:
                    e.fire_cooldown = random.randint(900, 1800)
                    enemy_bullets.append(Bullet(e.x, e.y + 10, ENEMY_BULLET_SPEED,
                                                 COL_ENEMY_BULLET, owner="enemy"))
                if finished:
                    # loop back into formation from the top
                    e.diving = False
                    e.x = e.home_x + self.offset_x
                    e.y = e.home_y - 40
            else:
                e.fire_cooldown -= dt
                if e.fire_cooldown <= 0 and random.random() < 0.5:
                    e.fire_cooldown = random.randint(1800, 4200)
                    enemy_bullets.append(Bullet(e.x, e.y + 14, ENEMY_BULLET_SPEED,
                                                 COL_ENEMY_BULLET, owner="enemy"))

    def lowest_y(self):
        alive = self.alive_enemies()
        if not alive:
            return 0
        return max(e.y for e in alive)

    def draw(self, surf, t):
        bob = math.sin(t / 260.0) * 3
        for e in self.alive_enemies():
            e.draw(surf, bob if not e.diving else 0)


# --------------------------------------------------------------------------- #
# HUD helpers
# --------------------------------------------------------------------------- #
def draw_text(surf, text, size, color, center, bold=False, glow=False):
    font = pygame.font.Font(None, size)
    font.set_bold(bold)
    if glow:
        glow_surf = font.render(text, True, COL_UI_ACCENT)
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            r = glow_surf.get_rect(center=(center[0] + ox, center[1] + oy))
            surf.blit(glow_surf, r)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surf.blit(rendered, rect)


def draw_health(surf, health, max_health):
    for i in range(max_health):
        cx = 26 + i * 26
        cy = 24
        color = (90, 220, 200) if i < health else (60, 60, 70)
        pygame.draw.polygon(surf, color, [
            (cx, cy - 9), (cx + 8, cy + 5), (cx - 8, cy + 5)
        ])
        pygame.draw.polygon(surf, (10, 10, 20), [
            (cx, cy - 9), (cx + 8, cy + 5), (cx - 8, cy + 5)
        ], 1)


# --------------------------------------------------------------------------- #
# Main game
# --------------------------------------------------------------------------- #
class Game:
    STATE_START = "start"
    STATE_PLAYING = "playing"
    STATE_GAMEOVER = "gameover"
    STATE_LEVEL_CLEAR = "level_clear"

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Galaxy Guardian")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.starfield = Starfield()
        self.state = self.STATE_START
        self.level = 1
        self.score = 0
        self.best_score = 0
        self._new_game(reset_score=True)
        self.level_clear_timer = 0

    def _new_game(self, reset_score=False):
        self.player = Player()
        self.formation = Formation(level=self.level)
        self.player_bullets = []
        self.enemy_bullets = []
        self.explosions = []
        if reset_score:
            self.score = 0
            self.level = 1

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            self._handle_events(now)
            self._update(dt, now)
            self._draw(now)
            pygame.display.flip()

    # ----------------------------------------------------------------- #
    def _handle_events(self, now):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.state == self.STATE_START and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = self.STATE_PLAYING
                elif self.state == self.STATE_GAMEOVER and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._new_game(reset_score=True)
                    self.state = self.STATE_PLAYING
                elif self.state == self.STATE_PLAYING and event.key == pygame.K_SPACE:
                    if self.player.can_shoot(now):
                        self.player_bullets.extend(self.player.shoot(now))

    # ----------------------------------------------------------------- #
    def _update(self, dt, now):
        self.starfield.update()

        if self.state != self.STATE_PLAYING:
            if self.state == self.STATE_LEVEL_CLEAR:
                self.level_clear_timer -= dt
                if self.level_clear_timer <= 0:
                    self.level += 1
                    self._new_game(reset_score=False)
                    self.state = self.STATE_PLAYING
            return

        self.player.update(pygame.key.get_pressed(), dt)

        for b in self.player_bullets:
            b.update()
        self.player_bullets[:] = [b for b in self.player_bullets if b.alive]

        for b in self.enemy_bullets:
            b.update()
        self.enemy_bullets[:] = [b for b in self.enemy_bullets if b.alive]

        self.formation.update(dt, self.player, self.enemy_bullets, None)

        for exp in self.explosions:
            exp.update(dt)
        self.explosions[:] = [e for e in self.explosions if e.alive]

        # player bullets vs enemies
        for b in self.player_bullets[:]:
            for e in self.formation.alive_enemies():
                if b.rect.colliderect(e.rect):
                    if b in self.player_bullets:
                        self.player_bullets.remove(b)
                    destroyed = e.take_hit()
                    if destroyed:
                        self.explosions.append(Explosion(e.x, e.y, big=(e.kind == "elite")))
                        self.score += e.score
                    else:
                        self.explosions.append(Explosion(b.x, b.y))
                    break

        # enemy bullets vs player
        for b in self.enemy_bullets[:]:
            if self.player.alive and b.rect.colliderect(self.player.rect):
                if b in self.enemy_bullets:
                    self.enemy_bullets.remove(b)
                if self.player.hit():
                    self.explosions.append(Explosion(self.player.x, self.player.y, big=True))

        # diving enemies colliding directly with the player
        for e in self.formation.alive_enemies():
            if e.diving and self.player.alive and e.rect.colliderect(self.player.rect):
                e.alive = False
                self.explosions.append(Explosion(e.x, e.y, big=True))
                if self.player.hit():
                    self.explosions.append(Explosion(self.player.x, self.player.y, big=True))

        # formation reaching the player's line -> game over
        if self.formation.lowest_y() > self.player.y - 30:
            self.player.alive = False

        if not self.player.alive:
            self.best_score = max(self.best_score, self.score)
            self.state = self.STATE_GAMEOVER

        elif not self.formation.alive_enemies():
            self.state = self.STATE_LEVEL_CLEAR
            self.level_clear_timer = 1800

    # ----------------------------------------------------------------- #
    def _draw(self, now):
        self.starfield.draw(self.screen)

        if self.state == self.STATE_START:
            self._draw_start_screen()
            return

        self.formation.draw(self.screen, now)

        for b in self.player_bullets:
            b.draw(self.screen)
        for b in self.enemy_bullets:
            b.draw(self.screen)
        for exp in self.explosions:
            exp.draw(self.screen)

        self.player.draw(self.screen)

        draw_health(self.screen, self.player.health, PLAYER_MAX_HEALTH)
        draw_text(self.screen, f"Score: {self.score}", 26, COL_UI_TEXT, (SCREEN_W - 90, 24))
        draw_text(self.screen, f"Level {self.level}", 20, COL_UI_ACCENT, (SCREEN_W // 2, 24))

        if self.state == self.STATE_LEVEL_CLEAR:
            draw_text(self.screen, "LEVEL CLEAR!", 46, COL_UI_ACCENT,
                      (SCREEN_W // 2, SCREEN_H // 2), bold=True, glow=True)
        elif self.state == self.STATE_GAMEOVER:
            self._draw_game_over_screen()

    def _draw_start_screen(self):
        draw_text(self.screen, "GALAXY GUARDIAN", 46, COL_UI_ACCENT,
                  (SCREEN_W // 2, SCREEN_H // 2 - 100), bold=True, glow=True)
        draw_text(self.screen, "Press ENTER to Start", 26, COL_UI_TEXT, (SCREEN_W // 2, SCREEN_H // 2))
        draw_text(self.screen, "A/D or Arrows - Move", 18, COL_UI_TEXT, (SCREEN_W // 2, SCREEN_H // 2 + 50))
        draw_text(self.screen, "SPACE - Shoot   ESC - Quit", 18, COL_UI_TEXT, (SCREEN_W // 2, SCREEN_H // 2 + 76))
        if self.best_score > 0:
            draw_text(self.screen, f"Best Score: {self.best_score}", 20, COL_UI_ACCENT,
                      (SCREEN_W // 2, SCREEN_H // 2 + 120))

    def _draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, "GAME OVER", 50, (255, 90, 90),
                  (SCREEN_W // 2, SCREEN_H // 2 - 60), bold=True, glow=True)
        draw_text(self.screen, f"Score: {self.score}", 28, COL_UI_TEXT, (SCREEN_W // 2, SCREEN_H // 2))
        draw_text(self.screen, f"Best: {self.best_score}", 22, COL_UI_ACCENT, (SCREEN_W // 2, SCREEN_H // 2 + 35))
        draw_text(self.screen, "Press ENTER to Restart", 20, COL_UI_TEXT, (SCREEN_W // 2, SCREEN_H // 2 + 80))


if __name__ == "__main__":
    Game().run()
   #698