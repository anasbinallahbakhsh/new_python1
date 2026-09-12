"""
game.py
-------
The Game class owns the state machine (start / playing / paused /
game-over), the main loop, all spawning logic for traffic / bus stops /
fuel stations, and collision detection. This is the "conductor" that
uses every other module.
"""

import random
import sys

import pygame

import settings as S
from entities import Bus, Vehicle, BusStop, FuelStation
from environment import Road, SceneryManager
from sound_manager import SoundManager
import ui


STATE_START = "start"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAMEOVER = "gameover"


class Game:
    """Top-level game object: run() starts the whole thing."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
        pygame.display.set_caption(S.GAME_TITLE)
        self.clock = pygame.time.Clock()

        self.fonts = ui.Fonts()
        self.sound = SoundManager()

        self.state = STATE_START#anas maik  on 
        self.running = True

        # --- menu buttons (created once, reused every screen) ---
        cx = S.SCREEN_WIDTH / 2
        self.start_button = ui.Button(cx, 500, 220, 60, "START DRIVING", self.fonts.medium)
        self.resume_button = ui.Button(cx, S.SCREEN_HEIGHT / 2, 220, 55, "RESUME", self.fonts.medium)
        self.pause_quit_button = ui.Button(cx, S.SCREEN_HEIGHT / 2 + 75, 220, 55, "QUIT", self.fonts.medium)
        self.restart_button = ui.Button(cx, 430, 220, 55, "PLAY AGAIN", self.fonts.medium)
        self.gameover_quit_button = ui.Button(cx, 500, 220, 55, "QUIT", self.fonts.medium)

        self.how_to_play_lines = [
            "ARROW KEYS / WASD to drive: accelerate, brake, steer left/right.",
            "Pull up to a BLUE bus stop and slow down to pick up passengers.",
            "Deliver them to a GREEN destination stop to score big points.",
            "Drive through a RED fuel pump to refill your tank.",
            "Avoid traffic! Colliding damages your bus. Don't run out of fuel.",
            "SPACE = horn   |   P / ESC = pause",
        ]

        self._new_game_state()

    # ----------------------------------------------------------------
    # (Re)initialize everything needed for a fresh playthrough
    # ----------------------------------------------------------------
    def _new_game_state(self):
        start_x = (S.LANE_CENTERS[2] + S.LANE_CENTERS[3]) / 2
        self.bus = Bus(start_x, S.BUS_SCREEN_Y)
        self.road = Road()
        self.scenery = SceneryManager()

        self.traffic = []
        self.stops = []
        self.fuel_stations = []

        self.traffic_spawn_timer = 1.0
        self.stop_spawn_timer = 3.0
        self.fuel_spawn_timer = 8.0
        self.stops_spawned = 0

        self.score = 0.0
        self.distance_m = 0.0
        self.passengers_delivered = 0
        self.game_over_reason = ""

    # ----------------------------------------------------------------
    # Main loop
    # ----------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(S.FPS) / 1000.0
            dt = min(dt, 0.05)  # avoid huge jumps if the window freezes briefly

            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # ----------------------------------------------------------------
    # Events
    # ----------------------------------------------------------------
    def _handle_events(self):
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

        mouse_pos = pygame.mouse.get_pos()

        if self.state == STATE_START:
            self.start_button.update(mouse_pos)
            if self.start_button.is_clicked(mouse_pos, mouse_click):
                self._start_new_game()

        elif self.state == STATE_PAUSED:
            self.resume_button.update(mouse_pos)
            self.pause_quit_button.update(mouse_pos)
            if self.resume_button.is_clicked(mouse_pos, mouse_click):
                self.state = STATE_PLAYING
            elif self.pause_quit_button.is_clicked(mouse_pos, mouse_click):
                self.running = False

        elif self.state == STATE_GAMEOVER:
            self.restart_button.update(mouse_pos)
            self.gameover_quit_button.update(mouse_pos)
            if self.restart_button.is_clicked(mouse_pos, mouse_click):
                self._start_new_game()
            elif self.gameover_quit_button.is_clicked(mouse_pos, mouse_click):
                self.running = False

    def _handle_keydown(self, key):
        if key == pygame.K_RETURN and self.state == STATE_START:
            self._start_new_game()

        elif key in (pygame.K_p, pygame.K_ESCAPE):
            if self.state == STATE_PLAYING:
                self.state = STATE_PAUSED
            elif self.state == STATE_PAUSED:
                self.state = STATE_PLAYING

        elif key == pygame.K_SPACE and self.state == STATE_PLAYING:
            self.sound.play("horn")

        elif key == pygame.K_RETURN and self.state == STATE_GAMEOVER:
            self._start_new_game()

    def _start_new_game(self):
        self._new_game_state()
        self.state = STATE_PLAYING
        self.sound.play("start")

    # ----------------------------------------------------------------
    # Update
    # ----------------------------------------------------------------
    def _update(self, dt):
        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        hit_curb = self.bus.update(dt, keys)
        if hit_curb and self.bus.take_damage(S.DAMAGE_CURB_HIT):
            self.sound.play("curb")

        scroll_speed_px = self.bus.speed * S.SPEED_TO_SCROLL

        self.road.update(dt, scroll_speed_px)
        self.scenery.update(dt, scroll_speed_px)

        self._update_traffic(dt, scroll_speed_px)
        self._update_stops(dt, scroll_speed_px)
        self._update_fuel_stations(dt, scroll_speed_px)

        self._handle_collisions()

        # distance & passive score
        forward_speed = max(0.0, self.bus.speed)
        self.distance_m += forward_speed / 3.6 * dt
        self.score += forward_speed / 3.6 * dt * S.SCORE_PER_METER

        self._check_game_over()

    def _difficulty(self):
        return min(1.0, self.distance_m / S.DIFFICULTY_RAMP_METERS)

    # --- traffic -----------------------------------------------------
    def _update_traffic(self, dt, scroll_speed_px):
        self.traffic_spawn_timer -= dt
        if self.traffic_spawn_timer <= 0 and len(self.traffic) < S.TRAFFIC_MAX_ON_SCREEN:
            self._spawn_traffic()
            diff = self._difficulty()
            lo = S.TRAFFIC_SPAWN_INTERVAL_MIN - 0.4 * diff
            hi = S.TRAFFIC_SPAWN_INTERVAL_MAX - 0.7 * diff
            self.traffic_spawn_timer = random.uniform(max(0.35, lo), max(0.6, hi))

        for v in self.traffic:
            v.update(dt, scroll_speed_px)
        self.traffic = [v for v in self.traffic if not v.is_off_screen()]

    def _spawn_traffic(self):
        lane_index = random.randrange(S.LANE_COUNT)
        lane_x = S.LANE_CENTERS[lane_index]
        is_oncoming = lane_x in S.ONCOMING_LANES
        diff = self._difficulty()
        speed = random.uniform(S.TRAFFIC_MIN_SPEED, S.TRAFFIC_MAX_SPEED + 25 * diff)
        y = -180.0
        self.traffic.append(Vehicle(lane_x, y, speed, is_oncoming))

    # --- bus stops -----------------------------------------------------
    def _update_stops(self, dt, scroll_speed_px):
        self.stop_spawn_timer -= dt
        if self.stop_spawn_timer <= 0:
            self._spawn_stop()
            self.stop_spawn_timer = random.uniform(S.STOP_SPAWN_INTERVAL_MIN, S.STOP_SPAWN_INTERVAL_MAX)

        for stop in self.stops:
            stop.update(dt, scroll_speed_px)
        self.stops = [s for s in self.stops if not s.is_off_screen()]

    def _spawn_stop(self):
        self.stops_spawned += 1
        is_destination = (self.stops_spawned % S.EVERY_NTH_STOP_IS_DESTINATION == 0)
        self.stops.append(BusStop(y=-160.0, is_destination=is_destination))

    # --- fuel stations -------------------------------------------------
    def _update_fuel_stations(self, dt, scroll_speed_px):
        self.fuel_spawn_timer -= dt
        if self.fuel_spawn_timer <= 0:
            self.fuel_stations.append(FuelStation(y=-160.0))
            self.fuel_spawn_timer = random.uniform(
                S.FUEL_STATION_SPAWN_INTERVAL_MIN, S.FUEL_STATION_SPAWN_INTERVAL_MAX
            )

        for f in self.fuel_stations:
            f.update(dt, scroll_speed_px)
        self.fuel_stations = [f for f in self.fuel_stations if not f.is_off_screen()]

    # --- collisions / interactions --------------------------------------
    def _handle_collisions(self):
        bus_rect = self.bus.get_rect()

        # traffic collisions
        for v in self.traffic:
            if bus_rect.colliderect(v.get_rect()):
                if self.bus.take_damage(S.DAMAGE_TRAFFIC_COLLISION):
                    self.sound.play("collision")

        # bus stop interactions (must be nearly stopped, touching the stop zone)
        is_slow_enough = abs(self.bus.speed) <= S.STOP_INTERACT_SPEED_THRESHOLD
        for stop in self.stops:
            if stop.served or not is_slow_enough:
                continue
            if not bus_rect.colliderect(stop.get_interact_rect()):
                continue

            if stop.is_destination:
                if self.bus.passengers > 0:
                    delivered = self.bus.unload_passengers()
                    self.score += delivered * S.SCORE_PER_DROPOFF
                    self.passengers_delivered += delivered
                    stop.served = True
                    self.sound.play("dropoff")
            else:
                boarded = self.bus.board_passengers(stop.waiting)
                if boarded > 0:
                    stop.waiting -= boarded
                    self.score += boarded * S.SCORE_PER_PICKUP
                    self.sound.play("pickup")
                    if stop.waiting <= 0:
                        stop.served = True

        # fuel station interactions (any speed, just drive through)
        for station in self.fuel_stations:
            if station.used:
                continue
            if bus_rect.colliderect(station.get_rect()):
                self.bus.refuel(S.FUEL_REFILL_AMOUNT)
                station.used = True
                self.sound.play("refuel")

    def _check_game_over(self):
        if self.bus.is_wrecked():
            self.game_over_reason = "Your bus was wrecked in a collision!"
            self._trigger_game_over()
        elif self.bus.is_out_of_fuel_and_stopped():
            self.game_over_reason = "You ran out of fuel!"
            self._trigger_game_over()

    def _trigger_game_over(self):
        self.state = STATE_GAMEOVER
        self.sound.play("gameover")

    # ----------------------------------------------------------------
    # Drawing
    # ----------------------------------------------------------------
    def _next_stop_hint(self):
        upcoming = [s for s in self.stops if not s.served and s.y < self.bus.y]
        if not upcoming:
            upcoming = [s for s in self.stops if not s.served]
        if not upcoming:
            return None
        nearest = min(upcoming, key=lambda s: abs(s.y - self.bus.y))
        meters_away = max(0, int(abs(nearest.y - self.bus.y) / 4))
        if nearest.is_destination:
            return f"Destination stop ahead ~{meters_away}m - pull over to drop off passengers"
        return f"Bus stop ahead ~{meters_away}m - pull over to pick up passengers"

    def _draw(self):
        if self.state == STATE_START:
            ui.draw_start_screen(self.screen, self.fonts, self.start_button, self.how_to_play_lines)
            return

        # playing / paused / gameover all show the game world underneath
        self.road.draw(self.screen)
        self.scenery.draw(self.screen)

        for station in self.fuel_stations:
            station.draw(self.screen, self.fonts.tiny)
        for stop in self.stops:
            stop.draw(self.screen, self.fonts.tiny)
        for v in self.traffic:
            v.draw(self.screen)

        self.bus.draw(self.screen)
        ui.draw_hud(self.screen, self.fonts, self.bus, self.score, self.distance_m,
                    self._next_stop_hint())

        if self.state == STATE_PAUSED:
            ui.draw_pause_screen(self.screen, self.fonts, self.resume_button, self.pause_quit_button)
        elif self.state == STATE_GAMEOVER:
            ui.draw_gameover_screen(
                self.screen, self.fonts, self.game_over_reason, self.score,
                self.distance_m, self.passengers_delivered,
                self.restart_button, self.gameover_quit_button
            )
