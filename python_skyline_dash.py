"""
SKYLINE DASH
An original 3-lane endless runner built with pure Python + Pygame.
All graphics are procedurally drawn shapes/gradients/particles - no external
assets, images, fonts, or sounds are used. All characters, vehicles and
environment art are original designs (not based on any existing game).

Controls:
    LEFT / A    - move to left lane
    RIGHT / D   - move to right lane
    UP / W / SPACE - jump
    DOWN / S    - slide / duck
    ENTER       - start game / restart after game over
    ESC         - quit

Run with:  python3 skyline_dash.py
"""

import pygame
import random
import math
import sys

# --------------------------------------------------------------------------
# SETUP
# --------------------------------------------------------------------------
pygame.init()

WIDTH, HEIGHT = 480, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skyline Dash")
clock = pygame.time.Clock()
FPS = 60

FONT_BIG = pygame.font.SysFont("arialrounded,arial,sans-serif", 64, bold=True)
FONT_MED = pygame.font.SysFont("arial,sans-serif", 34, bold=True)
FONT_SMALL = pygame.font.SysFont("arial,sans-serif", 22, bold=True)
FONT_TINY = pygame.font.SysFont("arial,sans-serif", 16)

# --------------------------------------------------------------------------
# COLOR PALETTE (bright, cartoon mobile-game style)
# --------------------------------------------------------------------------
SKY_TOP = (95, 200, 255)
SKY_BOTTOM = (200, 240, 255)
SUN = (255, 236, 130)
ROAD_COLOR = (70, 70, 82)
ROAD_EDGE = (235, 235, 240)
SIDEWALK = (188, 188, 198)
GRASS = (120, 200, 110)
LANE_LINE = (250, 220, 90)

PLAYER_SKIN = (255, 202, 150)
PLAYER_SHIRT = (255, 90, 90)
PLAYER_PANTS = (60, 90, 200)
PLAYER_HAIR = (70, 45, 35)
PLAYER_SHOE = (40, 40, 50)

WHITE = (255, 255, 255)
BLACK = (20, 20, 25)

# --------------------------------------------------------------------------
# PERSPECTIVE MATH
# --------------------------------------------------------------------------
HORIZON_Y = 190
BASE_Y = HEIGHT - 60          # y where scale == 1.0 (near the player)
PLAYER_FIXED_Y = HEIGHT - 175  # where the player sprite is drawn

LANE_HORIZON_X = [WIDTH / 2 - 14, WIDTH / 2, WIDTH / 2 + 14]
LANE_BASE_X = [WIDTH / 2 - 130, WIDTH / 2, WIDTH / 2 + 130]

ROAD_HALF_HORIZON = 40
ROAD_HALF_BASE = 220


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def depth_t(y):
    """0 at horizon, 1 at BASE_Y, can exceed 1 closer than base."""
    return (y - HORIZON_Y) / (BASE_Y - HORIZON_Y)


def scale_at(y):
    t = clamp(depth_t(y), 0, 3)
    return lerp(0.12, 1.0, min(t, 1.0)) + max(0, t - 1.0) * 0.9


def lane_x(lane, y):
    t = clamp(depth_t(y), 0, 1.4)
    tt = min(t, 1.0)
    x = lerp(LANE_HORIZON_X[lane], LANE_BASE_X[lane], tt)
    if t > 1.0:
        # extrapolate a bit further out for objects closer than BASE_Y
        x += (LANE_BASE_X[lane] - LANE_HORIZON_X[lane]) * (t - 1.0)
    return x


def road_edges(y):
    t = clamp(depth_t(y), 0, 1.4)
    tt = min(t, 1.0)
    half = lerp(ROAD_HALF_HORIZON, ROAD_HALF_BASE, tt)
    if t > 1.0:
        half += (ROAD_HALF_BASE - ROAD_HALF_HORIZON) * (t - 1.0)
    cx = lerp(WIDTH / 2, WIDTH / 2, tt)
    return cx - half, cx + half


# --------------------------------------------------------------------------
# HELPER DRAW FUNCTIONS
# --------------------------------------------------------------------------
def draw_vgradient(surf, rect, top_color, bottom_color):
    x, y, w, h = rect
    if h <= 0:
        return
    for i in range(h):
        t = i / h
        c = (
            int(lerp(top_color[0], bottom_color[0], t)),
            int(lerp(top_color[1], bottom_color[1], t)),
            int(lerp(top_color[2], bottom_color[2], t)),
        )
        pygame.draw.line(surf, c, (x, y + i), (x + w, y + i))


def draw_shadow_ellipse(surf, cx, cy, w, h, alpha=90):
    if w <= 1 or h <= 1:
        return
    s = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, alpha), (0, 0, w, h))
    surf.blit(s, (cx - w / 2, cy - h / 2))


def rounded_rect(surf, color, rect, radius=8):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def lighten(color, amount):
    return tuple(clamp(int(c + amount), 0, 255) for c in color)


def darken(color, amount):
    return lighten(color, -amount)


# --------------------------------------------------------------------------
# PARTICLES
# --------------------------------------------------------------------------
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "gravity")

    def __init__(self, x, y, vx, vy, life, color, size, gravity=0.0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        t = clamp(self.life / self.max_life, 0, 1)
        alpha = int(255 * t)
        size = max(1, int(self.size * t))
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
        surf.blit(s, (self.x - size, self.y - size))


particles = []


def spawn_dust(x, y, n=2):
    for _ in range(n):
        particles.append(Particle(
            x + random.uniform(-8, 8), y + random.uniform(-2, 2),
            random.uniform(-30, 30), random.uniform(-40, -10),
            random.uniform(0.25, 0.5), (230, 230, 220), random.uniform(3, 6),
            gravity=60))


def spawn_burst(x, y, color, n=26):
    for _ in range(n):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(80, 320)
        particles.append(Particle(
            x, y, math.cos(ang) * spd, math.sin(ang) * spd,
            random.uniform(0.4, 0.9), color, random.uniform(3, 7),
            gravity=200))


def spawn_sparkle(x, y):
    for _ in range(10):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(40, 140)
        particles.append(Particle(
            x, y, math.cos(ang) * spd, math.sin(ang) * spd,
            random.uniform(0.3, 0.6), (255, 225, 90), random.uniform(2, 4),
            gravity=-20))


# --------------------------------------------------------------------------
# BACKGROUND DECORATIONS (buildings, trees, lamps) - scroll using the same
# perspective system as obstacles but positioned off the road.
# --------------------------------------------------------------------------
class Decoration:
    def __init__(self, side, kind, y=None):
        self.side = side  # -1 left, 1 right
        self.kind = kind
        self.y = y if y is not None else HORIZON_Y
        self.seed = random.random()
        self.hue = random.choice([
            (255, 150, 150), (150, 200, 255), (255, 210, 130),
            (170, 230, 170), (230, 170, 240), (255, 235, 150)
        ])

    def update(self, dt, speed_mult):
        t = clamp(depth_t(self.y), 0.02, 3)
        dy = (40 + t * 260) * speed_mult * dt
        self.y += dy
        return self.y < HEIGHT + 260

    def draw(self, surf):
        t = clamp(depth_t(self.y), 0, 1.6)
        scale = scale_at(self.y)
        left_edge, right_edge = road_edges(self.y)
        base_x = left_edge - 26 * scale if self.side < 0 else right_edge + 26 * scale

        if self.kind == "building":
            w = 90 * scale
            h = (140 + 220 * self.seed) * scale
            x = base_x - w / 2 if self.side < 0 else base_x - w / 2
            top = self.y - h
            body_color = darken(self.hue, 20)
            rounded_rect(surf, body_color, (x, top, w, h), radius=int(4 * scale) + 1)
            # windows grid
            win_c = lighten(body_color, 70)
            cols = max(1, int(w // (14 * max(scale, 0.2))))
            rows = max(1, int(h // (18 * max(scale, 0.2))))
            for r in range(rows):
                for c in range(cols):
                    if (r + c + int(self.seed * 10)) % 3 == 0:
                        continue
                    wx = x + 6 * scale + c * (w - 12 * scale) / max(cols, 1)
                    wy = top + 8 * scale + r * (h - 16 * scale) / max(rows, 1)
                    ww = max(2, 6 * scale)
                    wh = max(2, 9 * scale)
                    pygame.draw.rect(surf, win_c, (wx, wy, ww, wh), border_radius=1)
            # rooftop block
            rounded_rect(surf, darken(body_color, 15), (x + w * 0.25, top - 14 * scale, w * 0.5, 14 * scale + 2))

        elif self.kind == "tree":
            trunk_w = 8 * scale
            trunk_h = 26 * scale
            x = base_x
            pygame.draw.rect(surf, (120, 80, 45), (x - trunk_w / 2, self.y - trunk_h, trunk_w, trunk_h))
            r = 26 * scale
            for dx, dy, rr in ((0, -trunk_h - r * 0.5, r), (-r * 0.6, -trunk_h - r * 0.2, r * 0.7),
                               (r * 0.6, -trunk_h - r * 0.2, r * 0.7)):
                pygame.draw.circle(surf, (70, 180, 90), (int(x + dx), int(self.y + dy)), max(2, int(rr)))
            pygame.draw.circle(surf, (95, 205, 115), (int(x - r * 0.15), int(self.y - trunk_h - r * 0.75)),
                                max(1, int(r * 0.5)))

        elif self.kind == "lamp":
            x = base_x
            pole_h = 70 * scale
            pygame.draw.rect(surf, (60, 60, 68), (x - 2 * scale, self.y - pole_h, 4 * scale, pole_h))
            arm_dir = 1 if self.side < 0 else -1
            arm_len = 18 * scale
            pygame.draw.line(surf, (60, 60, 68), (x, self.y - pole_h),
                              (x + arm_dir * arm_len, self.y - pole_h - 6 * scale), max(1, int(3 * scale)))
            glow_pos = (int(x + arm_dir * arm_len), int(self.y - pole_h - 6 * scale))
            s = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 240, 150, 90), (30, 30), max(3, int(14 * scale)))
            surf.blit(s, (glow_pos[0] - 30, glow_pos[1] - 30))
            pygame.draw.circle(surf, (255, 245, 190), glow_pos, max(2, int(5 * scale)))


decorations = []


def spawn_decoration_row():
    kinds_l = random.choice(["building", "building", "tree", "lamp"])
    kinds_r = random.choice(["building", "building", "tree", "lamp"])
    decorations.append(Decoration(-1, kinds_l, HORIZON_Y - random.uniform(0, 40)))
    decorations.append(Decoration(1, kinds_r, HORIZON_Y - random.uniform(0, 40)))


# --------------------------------------------------------------------------
# PLAYER - original cartoon runner character
# --------------------------------------------------------------------------
class Player:
    def __init__(self):
        self.lane = 1
        self.x = lane_x(1, PLAYER_FIXED_Y)
        self.display_lane = 1.0
        self.jumping = False
        self.jump_t = 0.0
        self.jump_dur = 0.62
        self.sliding = False
        self.slide_t = 0.0
        self.slide_dur = 0.5
        self.run_cycle = 0.0
        self.alive = True
        self.hit_flash = 0.0

    def move(self, d):
        self.lane = clamp(self.lane + d, 0, 2)

    def jump(self):
        if not self.jumping and not self.sliding:
            self.jumping = True
            self.jump_t = 0.0

    def slide(self):
        if not self.jumping and not self.sliding:
            self.sliding = True
            self.slide_t = 0.0

    def update(self, dt, speed_mult):
        self.display_lane += (self.lane - self.display_lane) * clamp(dt * 12, 0, 1)
        self.x = lane_x(self.display_lane, PLAYER_FIXED_Y)

        self.run_cycle += dt * (9 + speed_mult * 3)
        if int(self.run_cycle * 10) % 3 == 0 and not self.jumping:
            spawn_dust(self.x + random.uniform(-14, 14), PLAYER_FIXED_Y + 46)

        if self.jumping:
            self.jump_t += dt
            if self.jump_t >= self.jump_dur:
                self.jumping = False
                self.jump_t = 0.0
        if self.sliding:
            self.slide_t += dt
            if self.slide_t >= self.slide_dur:
                self.sliding = False
                self.slide_t = 0.0
        if self.hit_flash > 0:
            self.hit_flash -= dt

    def get_jump_height(self):
        if not self.jumping:
            return 0.0
        p = self.jump_t / self.jump_dur
        return math.sin(p * math.pi) * 128

    def bounding_state(self):
        """Returns whether player currently occupies the 'low' zone (can be
        hit by ground obstacles) and/or 'high' zone (can be hit by overhead
        obstacles)."""
        airborne = self.jumping and self.get_jump_height() > 34
        ducking = self.sliding
        return airborne, ducking

    def draw(self, surf):
        scale = 1.65
        jump_h = self.get_jump_height()
        base_x = self.x
        base_y = PLAYER_FIXED_Y - jump_h

        shadow_scale = clamp(1.0 - jump_h / 220, 0.35, 1.0)
        draw_shadow_ellipse(surf, base_x, PLAYER_FIXED_Y + 46, 70 * shadow_scale, 20 * shadow_scale, alpha=110)

        wobble = math.sin(self.run_cycle) if not self.jumping else 0
        flash = self.hit_flash > 0 and int(self.hit_flash * 20) % 2 == 0

        if self.sliding:
            self._draw_sliding(surf, base_x, base_y, scale, flash)
        else:
            self._draw_running(surf, base_x, base_y, scale, wobble, flash)

    def _limb_color(self, color, flash):
        return (255, 255, 255) if flash else color

    def _draw_running(self, surf, x, y, s, wobble, flash):
        skin = self._limb_color(PLAYER_SKIN, flash)
        shirt = self._limb_color(PLAYER_SHIRT, flash)
        pants = self._limb_color(PLAYER_PANTS, flash)
        shoe = self._limb_color(PLAYER_SHOE, flash)
        hair = self._limb_color(PLAYER_HAIR, flash)

        leg_swing = wobble * 16
        arm_swing = -wobble * 18

        # back leg
        pygame.draw.line(surf, pants, (x - 6 * s, y + 8 * s), (x - 6 * s - leg_swing, y + 34 * s), int(9 * s))
        pygame.draw.circle(surf, shoe, (int(x - 6 * s - leg_swing), int(y + 36 * s)), int(6 * s))
        # back arm
        pygame.draw.line(surf, shirt, (x - 9 * s, y - 4 * s), (x - 9 * s + arm_swing * 0.6, y + 16 * s), int(7 * s))
        pygame.draw.circle(surf, skin, (int(x - 9 * s + arm_swing * 0.6), int(y + 17 * s)), int(5 * s))

        # torso
        rounded_rect(surf, shirt, (x - 15 * s, y - 22 * s, 30 * s, 30 * s), radius=int(10 * s))
        pygame.draw.circle(surf, lighten(shirt, 25), (int(x), int(y - 12 * s)), int(6 * s))

        # front leg
        pygame.draw.line(surf, pants, (x + 6 * s, y + 8 * s), (x + 6 * s + leg_swing, y + 34 * s), int(9 * s))
        pygame.draw.circle(surf, shoe, (int(x + 6 * s + leg_swing), int(y + 36 * s)), int(6 * s))

        # head
        pygame.draw.circle(surf, skin, (int(x), int(y - 32 * s)), int(13 * s))
        pygame.draw.circle(surf, hair, (int(x - 1 * s), int(y - 40 * s)), int(12 * s))
        pygame.draw.rect(surf, hair, (x - 13 * s, y - 42 * s, 26 * s, 8 * s), border_radius=int(6 * s))
        # cap visor (original design element)
        rounded_rect(surf, self._limb_color((255, 210, 60), flash), (x - 2 * s, y - 36 * s, 20 * s, 7 * s), radius=3)
        # eye
        pygame.draw.circle(surf, BLACK, (int(x + 6 * s), int(y - 31 * s)), int(2 * s))

        # front arm
        pygame.draw.line(surf, shirt, (x + 9 * s, y - 4 * s), (x + 9 * s - arm_swing * 0.6, y + 16 * s), int(7 * s))
        pygame.draw.circle(surf, skin, (int(x + 9 * s - arm_swing * 0.6), int(y + 17 * s)), int(5 * s))

    def _draw_sliding(self, surf, x, y, s, flash):
        skin = self._limb_color(PLAYER_SKIN, flash)
        shirt = self._limb_color(PLAYER_SHIRT, flash)
        pants = self._limb_color(PLAYER_PANTS, flash)
        shoe = self._limb_color(PLAYER_SHOE, flash)
        hair = self._limb_color(PLAYER_HAIR, flash)
        y2 = y + 26 * s
        rounded_rect(surf, shirt, (x - 26 * s, y2 - 10 * s, 40 * s, 20 * s), radius=int(9 * s))
        pygame.draw.line(surf, pants, (x + 14 * s, y2), (x + 34 * s, y2 + 4 * s), int(9 * s))
        pygame.draw.circle(surf, shoe, (int(x + 34 * s), int(y2 + 4 * s)), int(6 * s))
        pygame.draw.line(surf, pants, (x - 6 * s, y2 + 6 * s), (x - 20 * s, y2 + 10 * s), int(9 * s))
        pygame.draw.circle(surf, shoe, (int(x - 20 * s), int(y2 + 10 * s)), int(6 * s))
        pygame.draw.circle(surf, skin, (int(x - 22 * s), int(y2 - 14 * s)), int(12 * s))
        pygame.draw.circle(surf, hair, (int(x - 23 * s), int(y2 - 21 * s)), int(11 * s))
        rounded_rect(surf, self._limb_color((255, 210, 60), flash),
                     (x - 34 * s, y2 - 17 * s, 18 * s, 6 * s), radius=3)
        pygame.draw.circle(surf, BLACK, (int(x - 16 * s), int(y2 - 15 * s)), int(2 * s))


# --------------------------------------------------------------------------
# OBSTACLES - original vehicles (cars, buses, taxis, vans) and hazards
# --------------------------------------------------------------------------
VEHICLE_TYPES = ["car", "taxi", "bus", "van"]


class Obstacle:
    def __init__(self, lane, kind, y=None):
        self.lane = lane
        self.kind = kind
        self.y = y if y is not None else HORIZON_Y
        self.passed = False
        self.hue = random.choice([
            (240, 90, 90), (90, 150, 240), (250, 190, 70), (120, 200, 130), (200, 120, 220)
        ])
        self.requires = "jump" if kind in VEHICLE_TYPES or kind == "cone" else "duck"

    def update(self, dt, speed_mult):
        t = clamp(depth_t(self.y), 0.02, 3)
        dy = (55 + t * 300) * speed_mult * dt
        self.y += dy
        return self.y < HEIGHT + 220

    def get_rect_scale(self):
        return scale_at(self.y)

    def draw(self, surf):
        s = self.get_rect_scale()
        x = lane_x(self.lane, self.y)
        y = self.y

        if self.kind in VEHICLE_TYPES:
            self._draw_vehicle(surf, x, y, s)
        elif self.kind == "cone":
            self._draw_cone(surf, x, y, s)
        elif self.kind == "sign":
            self._draw_sign(surf, x, y, s)

    def _draw_vehicle(self, surf, x, y, s):
        length = {"car": 60, "taxi": 62, "van": 76, "bus": 110}[self.kind]
        width = {"car": 40, "taxi": 42, "van": 46, "bus": 50}[self.kind]
        h = length * s
        w = width * s
        top = y - h
        body = self.hue
        draw_shadow_ellipse(surf, x, y + 4 * s, w * 1.1, 10 * s, alpha=100)

        rounded_rect(surf, darken(body, 30), (x - w / 2, top + h * 0.10, w, h * 0.92), radius=int(10 * s) + 1)
        rounded_rect(surf, body, (x - w / 2, top, w, h * 0.85), radius=int(12 * s) + 1)
        rounded_rect(surf, lighten(body, 35), (x - w * 0.42, top + 4 * s, w * 0.84, h * 0.22),
                     radius=int(6 * s) + 1)
        # windshield
        wcolor = (150, 210, 240)
        rounded_rect(surf, wcolor, (x - w * 0.36, top + h * 0.06, w * 0.72, h * 0.16), radius=int(4 * s) + 1)
        if self.kind == "bus":
            for i in range(4):
                wy = top + h * 0.30 + i * h * 0.14
                rounded_rect(surf, wcolor, (x - w * 0.42, wy, w * 0.84, h * 0.09), radius=2)
        elif self.kind == "taxi":
            rounded_rect(surf, (255, 210, 40), (x - w * 0.5, top + h * 0.32, w, h * 0.14))
            for i, cx in enumerate((-0.25, 0.25)):
                rounded_rect(surf, wcolor, (x + cx * w - w * 0.16, top + h * 0.34, w * 0.32, h * 0.14), radius=3)
        else:
            rounded_rect(surf, wcolor, (x - w * 0.4, top + h * 0.32, w * 0.8, h * 0.16), radius=3)

        # headlight strip near bottom-front (toward viewer)
        pygame.draw.rect(surf, (255, 245, 200), (x - w * 0.44, y - h * 0.06, w * 0.2, h * 0.05))
        pygame.draw.rect(surf, (255, 245, 200), (x + w * 0.24, y - h * 0.06, w * 0.2, h * 0.05))
        # wheels
        wheel_r = max(2, w * 0.11)
        for wx in (x - w * 0.42, x + w * 0.42):
            pygame.d