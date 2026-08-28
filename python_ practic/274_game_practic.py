import pygame
import sys
import random

# Initialize game engine
pygame.init()

# Set up our game window constants like width, height
width, height = 800, 450
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pubg Lite")

# Load images
background_image = pygame.image.load("pubg_bg.png")
player_image = pygame.image.load("pubg_player.png")
enemy_image = pygame.image.load("pubg_enemy.png")
bullet_image = pygame.image.load("bullet.png")

# Set up player
player_rect = player_image.get_rect()
player_rect.topleft = (width // 2 - player_rect.width // 2, height - player_rect.height)
player_speed = 5

# Set up the enemy
enemy_rect = enemy_image.get_rect()
enemy_speed = 1
enemy_rect.topleft = (random.randint(0, width - enemy_rect.width), 0)

# Set up the bullet
bullet_rect = bullet_image.get_rect()
bullet_speed = 7
bullet_state = "ready"

# Game Loop
while True:
    for event in pygame.event.get() :
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get keyboard state
    keys = pygame.key.get_pressed()

    # Left and right key event logic
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < width:
        player_rect.x += player_speed

    # Event handling for shooting bullet
    if keys[pygame.K_SPACE] and bullet_state == "ready":
        bullet_state = "fire"
        bullet_rect.topleft = (
            player_rect.x + player_rect.width // 2 - bullet_rect.width // 2,
            player_rect.y
        )

    # Update bullet position
    if bullet_state == "fire":
        bullet_rect.y -= bullet_speed
        if bullet_rect.y < -8:
            bullet_state = "ready"

    # Update the enemy position
    enemy_rect.y += enemy_speed
    if enemy_rect.y > height:
        enemy_rect.topleft = (random.randint(0, width - enemy_rect.width), 0)

    # Bullet enemy collision detection
    if bullet_rect.colliderect(enemy_rect):
        bullet_state = "ready"
        bullet_rect.y = -100  # Move bullet out of view
        enemy_rect.topleft = (random.randint(0, width - enemy_rect.width), 0)

    # Drawing every game graphic on screen
    screen.blit(background_image, (0, 0))
    screen.blit(player_image, player_rect)
    screen.blit(enemy_image, enemy_rect)

    if bullet_state == "fire":
        screen.blit(bullet_image, bullet_rect)

    pygame.display.flip()  # Code hereG