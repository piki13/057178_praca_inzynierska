import random
from classes.character import Character
from classes.grid_manager import GridManager


class BattleState:
    def __init__(self, enemy_stats, players):
        self.enemy = Character(0, True, **enemy_stats)
        self.enemy_stats = enemy_stats
        self.enemy_target = random.choice(players)
        self.damage_from_players = {player.id: 0 for player in players}
        self.players = players
        self.order = []
        self.grid_manager = GridManager(grid_size=10)
        self.grid = None
        self.log = []
        self.round_counter = 0

    def get_reward(self):
        return 1 if not self.enemy.is_alive() else 0

    def log_action(self, description):
        self.log.append(description)

    def log_health(self):
        return [f"Gracz {p.id}: {p.health} HP" for p in self.players] + [f"Przeciwnik: {self.enemy.health} HP"]

    def roll_initiative(self):
        for character in self.players + [self.enemy]:
            character.roll_initiative()
        self.order = sorted(self.players + [self.enemy], key=lambda c: c.initiative, reverse=True)

    def is_terminal(self):
        return not self.enemy.is_alive() or all(not p.is_alive() for p in self.players)

    def prepare_battle(self, print_logs):
        self.enemy.heal_to_max()
        for player in self.players:
            player.heal_to_max()

        self.roll_initiative()
        self.grid = self.grid_manager.place_characters_on_grid(self.players, self.enemy)

        print_logs and self.log_action("=== Rozpoczęcie bitwy ===")
        print_logs and self.grid_manager.visualize_grid(title="Rozmieszczenie na początku gry")

    def update_enemy_target(self):
        alive_players = [p for p in self.players if p.is_alive()]
        if not alive_players:
            self.finish_battle()
            return

        weights = []

        for player in alive_players:
            distance = player.distance_from_enemy(self.enemy)
            distance_score = max(1, 10 - distance)
            damage_score = self.damage_from_players.get(player.id, 0)
            total_weight = distance_score + damage_score

            weights.append(total_weight)

        self.enemy_target = random.choices(alive_players, weights=weights, k=1)[0]

        return

    def execute_turn(self, character, print_logs):
        if character.is_enemy:
            self.update_enemy_target()
        target = self.enemy_target if character.is_enemy else self.enemy

        if not character.is_alive():
            print_logs and self.log_action(
                f"{'Przeciwnik' if character.is_enemy else f'Gracz {character.id}'} pominięty, ponieważ nie żyje.")
            return

        best_action = character.choose_best_actions(target, self.players)
        character.perform_best_action(best_action, target, self.grid)
        print_logs and self.log_action("=Koniec ruchu=")

    def execute_round(self, print_logs):

        print_logs and self.log_action(f"=== Runda {self.round_counter} ===")
        initial_log_length = len(self.log)

        for character in self.order:
            if self.is_terminal():
                break
            self.execute_turn(character, print_logs)

        new_logs = self.log[initial_log_length:]
        if new_logs and print_logs:
            print("\n".join(new_logs))

        if print_logs:
            print("\nStan zdrowia po rundzie:")

            for health_log in self.log_health():
                print(health_log)

        self.order = [c for c in self.order if c.is_alive()]
        self.grid = self.grid_manager.update_grid_state(self.players, self.enemy)

        print_logs and self.log_action(f"=== Pozycje po rundzie {self.round_counter} ===")
        print_logs and self.grid_manager.visualize_grid(title=f"Pozycje po rundzie {self.round_counter}")

    def finish_battle(self, print_logs=False):
        self.log_action("=== Koniec bitwy ===")
        winner = "Gracze wygrali!" if not self.enemy.is_alive() else "Przeciwnik wygrał!"
        self.log_action(f"Rezultat: {winner}")

        if print_logs:
            print("\n".join(self.log[-2:]))

    def simulate_battle(self, print_logs=False):
        max_rounds = 20
        self.enemy.battle_state = self
        for player in self.players:
            player.battle_state = self

        self.prepare_battle(print_logs)

        while not self.is_terminal() and self.round_counter < max_rounds:
            self.round_counter += 1
            self.execute_round(print_logs)
            if self.is_terminal():
                break
        print_logs and self.finish_battle(print_logs)
        if self.round_counter >= max_rounds and not self.is_terminal():
            return -1.0
        return self.get_reward()
