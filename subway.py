"""
SUBWAY SURFERS STYLE ENDLESS RUNNER
------------------------------------
A complete single-file game made with Python + Pygame only.
No external images / sounds are used - everything is drawn using
Pygame shapes (rectangles, circles) and text.

Controls:
    LEFT ARROW / A   -> move to left lane
    RIGHT ARROW / D  -> move to right lane
    SPACE            -> jump (avoids low barriers)
    R                -> restart after Game Over

Run with:  python subway_runner.py
"""

import pygame
import random
import sys

# ------------------------------------------------------------
# BASIC SETUP
# ------------------------------------------------------------
pygame.init()

WIDTH, HEIGHT = 420, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Runner")
clock = pygame.time.Clock()
FPS = 60

# Fonts
font_small = pygame.font.SysFont("arial", 22, bold=True)
font_medium = pygame.font.SysFont("arial", 32, bold=True)
font_big = pygame.font.SysFont("arial", 48, bold=True)

# Colors
SKY_TOP = (135, 206, 235)
SKY_BOTTOM = (200, 230, 245)
GROUND_COLOR = (60, 60, 70)
LANE_LINE_COLOR = (220, 220, 220)
PLAYER_COLOR = (255, 90, 60)
PLAYER_SKIN = (255, 205, 148)
TRAIN_COLOR = (40, 130, 200)
TRAIN_WINDOW = (220, 240, 255)
BARRIER_COLOR = (230, 180, 40)
POLICE_COLOR = (30, 40, 120)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
RED = (220, 30, 30)

# ------------------------------------------------------------
# LANE SETUP (3 lanes)
# ------------------------------------------------------------
LANE_COUNT = 3
LANE_WIDTH = WIDTH // LANE_COUNT
LANE_CENTERS = [LANE_WIDTH * i + LANE_WIDTH // 2 for i in range(LANE_COUNT)]

GROUND_Y = HEIGHT - 140      # where the player's feet stand
PLAYER_WIDTH = 46
PLAYER_HEIGHT = 70

# ------------------------------------------------------------
# GAME STATE VARIABLES (these get reset every time we restart)
# ------------------------------------------------------------
def reset_game():
    global player_lane, player_x, player_y, is_jumping, jump_velocity
    global obstacles, spawn_timer, spawn_interval, game_speed
    global score, game_state, catch_timer, police_x, bob_timer

    player_lane = 1                       # start in the middle lane
    player_x = LANE_CENTERS[player_lane]
    player_y = GROUND_Y
    is_jumping = False
    jump_velocity = 0

    obstacles = []          # each obstacle: {"lane", "y", "type"}
    spawn_timer = 0
    spawn_interval = 70     # frames between spawns (gets smaller = harder)
    game_speed = 6          # how fast obstacles move down the screen

    score = 0
    game_state = "PLAYING"  # PLAYING -> CAUGHT -> GAME_OVER
    catch_timer = 0
    police_x = -100
    bob_timer = 0


reset_game()

# ------------------------------------------------------------
# HELPER: draw a simple gradient sky background
# ------------------------------------------------------------
def draw_background():
    for i in range(HEIGHT):
        ratio = i / HEIGHT
        r = SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * ratio
        g = SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * ratio
        b = SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * ratio
        pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))

    # ground
    pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y + 60, WIDTH, HEIGHT - GROUND_Y - 60))

    # lane divider lines (moving stripes give a sense of speed)
    stripe_offset = (pygame.time.get_ticks() // 20) % 40
    for lane_edge in range(1, LANE_COUNT):
        x = lane_edge * LANE_WIDTH
        for y in range(-40 + stripe_offset, HEIGHT, 40):
            pygame.draw.line(screen, LANE_LINE_COLOR, (x, y), (x, y + 20), 3)


# ------------------------------------------------------------
# PLAYER
# ------------------------------------------------------------
def update_player():
    global player_x, is_jumping, jump_velocity, player_y, bob_timer

    # smoothly slide towards the target lane (nice visual effect)
    target_x = LANE_CENTERS[player_lane]
    player_x += (target_x - player_x) * 0.25

    # jumping physics (simple arc)
    if is_jumping:
        player_y += jump_velocity
        jump_velocity += 1.2          # gravity pulls back down
        if player_y >= GROUND_Y:
            player_y = GROUND_Y
            is_jumping = False
            jump_velocity = 0
    else:
        # small running "bob" animation while on the ground
        bob_timer += 1
        player_y = GROUND_Y


def get_player_rect():
    # while jumping, the player is higher up -> smaller collision box near ground
    top = player_y - PLAYER_HEIGHT - (GROUND_Y - player_y)
    return pygame.Rect(player_x - PLAYER_WIDTH // 2, top, PLAYER_WIDTH, PLAYER_HEIGHT)


def draw_player():
    bob = 4 * (1 if (bob_timer // 6) % 2 == 0 else -1) if not is_jumping else 0
    body_top = player_y - PLAYER_HEIGHT - (GROUND_Y - player_y) + bob

    # legs (simple animation - alternate leg positions)
    leg_offset = 6 if (bob_timer // 6) % 2 == 0 else -6
    pygame.draw.line(screen, BLACK, (player_x - 8, body_top + PLAYER_HEIGHT),
                      (player_x - 8 + leg_offset, body_top + PLAYER_HEIGHT + 18), 6)
    pygame.draw.line(screen, BLACK, (player_x + 8, body_top + PLAYER_HEIGHT),
                      (player_x + 8 - leg_offset, body_top + PLAYER_HEIGHT + 18), 6)

    # body
    pygame.draw.rect(screen, PLAYER_COLOR,
                      (player_x - PLAYER_WIDTH // 2, body_top, PLAYER_WIDTH, PLAYER_HEIGHT - 20),
                      border_radius=10)

    # head
    pygame.draw.circle(screen, PLAYER_SKIN, (int(player_x), int(body_top - 12)), 16)

    # arms
    pygame.draw.line(screen, PLAYER_COLOR, (player_x - PLAYER_WIDTH // 2, body_top + 10),
                      (player_x - PLAYER_WIDTH // 2 - 12, body_top + 30), 6)
    pygame.draw.line(screen, PLAYER_COLOR, (player_x + PLAYER_WIDTH // 2, body_top + 10),
                      (player_x + PLAYER_WIDTH // 2 + 12, body_top + 30), 6)


# ------------------------------------------------------------
# OBSTACLES (trains + low barriers)
# ------------------------------------------------------------
def spawn_obstacle():
    lane = random.randint(0, LANE_COUNT - 1)
    obstacle_type = random.choices(["train", "barrier"], weights=[70, 30])[0]
    obstacles.append({"lane": lane, "y": -150, "type": obstacle_type})


def update_obstacles():
    global spawn_timer, spawn_interval, game_speed

    spawn_timer += 1
    if spawn_timer >= spawn_interval:
        spawn_timer = 0
        spawn_obstacle()

    for obs in obstacles:
        obs["y"] += game_speed

    # remove obstacles that went off screen
    obstacles[:] = [o for o in obstacles if o["y"] < HEIGHT + 200]


def draw_obstacles():
    blink = (pygame.time.get_ticks() // 300) % 2 == 0

    for obs in obstacles:
        x_center = LANE_CENTERS[obs["lane"]]
        y = obs["y"]

        if obs["type"] == "train":
            train_w, train_h = LANE_WIDTH - 20, 150
            rect = pygame.Rect(x_center - train_w // 2, y, train_w, train_h)
            pygame.draw.rect(screen, TRAIN_COLOR, rect, border_radius=8)
            # windows
            for i in range(3):
                wx = rect.x + 12 + i * (train_w - 24) // 2
                pygame.draw.rect(screen, TRAIN_WINDOW, (wx, rect.y + 20, 24, 24), border_radius=4)
            # front warning lights (blinking)
            light_color = RED if blink else (120, 0, 0)
            pygame.draw.circle(screen, light_color, (rect.centerx, rect.y + train_h - 15), 6)

        else:  # barrier (low obstacle, jump over it)
            barrier_w, barrier_h = LANE_WIDTH - 30, 25
            rect = pygame.Rect(x_center - barrier_w // 2, y + 100, barrier_w, barrier_h)
            pygame.draw.rect(screen, BARRIER_COLOR, rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)

        obs["rect"] = rect
        obs["rect_type"] = obs["type"]


def check_collisions():
    global game_state, catch_timer

    player_rect = get_player_rect()

    for obs in obstacles:
        rect = obs.get("rect")
        if rect is None:
            continue

        if player_rect.colliderect(rect):
            if obs["type"] == "train":
                # trains always cause a collision (avoid by changing lane, not jump)
                game_state = "CAUGHT"
                catch_timer = 0
                return
            else:
                # barrier only hits the player if NOT jumping high enough
                if not is_jumping or player_y > GROUND_Y - 40:
                    game_state = "CAUGHT"
                    catch_timer = 0
                    return


# ------------------------------------------------------------
# POLICE OFFICER (chases the player after a collision)
# ------------------------------------------------------------
def draw_police(x, y):
    # legs animation
    leg_offset = 6 if (pygame.time.get_ticks() // 100) % 2 == 0 else -6
    pygame.draw.line(screen, BLACK, (x - 8, y + 50), (x - 8 + leg_offset, y + 68), 6)
    pygame.draw.line(screen, BLACK, (x + 8, y + 50), (x + 8 - leg_offset, y + 68), 6)

    # body
    pygame.draw.rect(screen, POLICE_COLOR, (x - 20, y, 40, 50), border_radius=8)
    # head
    pygame.draw.circle(screen, PLAYER_SKIN, (x, y - 14), 15)
    # police cap
    pygame.draw.rect(screen, BLACK, (x - 16, y - 28, 32, 10), border_radius=3)
    # badge
    pygame.draw.circle(screen, (255, 215, 0), (x, y + 15), 5)


# ------------------------------------------------------------
# SCORE / UI
# ------------------------------------------------------------
def draw_score():
    text = font_small.render(f"Score: {int(score)}", True, BLACK)
    screen.blit(text, (16, 16))


def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    title = font_big.render("GAME OVER", True, RED)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))

    score_text = font_medium.render(f"Final Score: {int(score)}", True, WHITE)
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))

    restart_text = font_small.render("Press R to Restart", True, WHITE)
    screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))


# ------------------------------------------------------------
# MAIN GAME LOOP
# ------------------------------------------------------------
def main():
    global player_lane, is_jumping, jump_velocity, score
    global game_state, catch_timer, police_x, game_speed, spawn_interval

    running = True
    while running:
        clock.tick(FPS)

        # ---------------- EVENTS ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_state == "PLAYING":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        if player_lane > 0:
                            player_lane -= 1
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if player_lane < LANE_COUNT - 1:
                            player_lane += 1
                    elif event.key == pygame.K_SPACE:
                        if not is_jumping:
                            is_jumping = True
                            jump_velocity = -18

                elif game_state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        reset_game()

        # ---------------- UPDATE ----------------
        if game_state == "PLAYING":
            update_player()
            update_obstacles()
            draw_background()
            draw_obstacles()
            draw_player()
            check_collisions()

            # score increases over time, difficulty ramps up slowly
            score += 0.5
            game_speed = 6 + score / 300           # gets faster over time
            spawn_interval = max(30, 70 - int(score / 50))

            draw_score()

        elif game_state == "CAUGHT":
            # short chase animation before showing the Game Over screen
            draw_background()
            draw_obstacles()
            draw_player()

            catch_timer += 1
            police_x += 10
            draw_police(min(police_x, player_x), player_y - PLAYER_HEIGHT)

            draw_score()

            if catch_timer > 45:
                game_state = "GAME_OVER"

        elif game_state == "GAME_OVER":
            draw_background()
            draw_obstacles()
            draw_player()
            draw_police(player_x, player_y - PLAYER_HEIGHT)
            draw_game_over()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()