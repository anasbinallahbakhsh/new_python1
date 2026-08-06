"""
Temple Run Style Endless Runner Game
=====================================
Controls:
  LEFT ARROW  / A  -> Move to left lane
  RIGHT ARROW / D  -> Move to right lane
  UP ARROW    / W / SPACE -> Jump
  DOWN ARROW  / S  -> Slide (duck)
  R  -> Restart after Game Over
  ESC -> Quit

Requirements:
  pip install pygame
"""
p
import pygame
import random
import sys

# ---------------- Setup ----------------
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Temple Run - Python Edition")
clock = pygame.time.Clock()
FPS = 60

# Colors
SKY = (135, 206, 235)
GROUND = (139, 90, 60)
GROUND_DARK = (110, 70, 45)
PLAYER_COLOR = (220, 60, 60)
OBSTACLE_COLOR = (60, 60, 60)
COIN_COLOR = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SHADOW = (0, 0, 0, 100)

# Lanes (x positions of 3 lanes)
LANE_WIDTH = WIDTH // 3
LANES = [LANE_WIDTH // 2, LANE_WIDTH + LANE_WIDTH // 2, 2 * LANE_WIDTH + LANE_WIDTH // 2]

GROUND_Y = HEIGHT - 120

font_big = pygame.font.SysFont("Arial", 60, bold=True)
font_med = pygame.font.SysFont("Arial", 34, bold=True)
font_small = pygame.font.SysFont("Arial", 24)


class Player:
    def __init__(self):
        self.lane = 1  # 0=left, 1=mid, 2=right
        self.x = LANES[self.lane]
        self.width = 50
        self.height = 70
        self.normal_height = 70
        self.slide_height = 35

        self.y = GROUND_Y - self.height

        self.vel_y = 0
        self.is_jumping = False
        self.is_sliding = False
        self.slide_timer = 0

        self.gravity = 1.4
        self.jump_power = -22

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1

    def move_right(self):
        if self.lane < 2:
            self.lane += 1

    def jump(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_jumping = True
            self.vel_y = self.jump_power

    def slide(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_sliding = True
            self.slide_timer = 30
            self.height = self.slide_height

    def update(self):
        # Smooth horizontal movement toward target lane
        target_x = LANES[self.lane]
        self.x += (target_x - self.x) * 0.25

        # Jump physics
        if self.is_jumping:
            self.y += self.vel_y
            self.vel_y += self.gravity
            if self.y >= GROUND_Y - self.height:
                self.y = GROUND_Y - self.height
                self.is_jumping = False
                self.vel_y = 0
        else:
            self.y = GROUND_Y - self.height

        # Slide timer
        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False
                self.height = self.normal_height

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        # shadow
        shadow_rect = pygame.Rect(self.x - self.width // 2, GROUND_Y - 8, self.width, 10)
        pygame.draw.ellipse(surface, (0, 0, 0), shadow_rect)
        pygame.draw.rect(surface, PLAYER_COLOR, rect, border_radius=10)
        # simple face
        eye_y = rect.y + 12
        pygame.draw.circle(surface, WHITE, (rect.centerx - 8, eye_y), 5)
        pygame.draw.circle(surface, WHITE, (rect.centerx + 8, eye_y), 5)
        pygame.draw.circle(surface, BLACK, (rect.centerx - 8, eye_y), 2)
        pygame.draw.circle(surface, BLACK, (rect.centerx + 8, eye_y), 2)


class Obstacle:
    """Obstacle types: 'block' (jump over), 'bar' (slide under), 'gap' (visual only)"""

    def __init__(self, lane, kind, z):
        self.lane = lane
        self.kind = kind
        self.z = z  # distance from player (large = far away)
        self.passed = False

    def get_screen_pos(self):
        # Perspective scale based on z (closer = bigger, lower on screen)
        scale = max(0.15, 1 - self.z / 1000)
        x = LANES[self.lane]
        y = GROUND_Y - (self.z * 0.35)
        return x, y, scale

    def draw(self, surface):
        x, y, scale = self.get_screen_pos()
        if scale <= 0.16:
            return
        w = int(50 * scale)
        if self.kind == "block":
            h = int(60 * scale)
            rect = pygame.Rect(x - w // 2, y - h, w, h)
            pygame.draw.rect(surface, OBSTACLE_COLOR, rect, border_radius=6)
        elif self.kind == "bar":
            h = int(15 * scale)
            bar_y = y - int(80 * scale)
            rect = pygame.Rect(x - w // 2, bar_y, w, h)
            pygame.draw.rect(surface, (150, 100, 40), rect, border_radius=4)
            # posts
            pygame.draw.rect(surface, (100, 70, 30), (x - w // 2, bar_y, 6, int(80 * scale)))
            pygame.draw.rect(surface, (100, 70, 30), (x + w // 2 - 6, bar_y, 6, int(80 * scale)))

    def check_collision(self, player):
        x, y, scale = self.get_screen_pos()
        if scale < 0.55 or scale > 0.85:
            return False  # only check collision when close to player's depth
        if self.lane != player.lane:
            return False

        if self.kind == "block":
            # must jump over it
            if not player.is_jumping or player.y > GROUND_Y - 40:
                return True
        elif self.kind == "bar":
            # must slide under it
            if not player.is_sliding:
                return True
        return False


class Coin:
    def __init__(self, lane, z):
        self.lane = lane
        self.z = z
        self.collected = False

    def get_screen_pos(self):
        scale = max(0.15, 1 - self.z / 1000)
        x = LANES[self.lane]
        y = GROUND_Y - (self.z * 0.35) - int(40 * scale)
        return x, y, scale

    def draw(self, surface):
        x, y, scale = self.get_screen_pos()
        if scale <= 0.16:
            return
        r = max(3, int(12 * scale))
        pygame.draw.circle(surface, COIN_COLOR, (int(x), int(y)), r)
        pygame.draw.circle(surface, (200, 160, 0), (int(x), int(y)), r, 2)

    def check_collect(self, player):
        x, y, scale = self.get_screen_pos()
        if scale < 0.55 or scale > 0.85:
            return False
        if self.lane != player.lane:
            return False
        if player.is_jumping and player.y < GROUND_Y - 90:
            return False
        return True


def draw_background(surface, offset):
    surface.fill(SKY)
    # ground
    pygame.draw.rect(surface, GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    # lane dividers with scrolling effect
    for lane_x in [LANE_WIDTH, 2 * LANE_WIDTH]:
        for i in range(-1, 15):
            y = GROUND_Y + ((i * 40 + offset) % (HEIGHT - GROUND_Y + 40))
            pygame.draw.line(surface, GROUND_DARK, (lane_x, y), (lane_x, y + 20), 4)
    # simple sun
    pygame.draw.circle(surface, (255, 250, 200), (WIDTH - 80, 80), 40)


def spawn_wave(obstacles, coins):
    kind = random.choice(["block", "bar"])
    lane = random.randint(0, 2)
    obstacles.append(Obstacle(lane, kind, 900))

    # sometimes add coins in other lanes
    if random.random() < 0.6:
        coin_lane = random.choice([l for l in range(3) if l != lane])
        for i in range(3):
            coins.append(Coin(coin_lane, 900 + i * 40))


def main():
    player = Player()
    obstacles = []
    coins = []

    speed = 8
    max_speed = 22
    score = 0
    coin_count = 0
    running = True
    game_over = False
    spawn_timer = 0
    bg_offset = 0

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if not game_over:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        player.move_left()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        player.move_right()
                    elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                        player.jump()
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        player.slide()
                else:
                    if event.key == pygame.K_r:
                        return main()  # restart

        if not game_over:
            player.update()

            # Move obstacles & coins closer
            for obs in obstacles:
                obs.z -= speed
            for c in coins:
                c.z -= speed

            # Collision checks
            for obs in obstacles:
                if obs.check_collision(player):
                    game_over = True

            for c in coins:
                if not c.collected and c.check_collect(player):
                    c.collected = True
                    coin_count += 1
                    score += 10

            obstacles = [o for o in obstacles if o.z > -50]
            coins = [c for c in coins if c.z > -50 and not c.collected]

            # Spawn new obstacles periodically
            spawn_timer -= 1
            if spawn_timer <= 0:
                spawn_wave(obstacles, coins)
                spawn_timer = max(35, 70 - int(speed))

            # Increase difficulty
            speed = min(max_speed, speed + 0.002)
            score += 0.2
            bg_offset += speed

        # ---------------- Draw ----------------
        draw_background(screen, bg_offset)

        # sort by z so far things draw first (behind)
        for obs in sorted(obstacles, key=lambda o: -o.z):
            obs.draw(screen)
        for c in coins:
            c.draw(screen)

        player.draw(screen)

        # HUD
        score_text = font_med.render(f"Score: {int(score)}", True, BLACK)
        coin_text = font_small.render(f"Coins: {coin_count}", True, BLACK)
        screen.blit(score_text, (20, 20))
        screen.blit(coin_text, (20, 60))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            over_text = font_big.render("GAME OVER", True, (255, 60, 60))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 100))

            final_score = font_med.render(f"Final Score: {int(score)}", True, WHITE)
            screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 - 20))

            restart_text = font_small.render("Press R to Restart  |  ESC to Quit", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()


if __name__ == "__main__":
    main()