import numpy as np
import random


class GridManager:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.grid = np.full((grid_size, grid_size), None, dtype=object)

    def place_characters_on_grid(self, players, enemy):
        self.grid = np.full((self.grid_size, self.grid_size), None, dtype=object)

        alive_characters = [p for p in players if p.is_alive()] + ([enemy] if enemy.is_alive() else [])
        positions = []

        while len(positions) < len(alive_characters):
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            if all(abs(x - px) > 1 or abs(y - py) > 1 for px, py in positions):
                positions.append((x, y))

        for i, character in enumerate(alive_characters):
            x, y = positions[i]
            character.position = (x, y)
            self.grid[x, y] = character

        return self.grid

    def update_grid_state(self, players, enemy):

        self.grid = np.full((self.grid_size, self.grid_size), None, dtype=object)

        for character in players + [enemy]:
            if character.is_alive() and character.position:
                x, y = character.position
                self.grid[x, y] = character

        return self.grid

    def render_grid(self, title="", logs=None):

        cell_width = 5

        print("\n" + "=" * (self.grid_size * cell_width + 6))
        if title:
            print(f"{title.center(self.grid_size * cell_width + 6)}")
        print("=" * (self.grid_size * cell_width + 6))

        if logs:
            for log in logs:
                print(log)

        column_headers = " " * 4 + "".join(f"{i:>{cell_width}}" for i in range(0, self.grid_size))
        print(column_headers)

        for i, row in enumerate(self.grid):
            row_view = "".join(
                f"{f'P{cell.id}' if cell and not cell.is_enemy else 'E' if cell else '.':>{cell_width}}" for cell in row
            )
            print(f"{i:>2}  {row_view}")

        print("=" * (self.grid_size * cell_width + 6) + "\n")

    def visualize_grid(self, title="", logs=None):

        self.render_grid(title, logs)
