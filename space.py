"""
SPACE SHOOTER
A complete 2D space shooter game built with Python and Pygame.

Run with:  python space_shooter.py
"""

import pygame
import random
import math
import sys

# ----------------------------------------------------------------------
# INITIALIZATION
# ----------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

WIDTH = 900
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("consolas", 20)
FONT_MED = pygame.font.SysFont("consolas", 32, bold=True)
FONT_BIG = pygame.font.SysFont("consolas", 64, bold=True)

# ----------------------------------------------------------------------
# COLORS
# ----------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (80, 220, 255)
YELLOW = (255, 220, 60)
RED = (255, 70, 90)
GREEN = (100, 255, 130)
ORANGE = (255, 150, 60)
PURPLE = (170, 90, 255)
GRAY = (120, 130, 150)
DARK_BLUE = (10, 10, 35)

# ----------------------------------------------------------------------
# OPTIONAL SOUND LOADING (game works fine even if files are missing)
# ----------------------------------------------------------------------
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None


SHOOT_SOUND = load_sound("shoot.wav")
EXPLOSION_SOUND = load_sound("explosion.wav")
HIT_SOUND = load_sound("hit.wav")

try:
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.set_volume(0.4)
    MUSIC_LOADED = True
except Exception:
    MUSIC_LOADED = False


def play_sound(sound):
    if sound is not None:
        sound.play()


# ----------------------------------------------------------------------
# STAR (BACKGROUND)
# ----------------------------------------------------------------------
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(1, 4)
        self.size = random.randint(1, 3)
        self.color_val = random.randint(150, 255)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        c = (self.color_val, self.color_val, self.color_val)
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.size)


# ----------------------------------------------------------------------
# EXPLOSION EFFECT
# ----------------------------------------------------------------------
class Explosion:
    def __init__(self, x, y, color=ORANGE, particle_count=18):
        self.particles = []
        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 5)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(20, 40),
                "max_life": 40,
                "size": random.randint(2, 5),
                "color": color
            })
        self.done = False

    def update(self):
        alive_particles = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.05
            p["life"] -= 1
            if p["life"] > 0:
                alive_particles.append(p)
        self.particles = alive_particles
        if len(self.particles) == 0:
            self.done = True

    def draw(self, surface):
        for p in self.particles:
            alpha_ratio = max(p["life"] / p["max_life"], 0)
            size = max(1, int(p["size"] * alpha_ratio * 1.5))
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), size)


# ----------------------------------------------------------------------
# BULLET (PLAYER)
# ----------------------------------------------------------------------
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 14
        self.speed = 11
        self.rect = pygame.Rect(int(self.x - self.width / 2), int(self.y), self.width, self.height)

    def update(self):
        self.y -= self.speed
        self.rect.y = int(self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, CYAN, self.rect, border_radius=2)
        pygame.draw.rect(surface, WHITE, self.rect.inflate(-2, -6), border_radius=2)

    def is_off_screen(self):
        return self.y < -20


# ----------------------------------------------------------------------
# BULLET (ENEMY)
# ----------------------------------------------------------------------
class EnemyBullet:
    def __init__(self, x, y, vx=0, vy=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 5
        self.rect = pygame.Rect(int(x - self.radius), int(y - self.radius), self.radius * 2, self.radius * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 180, 180), (int(self.x), int(self.y)), self.radius, 1)

    def is_off_screen(self):
        return self.y > HEIGHT + 20 or self.x < -20 or self.x > WIDTH + 20


# ----------------------------------------------------------------------
# PLAYER
# ----------------------------------------------------------------------
class Player:
    def __init__(self):
        self.width = 50
        self.height = 46
        self.x = WIDTH // 2
        self.y = HEIGHT - 80
        self.speed = 7
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 14
        self.invulnerable_timer = 0
        self.invulnerable_time = 60  # frames of invulnerability after being hit
        self.rect = pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2),
                                 self.width, self.height)

    def handle_movement(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed

        # Keep player inside the window
        half_w = self.width / 2
        if self.x < half_w:
            self.x = half_w
        if self.x > WIDTH - half_w:
            self.x = WIDTH - half_w

        self.rect.x = int(self.x - self.width / 2)
        self.rect.y = int(self.y - self.height / 2)

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

    def can_shoot(self):
        return self.shoot_cooldown <= 0

    def shoot(self):
        self.shoot_cooldown = self.shoot_cooldown_max
        play_sound(SHOOT_SOUND)
        return Bullet(self.x, self.y - self.height / 2)

    def take_damage(self, amount):
        if self.invulnerable_timer <= 0:
            self.health -= amount
            self.invulnerable_timer = self.invulnerable_time
            play_sound(HIT_SOUND)
            if self.health < 0:
                self.health = 0
            return True
        return False

    def is_alive(self):
        return self.health > 0

    def draw(self, surface):
        # Flicker while invulnerable
        if self.invulnerable_timer > 0 and (self.invulnerable_timer // 4) % 2 == 0:
            return

        x, y = self.x, self.y
        w, h = self.width, self.height

        # engine flame
        flame_points = [
            (x - 8, y + h / 3),
            (x + 8, y + h / 3),
            (x, y + h / 3 + random.randint(14, 22))
        ]
        pygame.draw.polygon(surface, ORANGE, flame_points)
        pygame.draw.polygon(surface, YELLOW, [
            (x - 4, y + h / 3),
            (x + 4, y + h / 3),
            (x, y + h / 3 + random.randint(6, 12))
        ])

        # ship body
        body_points = [
            (x, y - h / 2),
            (x + w / 2, y + h / 4),
            (x + w / 5, y + h / 2),
            (x - w / 5, y + h / 2),
            (x - w / 2, y + h / 4),
        ]
        pygame.draw.polygon(surface, CYAN, body_points)
        pygame.draw.polygon(surface, (10, 90, 140), body_points, 2)

        # cockpit
        pygame.draw.ellipse(surface, (200, 240, 255), (x - 6, y - h / 4, 12, 16))

        # wings
        pygame.draw.polygon(surface, (30, 130, 190), [
            (x - w / 2, y + h / 4),
            (x - w / 2 - 10, y + h / 2 + 5),
            (x - w / 5, y + h / 2)
        ])
        pygame.draw.polygon(surface, (30, 130, 190), [
            (x + w / 2, y + h / 4),
            (x + w / 2 + 10, y + h / 2 + 5),
            (x + w / 5, y + h / 2)
        ])


# ----------------------------------------------------------------------
# ENEMY
# ----------------------------------------------------------------------
class Enemy:
    """
    enemy_type: 'basic', 'fast', 'strong'
    """
    def __init__(self, enemy_type, difficulty_speed_mult=1.0):
        self.type = enemy_type
        self.x = random.randint(40, WIDTH - 40)
        self.y = -40
        self.shoot_timer = random.randint(60, 180)

        if enemy_type == "basic":
            self.width = 36
            self.height = 32
            self.health = 1
            self.max_health = 1
            self.speed = random.uniform(1.5, 2.5) * difficulty_speed_mult
            self.score_value = 10
            self.color = GREEN
            self.shoot_chance_interval = (90, 200)

        elif enemy_type == "fast":
            self.width = 26
            self.height = 24
            self.health = 1
            self.max_health = 1
            self.speed = random.uniform(3.5, 5.0) * difficulty_speed_mult
            self.score_value = 15
            self.color = YELLOW
            self.shoot_chance_interval = (120, 240)

        else:  # strong
            self.width = 50
            self.height = 46
            self.health = 4
            self.max_health = 4
            self.speed = random.uniform(0.8, 1.4) * difficulty_speed_mult
            self.score_value = 30
            self.color = PURPLE
            self.shoot_chance_interval = (70, 150)

        # slight horizontal drift for basic/strong enemies
        self.drift_dir = random.choice([-1, 1])
        self.drift_amount = random.uniform(0.3, 1.0) if enemy_type != "fast" else 0

        self.rect = pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2),
                                 self.width, self.height)

    def update(self):
        self.y += self.speed
        self.x += self.drift_dir * self.drift_amount

        if self.x < self.width / 2 or self.x > WIDTH - self.width / 2:
            self.drift_dir *= -1

        self.rect.x = int(self.x - self.width / 2)
        self.rect.y = int(self.y - self.height / 2)

        self.shoot_timer -= 1

    def ready_to_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(*self.shoot_chance_interval)
            return True
        return False

    def shoot_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        speed = 4.5
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed
        return EnemyBullet(self.x, self.y, vx, vy)

    def take_damage(self, amount=1):
        self.health -= amount
        return self.health <= 0

    def is_off_screen(self):
        return self.y > HEIGHT + 60

    def draw(self, surface):
        x, y = self.x, self.y
        w, h = self.width, self.height

        points = [
            (x, y + h / 2),
            (x - w / 2, y - h / 3),
            (x - w / 5, y - h / 2),
            (x + w / 5, y - h / 2),
            (x + w / 2, y - h / 3),
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)

        # cockpit dot
        pygame.draw.circle(surface, WHITE, (int(x), int(y - h / 6)), 4)

        # health bar for tougher enemies
        if self.max_health > 1:
            bar_w = w
            bar_h = 5
            ratio = max(self.health / self.max_health, 0)
            bar_x = x - bar_w / 2
            bar_y = y - h / 2 - 12
            pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_w * ratio, bar_h))


# ----------------------------------------------------------------------
# GAME STATE / VARIABLES
# ----------------------------------------------------------------------
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

game_state = STATE_START

stars = [Star() for _ in range(120)]
player = None
bullets = []
enemy_bullets = []
enemies = []
explosions = []

score = 0
level = 1
enemy_spawn_timer = 0
enemy_spawn_interval = 70  # frames between spawns, decreases over time
difficulty_speed_mult = 1.0

LEVEL_UP_SCORE_STEP = 150  # every N points -> level up


# ----------------------------------------------------------------------
# GAME RESET
# ----------------------------------------------------------------------
def reset_game():
    global player, bullets, enemy_bullets, enemies, explosions
    global score, level, enemy_spawn_timer, enemy_spawn_interval, difficulty_speed_mult

    player = Player()
    bullets = []
    enemy_bullets = []
    enemies = []
    explosions = []

    score = 0
    level = 1
    enemy_spawn_timer = 0
    enemy_spawn_interval = 70
    difficulty_speed_mult = 1.0

    if MUSIC_LOADED:
        try:
            pygame.mixer.music.play(-1)
        except Exception:
            pass


# ----------------------------------------------------------------------
# ENEMY SPAWNING
# ----------------------------------------------------------------------
def spawn_enemy():
    roll = random.random()
    if roll < 0.55:
        enemy_type = "basic"
    elif roll < 0.85:
        enemy_type = "fast"
    else:
        enemy_type = "strong"

    enemies.append(Enemy(enemy_type, difficulty_speed_mult))


def update_difficulty():
    global level, enemy_spawn_interval, difficulty_speed_mult

    new_level = 1 + score // LEVEL_UP_SCORE_STEP
    if new_level != level:
        level = new_level

    # spawn interval shrinks as level increases, minimum cap so it's not impossible
    enemy_spawn_interval = max(18, 70 - (level - 1) * 5)

    # enemy speed multiplier grows slowly
    difficulty_speed_mult = 1.0 + (level - 1) * 0.12


# ----------------------------------------------------------------------
# COLLISION HANDLING
# ----------------------------------------------------------------------
def handle_collisions():
    global score

    # player bullets vs enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                destroyed = enemy.take_damage(1)
                if bullet in bullets:
                    bullets.remove(bullet)
                if destroyed:
                    explosions.append(Explosion(enemy.x, enemy.y, CYAN))
                    play_sound(EXPLOSION_SOUND)
                    score += enemy.score_value
                    if enemy in enemies:
                        enemies.remove(enemy)
                break  # bullet already used, stop checking other enemies

    # enemy bullets vs player
    for eb in enemy_bullets[:]:
        if eb.rect.colliderect(player.rect):
            player.take_damage(10)
            explosions.append(Explosion(eb.x, eb.y, RED, particle_count=10))
            if eb in enemy_bullets:
                enemy_bullets.remove(eb)

    # enemies colliding directly with player
    for enemy in enemies[:]:
        if enemy.rect.colliderect(player.rect):
            player.take_damage(20)
            explosions.append(Explosion(enemy.x, enemy.y, ORANGE))
            play_sound(EXPLOSION_SOUND)
            if enemy in enemies:
                enemies.remove(enemy)


# ----------------------------------------------------------------------
# DRAWING HELPERS
# ----------------------------------------------------------------------
def draw_background():
    screen.fill(DARK_BLUE)
    for star in stars:
        star.update()
        star.draw(screen)


def draw_hud():
    score_surf = FONT_SMALL.render(f"Score: {score}", True, WHITE)
    level_surf = FONT_SMALL.render(f"Level: {level}", True, WHITE)
    screen.blit(score_surf, (16, 14))
    screen.blit(level_surf, (16, 40))

    # health bar
    bar_x = WIDTH - 220
    bar_y = 16
    bar_w = 200
    bar_h = 22
    ratio = max(player.health / player.max_health, 0)

    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=6)
    health_color = GREEN if ratio > 0.5 else (YELLOW if ratio > 0.25 else RED)
    pygame.draw.rect(screen, health_color, (bar_x, bar_y, bar_w * ratio, bar_h), border_radius=6)
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=6)

    health_text = FONT_SMALL.render(f"Health: {max(player.health,0)}", True, WHITE)
    screen.blit(health_text, (bar_x, bar_y + bar_h + 4))


def draw_centered_text(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(surf, rect)


def draw_start_screen():
    draw_centered_text("SPACE SHOOTER", FONT_BIG, CYAN, HEIGHT // 2 - 140)
    draw_centered_text("Press ENTER to Start", FONT_MED, WHITE, HEIGHT // 2 - 50)
    draw_centered_text("A / D or Arrow Keys - Move", FONT_SMALL, GRAY, HEIGHT // 2 + 20)
    draw_centered_text("SPACE - Shoot", FONT_SMALL, GRAY, HEIGHT // 2 + 50)
    draw_centered_text("P - Pause", FONT_SMALL, GRAY, HEIGHT // 2 + 80)
    draw_centered_text("ESC - Quit", FONT_SMALL, GRAY, HEIGHT // 2 + 110)


def draw_pause_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    draw_centered_text("GAME PAUSED", FONT_BIG, YELLOW, HEIGHT // 2 - 30)
    draw_centered_text("Press P to Resume", FONT_MED, WHITE, HEIGHT // 2 + 40)


def draw_game_over_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    draw_centered_text("GAME OVER", FONT_BIG, RED, HEIGHT // 2 - 100)
    draw_centered_text(f"Final Score: {score}", FONT_MED, WHITE, HEIGHT // 2 - 20)
    draw_centered_text("Press R to Restart", FONT_SMALL, GRAY, HEIGHT // 2 + 40)
    draw_centered_text("Press ESC to Quit", FONT_SMALL, GRAY, HEIGHT // 2 + 70)


# ----------------------------------------------------------------------
# MAIN GAME LOOP
# ----------------------------------------------------------------------
def main():
    global game_state, enemy_spawn_timer

    running = True

    while running:
        clock.tick(FPS)

        # ---------------- EVENT HANDLING ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if game_state == STATE_START and event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = STATE_PLAYING

                elif game_state == STATE_PLAYING and event.key == pygame.K_p:
                    game_state = STATE_PAUSED

                elif game_state == STATE_PAUSED and event.key == pygame.K_p:
                    game_state = STATE_PLAYING

                elif game_state == STATE_GAME_OVER and event.key == pygame.K_r:
                    reset_game()
                    game_state = STATE_PLAYING

        keys = pygame.key.get_pressed()

        # ---------------- UPDATE ----------------
        if game_state == STATE_PLAYING:
            player.handle_movement(keys)
            player.update()

            if keys[pygame.K_SPACE] and player.can_shoot():
                bullets.append(player.shoot())

            for b in bullets:
                b.update()
            bullets[:] = [b for b in bullets if not b.is_off_screen()]

            for eb in enemy_bullets:
                eb.update()
            enemy_bullets[:] = [eb for eb in enemy_bullets if not eb.is_off_screen()]

            for enemy in enemies:
                enemy.update()
                if enemy.ready_to_shoot():
                    enemy_bullets.append(enemy.shoot_towards(player.x, player.y))
            enemies[:] = [e for e in enemies if not e.is_off_screen()]

            for exp in explosions:
                exp.update()
            explosions[:] = [e for e in explosions if not e.done]

            update_difficulty()

            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_interval:
                enemy_spawn_timer = 0
                spawn_enemy()

            handle_collisions()

            if not player.is_alive():
                game_state = STATE_GAME_OVER
                if MUSIC_LOADED:
                    try:
                        pygame.mixer.music.stop()
                    except Exception:
                        pass

        elif game_state != STATE_START:
            # still let explosions finish animating while paused / game over
            pass

        # ---------------- DRAW ----------------
        draw_background()

        if game_state == STATE_START:
            draw_start_screen()

        else:
            for enemy in enemies:
                enemy.draw(screen)
            for b in bullets:
                b.draw(screen)
            for eb in enemy_bullets:
                eb.draw(screen)
            for exp in explosions:
                exp.draw(screen)

            player.draw(screen)
            draw_hud()

            if game_state == STATE_PAUSED:
                draw_pause_screen()
            elif game_state == STATE_GAME_OVER:
                draw_game_over_screen()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()