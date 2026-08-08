"""
SHADOW SYNC — Terminal-based puzzle game

Your shadow follows your position from 5 ticks ago.

Goal:
1. Reach Plate B.
2. Exactly 5 ticks later, reach Plate A.
3. Your shadow should then be on Plate B.
4. The door opens.
5. Reach the goal without touching your shadow.
"""

COLS, ROWS = 8, 8
DELAY = 5

START = (0, 0)
GOAL = (7, 7)

PLATE_B = (1, 1)
PLATE_A = (4, 3)

DOOR = (4, 4)


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player = list(START)
        self.history = [tuple(START)]
        self.tick = 0
        self.door_open = False
        self.won = False
        self.shadow = None
        self.message = ""

    def is_wall(self, x, y):
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return True

        # Horizontal wall at y=4, except the door at x=4
        if y == 4 and x != 4:
            return True

        # Door remains closed until both plates are active
        if (x, y) == DOOR and not self.door_open:
            return True

        return False

    def step(self, dx, dy):
        if self.won:
            return

        nx = self.player[0] + dx
        ny = self.player[1] + dy

        if not self.is_wall(nx, ny):
            self.player = [nx, ny]

        self.tick += 1
        self.history.append(tuple(self.player))

        self._update_shadow_and_door()
        self._check_collision()
        self._check_win()

    def _update_shadow_and_door(self):
        if self.tick >= DELAY:
            self.shadow = self.history[self.tick - DELAY]
        else:
            self.shadow = None

        if self.shadow and not self.door_open:
            player_pos = tuple(self.player)
            shadow_pos = self.shadow

            player_on_a = player_pos == PLATE_A
            player_on_b = player_pos == PLATE_B

            shadow_on_a = shadow_pos == PLATE_A
            shadow_on_b = shadow_pos == PLATE_B

            if (player_on_a and shadow_on_b) or (
                player_on_b and shadow_on_a
            ):
                self.door_open = True
                self.message = "Darwaza khul gaya! 🔓"

    def _check_collision(self):
        if self.shadow and tuple(self.player) == self.shadow:
            self.message = (
                "Shadow ne pakad liya! Level reset ho raha hai... 👻"
            )
            self.reset()

    def _check_win(self):
        if tuple(self.player) == GOAL:
            self.won = True
            self.message = "Tum jeet gaye! 🎉"

    def render(self):
        grid = []

        for y in range(ROWS):
            row = []

            for x in range(COLS):
                position = (x, y)

                if position == tuple(self.player):
                    cell = "P"
                elif self.shadow and position == self.shadow:
                    cell = "S"
                elif position == PLATE_A:
                    cell = "A"
                elif position == PLATE_B:
                    cell = "B"
                elif position == GOAL:
                    cell = "G"
                elif position == DOOR:
                    cell = "O" if self.door_open else "#"
                elif y == 4:
                    cell = "#"
                else:
                    cell = "."

                row.append(cell)

            grid.append(" ".join(row))

        print("\n" * 2)
        print("========== SHADOW SYNC ==========")
        print(f"Tick: {self.tick}")
        print(f"Door: {'OPEN 🔓' if self.door_open else 'CLOSED 🔒'}")
        print()
        print("\n".join(grid))
        print()
        print("P = Player | S = Shadow | A = Plate A")
        print("B = Plate B | O = Door | G = Goal")
        print()
        print(self.message)
        print()
        print("Controls: W = Up | S = Down | A = Left | D = Right")
        print("Q = Quit")


def main():
    game = Game()

    while not game.won:
        game.render()

        command = input("Move: ").strip().lower()

        if command == "q":
            print("Game closed.")
            break

        moves = {
            "w": (0, -1),
            "s": (0, 1),
            "a": (-1, 0),
            "d": (1, 0),
        }

        if command in moves:
            dx, dy = moves[command]
            game.step(dx, dy)
        else:
            game.message = "Invalid move! Use W, A, S, D or Q."

    if game.won:
        game.render()
        print("🎉 Congratulations! You completed Shadow Sync!")


if __name__ == "__main__":
    main()