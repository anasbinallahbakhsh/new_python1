import math
import random
import sys
import pygame

# Mini Fantasy Platformer — inspired by the reference screenshot.
# Install: pip install pygame
# Run: python fantasy_platformer.py
# Controls: A/D or ←/→ to move, Space/W/↑ to jump, R to restart, Esc to quit.

pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moonlight Castle - Mini Platformer")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 22, bold=True)
SMALL = pygame.font.SysFont("consolas", 16, bold=True)

SKY_TOP = (20, 35, 100)
GRAVITY_UP, GRAVITY_DOWN, MAX_FALL_SPEED = 0.62, 0.12, 3.2
JUMP_POWER, SPEED = -13.5, 5.2
WORLD_WIDTH = 3100
random.seed(7)


def draw_gradient(surface):
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (
            int(SKY_TOP[0] * (1 - t) + 20 * t),
            int(SKY_TOP[1] * (1 - t) + 45 * t),
            int(SKY_TOP[2] * (1 - t) + 80 * t),
        )
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


def make_clouds():
    return [
        (random.randint(0, WORLD_WIDTH), random.randint(90, 310),
         random.randint(70, 150), random.randint(22, 42))
        for _ in range(32)
    ]


clouds = make_clouds()


def draw_background(cam):
    draw_gradient(screen)
    # Stars
    for i in range(100):
        wx = (i * 137 + 37) % WORLD_WIDTH
        sx = int(wx - cam * 0.18) % (WIDTH + 80) - 40
        sy = (i * 67 + 25) % 340
        twinkle = 150 + (i * 19 % 100)
        pygame.draw.circle(screen, (twinkle, twinkle, 255), (sx, sy), 1 + i % 2)

    # Lavender clouds
    for wx, y, w, h in clouds:
        sx = int(wx - cam * 0.28)
        if -w < sx < WIDTH + w:
            col = (100, 90, 190)
            pygame.draw.ellipse(screen, col, (sx, y, w, h))
            pygame.draw.ellipse(screen, (123, 100, 205), (sx + w * .18, y - h * .35, w * .55, h * .8))

    # Distant mountain layers
    for layer, color, factor, base in [
        (0, (38, 65, 130), .35, 420),
        (1, (32, 74, 125), .48, 475),
        (2, (22, 62, 105), .62, 520),
    ]:
        points = [(-100, HEIGHT)]
        for x in range(-100, WIDTH + 180, 100):
            wx = x + (cam * factor) % 200
            peak = base - (45 + ((x // 100 * 31 + layer * 13) % 110))
            points.extend([(x, base), (x + 50, peak), (x + 100, base)])
        points.append((WIDTH + 100, HEIGHT))
        pygame.draw.polygon(screen, color, points)

    # Moon
    moon_x = int(720 - cam * .10) % (WIDTH + 300) - 100
    pygame.draw.circle(screen, (80, 151, 226), (moon_x, 185), 94)
    pygame.draw.circle(screen, (124, 187, 244), (moon_x - 12, 174), 83)
    for cx, cy, r in [(moon_x - 35, 150, 10), (moon_x + 30, 205, 14), (moon_x + 14, 133, 7)]:
        pygame.draw.circle(screen, (105, 165, 225), (cx, cy), r)

    # Castle silhouette on a far cliff
    castle_x = int(770 - cam * .17)
    cliff = [(castle_x - 100, 455), (castle_x - 50, 400), (castle_x + 10, 420),
             (castle_x + 60, 350), (castle_x + 120, 400), (castle_x + 180, 330),
             (castle_x + 250, 410), (castle_x + 300, 455)]
    pygame.draw.polygon(screen, (34, 42, 104), cliff)
    pygame.draw.rect(screen, (35, 39, 99), (castle_x, 315, 230, 140))
    # Castle towers and pointed roofs
    towers = [(castle_x - 12, 285, 45, 120), (castle_x + 45, 245, 48, 160),
              (castle_x + 112, 205, 52, 200), (castle_x + 178, 275, 45, 130),
              (castle_x + 220, 310, 38, 100)]
    for tx, ty, tw, th in towers:
        pygame.draw.rect(screen, (39, 43, 108), (tx, ty, tw, th))
        pygame.draw.polygon(screen, (28, 32, 87), [(tx - 7, ty + 3), (tx + tw // 2, ty - 45), (tx + tw + 7, ty + 3)])
        for wy in range(ty + 22, ty + th - 8, 30):
            pygame.draw.rect(screen, (255, 178, 95), (tx + tw // 2 - 4, wy, 8, 13), border_radius=2)


def build_level():
    # x, y, width, height; gaps are intentional.
    platforms = [
        pygame.Rect(0, 470, 400, 45),
        pygame.Rect(470, 470, 300, 45),
        pygame.Rect(850, 420, 270, 45),
        pygame.Rect(1210, 470, 350, 45),
        pygame.Rect(1660, 410, 280, 45),
        pygame.Rect(2020, 470, 330, 45),
        pygame.Rect(2420, 420, 360, 45),
        pygame.Rect(2850, 470, 320, 45),
        pygame.Rect(1030, 330, 130, 18),
        pygame.Rect(1830, 300, 145, 18),
    ]
    spike_sets = [
        (pygame.Rect(190, 450, 100, 20), 6),
        (pygame.Rect(510, 450, 90, 20), 6),
        (pygame.Rect(900, 400, 90, 20), 6),
        (pygame.Rect(1310, 450, 105, 20), 7),
        (pygame.Rect(2110, 450, 90, 20), 6),
        (pygame.Rect(2510, 400, 90, 20), 6),
    ]
    coin_positions = [
        (110, 400), (350, 405), (550, 390), (720, 390), (920, 340),
        (1080, 285), (1280, 400), (1460, 400), (1750, 345), (1890, 245),
        (2160, 400), (2310, 400), (2510, 350), (2700, 350), (2940, 400)
    ]
    coins = [pygame.Rect(x, y, 20, 20) for x, y in coin_positions]
    return platforms, spike_sets, coins


platforms, spike_sets, coins = build_level()
player = pygame.Rect(70, 390, 34, 48)
vel_y = 0
on_ground = False
lives, score = 4, 0
invulnerable = 0
game_over = False
won = False


def reset_game():
    global platforms, spike_sets, coins, vel_y, on_ground, lives, score, invulnerable, game_over, won
    platforms, spike_sets, coins = build_level()
    player.topleft = (70, 390)
    vel_y, on_ground = 0, False
    lives, score, invulnerable = 4, 0, 0
    game_over, won = False, False


def draw_platform(rect, cam):
    r = rect.move(-int(cam), 0)
    if r.right < -20 or r.left > WIDTH + 20:
        return
    # rocky floating island
    pygame.draw.rect(screen, (49, 61, 91), (r.x, r.y + 13, r.w, r.h + 18), border_radius=9)
    pygame.draw.polygon(screen, (35, 43, 72), [
        (r.x + 8, r.y + 38), (r.x + 30, r.y + 57),
        (int(r.x + r.w * .30), r.y + 50), (int(r.x + r.w * .47), r.y + 64),
        (int(r.x + r.w * .72), r.y + 49), (r.right - 8, r.y + 35),
    ])
    pygame.draw.rect(screen, (64, 143, 76), (r.x, r.y, r.w, 17), border_radius=8)
    pygame.draw.rect(screen, (103, 181, 91), (r.x + 5, r.y + 2, max(0, r.w - 10), 7), border_radius=4)
    for gx in range(r.x + 12, r.right - 5, 32):
        pygame.draw.line(screen, (137, 204, 103), (gx, r.y + 4), (gx - 3, r.y - 4), 2)


def draw_spikes(rect, count, cam):
    r = rect.move(-int(cam), 0)
    if r.right < 0 or r.left > WIDTH:
        return
    step = r.w / count
    for i in range(count):
        x = r.x + i * step
        pygame.draw.polygon(screen, (225, 229, 239), [
            (x, r.bottom), (x + step, r.bottom), (x + step / 2, r.y)
        ])
        pygame.draw.line(screen, (155, 173, 205), (x + step / 2, r.y + 2), (x + step, r.bottom), 2)


def draw_coin(rect, cam):
    x, y = rect.centerx - int(cam), rect.centery
    pygame.draw.circle(screen, (255, 176, 20), (x, y), 12)
    pygame.draw.circle(screen, (255, 226, 79), (x, y), 8, 3)
    pygame.draw.line(screen, (255, 242, 156), (x, y - 5), (x, y + 5), 2)


def draw_player(rect, cam, frame):
    x, y = rect.x - int(cam), rect.y
    # shadow
    pygame.draw.ellipse(screen, (20, 32, 63), (x - 4, y + 43, 42, 8))
    # legs with running animation
    swing = int(math.sin(frame * .24) * 5)
    pygame.draw.line(screen, (28, 35, 60), (x + 12, y + 32), (x + 9 + swing, y + 44), 7)
    pygame.draw.line(screen, (28, 35, 60), (x + 23, y + 32), (x + 27 - swing, y + 43), 7)
    pygame.draw.ellipse(screen, (227, 232, 242), (x + 1 + swing, y + 39, 16, 7))
    pygame.draw.ellipse(screen, (227, 232, 242), (x + 22 - swing, y + 39, 16, 7))
    # red hoodie
    pygame.draw.rect(screen, (188, 55, 56), (x + 5, y + 15, 25, 22), border_radius=6)
    pygame.draw.rect(screen, (232, 82, 69), (x + 9, y + 17, 16, 15), border_radius=4)
    # arms
    pygame.draw.line(screen, (237, 174, 133), (x + 8, y + 21), (x + 1, y + 28), 7)
    pygame.draw.line(screen, (237, 174, 133), (x + 26, y + 21), (x + 32, y + 11), 7)
    # face and hair
    pygame.draw.ellipse(screen, (244, 190, 148), (x + 7, y, 23, 23))
    pygame.draw.polygon(screen, (83, 49, 40), [
        (x + 6, y + 11), (x + 7, y + 4), (x + 14, y - 1),
        (x + 24, y + 1), (x + 31, y + 8), (x + 26, y + 7),
        (x + 18, y + 10), (x + 12, y + 8)
    ])
    pygame.draw.circle(screen, (35, 32, 38), (x + 23, y + 12), 2)
    pygame.draw.line(screen, (154, 83, 71), (x + 20, y + 19), (x + 25, y + 19), 1)


def draw_bat(x, y, cam, frame):
    sx = int(x - cam)
    flap = int(math.sin(frame * .28) * 12)
    pygame.draw.polygon(screen, (54, 40, 90), [(sx, y + 8), (sx - 28, y - flap), (sx - 22, y + 16), (sx - 8, y + 12)])
    pygame.draw.polygon(screen, (54, 40, 90), [(sx + 2, y + 8), (sx + 30, y - flap), (sx + 23, y + 17), (sx + 9, y + 12)])
    pygame.draw.ellipse(screen, (91, 61, 126), (sx - 7, y, 17, 21))
    pygame.draw.circle(screen, (255, 86, 108), (sx - 2, y + 7), 2)
    pygame.draw.circle(screen, (255, 86, 108), (sx + 5, y + 7), 2)


def center_text(text, y, color=(255, 255, 255), size=34):
    f = pygame.font.SysFont("consolas", size, bold=True)
    img = f.render(text, True, color)
    screen.blit(img, (WIDTH // 2 - img.get_width() // 2, y))


frame = 0
running = True
while running:
    dt = clock.tick(60)
    frame += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                reset_game()

    keys = pygame.key.get_pressed()
    if not game_over and not won:
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        player.x += int(dx * SPEED)
        player.x = max(0, min(WORLD_WIDTH - player.width, player.x))

        # Horizontal collision
        for p in platforms:
            if player.colliderect(p):
                if dx > 0:
                    player.right = p.left
                elif dx < 0:
                    player.left = p.right

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
            vel_y = JUMP_POWER
            on_ground = False
        # Normal speed while rising; slow, floaty fall while coming down.
        if vel_y < 0:
            vel_y = min(0, vel_y + GRAVITY_UP)
        else:
            vel_y = min(MAX_FALL_SPEED, vel_y + GRAVITY_DOWN)
        player.y += int(vel_y)
        on_ground = False
        for p in platforms:
            if player.colliderect(p):
                if vel_y > 0:
                    player.bottom = p.top
                    on_ground = True
                elif vel_y < 0:
                    player.top = p.bottom
                vel_y = 0

        if invulnerable > 0:
            invulnerable -= 1

        hit_spikes = any(player.colliderect(s) for s, _ in spike_sets)
        fell = player.top > HEIGHT + 30
        if (hit_spikes or fell) and invulnerable == 0:
            lives -= 1
            player.topleft = (max(70, int(player.x - 100)), 360)
            vel_y = 0
            invulnerable = 75
            if lives <= 0:
                game_over = True

        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 100

        if player.x > WORLD_WIDTH - 130:
            won = True

    cam = max(0, min(WORLD_WIDTH - WIDTH, player.centerx - WIDTH * .34))
    draw_background(cam)

    for p in platforms:
        draw_platform(p, cam)
    for s, count in spike_sets:
        draw_spikes(s, count, cam)
    for c in coins:
        draw_coin(c, cam)

    # A flying bat near the castle section
    draw_bat(2260, 255 + int(math.sin(frame * .04) * 18), cam, frame)
    if invulnerable == 0 or frame % 8 < 4:
        draw_player(player, cam, frame)

    # HUD panels
    pygame.draw.rect(screen, (22, 36, 78), (12, 12, 185, 42), border_radius=10)
    pygame.draw.rect(screen, (106, 133, 204), (12, 12, 185, 42), 2, border_radius=10)
    screen.blit(FONT.render("♥ " * lives, True, (255, 83, 103)), (23, 18))
    pygame.draw.rect(screen, (22, 36, 78), (WIDTH - 205, 12, 193, 42), border_radius=10)
    pygame.draw.rect(screen, (106, 133, 204), (WIDTH - 205, 12, 193, 42), 2, border_radius=10)
    screen.blit(SMALL.render(f"SCORE {score:05d}", True, (255, 255, 255)), (WIDTH - 192, 25))
    screen.blit(FONT.render(f"🟡 COINS {score // 100}", True, (255, 218, 72)), (20, 64))
    screen.blit(SMALL.render("MOVE: A/D or ARROWS     JUMP: SPACE     RESTART: R", True, (225, 230, 255)), (20, HEIGHT - 28))

    if game_over:
        pygame.draw.rect(screen, (9, 13, 38), (0, 0, WIDTH, HEIGHT), 0)
        center_text("GAME OVER", 225, (255, 90, 112), 44)
        center_text("Press R to try again", 285, (255, 255, 255), 22)
    elif won:
        pygame.draw.rect(screen, (9, 13, 38), (0, 0, WIDTH, HEIGHT), 0)
        center_text("YOU REACHED THE CASTLE!", 220, (255, 225, 100), 32)
        center_text(f"Final score: {score}", 280, (255, 255, 255), 24)
        center_text("Press R to play again", 325, (220, 225, 255), 20)

    pygame.display.flip()

pygame.quit()
sys.exit()
