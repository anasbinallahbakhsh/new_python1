import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futuristic Scanner")

clock = pygame.time.Clock()

BLACK = (5, 5, 5)
GREEN = (0, 255, 120)
DARK_GREEN = (0, 80, 40)

scan_y = 0

font = pygame.font.SysFont("consolas", 22)

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    # Grid
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y))

    # Scanner line
    pygame.draw.line(screen, GREEN, (0, scan_y), (WIDTH, scan_y), 3)

    glow = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
    glow.fill((0, 255, 120, 60))
    screen.blit(glow, (0, scan_y - 20))

    # Target box
    pygame.draw.rect(screen, GREEN, (250, 150, 300, 300), 2)

    # Crosshair
    pygame.draw.line(screen, GREEN, (400, 150), (400, 450), 1)
    pygame.draw.line(screen, GREEN, (250, 300), (550, 300), 1)

    # Status text
    text = font.render("SCANNING TARGET...", True, GREEN)
    screen.blit(text, (20, 20))

    scan_y += 2
    if scan_y > HEIGHT:
        scan_y = 0

    pygame.display.flip()

pygame.quit()
sys.exit()