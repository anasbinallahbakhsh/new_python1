import pygame
import random
import sys

# ---------------- Setup ----------------
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Temple Run - Python Edition")
clock = pygame.time.Clock()