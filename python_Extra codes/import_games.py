import pygame
import random
import math
import os
import sys

pygame.init()
pygame.mixer.init()

# ─── Window Setup ───────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎵 Music Visualizer Pro")
clock = pygame.time.Clock()

# ─── Fonts ──────────────────────────────────────────────────────────────────
font_large  = pygame.font.SysFont("segoeui", 28, bold=True)
font_medium = pygame.font.SysFont("segoeui", 20)
font_small  = pygame.font.SysFont("segoeui", 15)

# ─── Colors ─────────────────────────────────────────────────────────────────
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
GRAY       = (60, 60, 60)
DARK_GRAY  = (30, 30, 30)
CYAN       = (0, 220, 255)
PURPLE     = (180, 0, 255)
PINK       = (255, 60, 180)
GREEN      = (0, 255, 120)
ORANGE     = (255, 140, 0)

# ─── Visualizer Modes ───────────────────────────────────────────────────────
MODES = ["Bars", "Wave", "Circle", "Spectrum"]
mode_index = 0

# ─── Bar Data ────────────────────────────────────────────────────────────────
NUM_BARS = 64
bars      = [random.randint(30, 200) for _ in range(NUM_BARS)]
smoothed  = bars[:]

# ─── Music State ────────────────────────────────────────────────────────────
music_loaded  = False
paused        = False
song_name     = ""
volume        = 0.7
pygame.mixer.music.set_volume(volume)

# ─── UI Layout ───────────────────────────────────────────────────────────────
VIZ_TOP    = 100
VIZ_BOTTOM = HEIGHT - 110
VIZ_HEIGHT = VIZ_BOTTOM - VIZ_TOP
VIZ_LEFT   = 20
VIZ_RIGHT  = WIDTH - 20
VIZ_WIDTH  = VIZ_RIGHT - VIZ_LEFT

# ─── Helper: gradient color from position ───────────────────────────────────
def gradient_color(i, total, beat):
    t   = i / total
    r   = int(80 + 175 * math.sin(math.pi * t + beat * 0.05))
    g   = int(80 + 175 * math.sin(math.pi * t + beat * 0.05 + 2))
    b   = int(200 + 55  * math.sin(math.pi * t + beat * 0.05 + 4))
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

# ─── Draw: Bars ─────────────────────────────────────────────────────────────
def draw_bars(beat):
    bar_w = VIZ_WIDTH // NUM_BARS
    for i, h in enumerate(smoothed):
        x     = VIZ_LEFT + i * bar_w
        y     = VIZ_BOTTOM - int(h)
        color = gradient_color(i, NUM_BARS, beat)
        pygame.draw.rect(screen, color, (x + 1, y, bar_w - 2, int(h)))
        # Reflection
        ref_surf = pygame.Surface((bar_w - 2, int(h * 0.35)), pygame.SRCALPHA)
        ref_surf.fill((*color, 50))
        screen.blit(ref_surf, (x + 1, VIZ_BOTTOM))

# ─── Draw: Wave ─────────────────────────────────────────────────────────────
def draw_wave(beat):
    points = []
    step   = VIZ_WIDTH / NUM_BARS
    for i, h in enumerate(smoothed):
        x = int(VIZ_LEFT + i * step)
        y = int(VIZ_TOP + VIZ_HEIGHT // 2 - h * 0.6 * math.sin(i * 0.3 + beat * 0.04))
        points.append((x, y))
    if len(points) > 1:
        pygame.draw.lines(screen, CYAN, False, points, 3)
        # Glow
        glow_pts = [(p[0], p[1] + 3) for p in points]
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.lines(s, (0, 220, 255, 60), False, glow_pts, 6)
        screen.blit(s, (0, 0))

# ─── Draw: Circle ───────────────────────────────────────────────────────────
def draw_circle(beat):
    cx, cy = WIDTH // 2, VIZ_TOP + VIZ_HEIGHT // 2
    base_r = 80
    for i, h in enumerate(smoothed):
        angle  = (2 * math.pi / NUM_BARS) * i - math.pi / 2
        r_out  = base_r + h * 0.55
        x1     = cx + int(base_r  * math.cos(angle))
        y1     = cy + int(base_r  * math.sin(angle))
        x2     = cx + int(r_out   * math.cos(angle))
        y2     = cy + int(r_out   * math.sin(angle))
        color  = gradient_color(i, NUM_BARS, beat)
        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 3)
    pygame.draw.circle(screen, WHITE, (cx, cy), base_r, 1)

# ─── Draw: Spectrum ─────────────────────────────────────────────────────────
def draw_spectrum(beat):
    bar_w = VIZ_WIDTH // NUM_BARS
    for i, h in enumerate(smoothed):
        x     = VIZ_LEFT + i * bar_w
        mid_y = VIZ_TOP + VIZ_HEIGHT // 2
        color = gradient_color(i, NUM_BARS, beat)
        half  = int(h * 0.5)
        pygame.draw.rect(screen, color, (x + 1, mid_y - half, bar_w - 2, half * 2))

# ─── Draw: Top Bar (song info) ───────────────────────────────────────────────
def draw_top_bar():
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, 90))
    pygame.draw.line(screen, GRAY, (0, 90), (WIDTH, 90), 1)

    title = font_large.render("🎵 Music Visualizer Pro", True, WHITE)
    screen.blit(title, (20, 10))

    if song_name:
        name_surf = font_medium.render(f"♪  {song_name}", True, CYAN)
        screen.blit(name_surf, (20, 48))

    status = "⏸ Paused" if paused else ("▶ Playing" if music_loaded else "No song loaded")
    color  = ORANGE if paused else (GREEN if music_loaded else GRAY)
    stat   = font_medium.render(status, True, color)
    screen.blit(stat, (WIDTH - stat.get_width() - 20, 10))

    vol_text = font_small.render(f"Vol: {int(volume * 100)}%", True, WHITE)
    screen.blit(vol_text, (WIDTH - vol_text.get_width() - 20, 48))

    mode_text = font_small.render(f"Mode: {MODES[mode_index]}", True, PURPLE)
    screen.blit(mode_text, (WIDTH - mode_text.get_width() - 20, 68))

# ─── Draw: Bottom Controls ──────────────────────────────────────────────────
def draw_controls():
    pygame.draw.rect(screen, DARK_GRAY, (0, VIZ_BOTTOM + 10, WIDTH, HEIGHT - VIZ_BOTTOM - 10))
    pygame.draw.line(screen, GRAY, (0, VIZ_BOTTOM + 10), (WIDTH, VIZ_BOTTOM + 10), 1)

    controls = [
        ("SPACE", "Pause/Play"),
        ("M",     "Change Mode"),
        ("↑↓",   "Volume"),
        ("O",     "Open Song"),
        ("ESC",   "Quit"),
    ]
    total_w   = WIDTH - 40
    each_w    = total_w // len(controls)
    y_key     = VIZ_BOTTOM + 20
    y_label   = VIZ_BOTTOM + 45

    for idx, (key, label) in enumerate(controls):
        x    = 20 + idx * each_w + each_w // 2
        k_s  = font_medium.render(f"[{key}]", True, CYAN)
        l_s  = font_small.render(label, True, WHITE)
        screen.blit(k_s, (x - k_s.get_width() // 2, y_key))
        screen.blit(l_s, (x - l_s.get_width() // 2, y_label))

# ─── Animate bars ────────────────────────────────────────────────────────────
beat_counter = 0

def update_bars():
    global beat_counter
    beat_counter += 1
    for i in range(NUM_BARS):
        target     = random.randint(20, int(VIZ_HEIGHT * 0.85))
        bars[i]    = bars[i] * 0.75 + target * 0.25
        smoothed[i] = bars[i]

# ─── File dialog (simple fallback) ──────────────────────────────────────────
def open_file_dialog():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(
            title="Select MP3 / WAV file",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg"), ("All Files", "*.*")]
        )
        root.destroy()
        return path
    except Exception:
        return None

# ─── Load a song ─────────────────────────────────────────────────────────────
def load_song(path):
    global music_loaded, paused, song_name
    if not path:
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        music_loaded = True
        paused       = False
        song_name    = os.path.basename(path)
    except Exception as e:
        print(f"Error loading file: {e}")

# ─── Ask for initial song ────────────────────────────────────────────────────
print("Opening file picker…  (close it to type path manually)")
initial = open_file_dialog()
if not initial:
    initial = input("Enter MP3/WAV file path: ").strip().strip('"')
load_song(initial)

# ─── Main Loop ───────────────────────────────────────────────────────────────
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Pause / Play
            if event.key == pygame.K_SPACE and music_loaded:
                if paused:
                    pygame.mixer.music.unpause()
                    paused = False
                else:
                    pygame.mixer.music.pause()
                    paused = True

            # Change mode
            elif event.key == pygame.K_m:
                mode_index_local = MODES.index(MODES[mode_index])
                mode_index_ref   = (mode_index_local + 1) % len(MODES)
                globals().update(mode_index=mode_index_ref)

            # Volume up
            elif event.key == pygame.K_UP:
                volume = min(1.0, volume + 0.05)
                pygame.mixer.music.set_volume(volume)

            # Volume down
            elif event.key == pygame.K_DOWN:
                volume = max(0.0, volume - 0.05)
                pygame.mixer.music.set_volume(volume)

            # Open new song
            elif event.key == pygame.K_o:
                pygame.mixer.music.pause()
                path = open_file_dialog()
                if path:
                    load_song(path)
                elif music_loaded and not paused:
                    pygame.mixer.music.unpause()

            # Quit
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Update bars
    if not paused:
        update_bars()

    # Draw visualizer
    mode_name = MODES[mode_index]
    if mode_name == "Bars":
        draw_bars(beat_counter)
    elif mode_name == "Wave":
        draw_wave(beat_counter)
    elif mode_name == "Circle":
        draw_circle(beat_counter)
    elif mode_name == "Spectrum":
        draw_spectrum(beat_counter)

    draw_top_bar()
    draw_controls()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()