import random
import math
from classes.weapon import Weapon


def roll_dice(sides):
    return random.randint(1, sides)


class Character:
    def __init__(self, char_id, is_enemy, weapon_skill, ballistic_skill, agility, strength, health, movement,
                 armor_and_toughness, melee_weapon_mod, ranged_weapon_mod, battle_state=None):
        self.id = char_id
        self.is_enemy = is_enemy
        self.initiative = 0
        self.melee_weapon_mod = melee_weapon_mod
        self.ranged_weapon_mod = ranged_weapon_mod
        self.weapon_skill = weapon_skill
        self.ballistic_skill = ballistic_skill
        self.armor_and_toughness = armor_and_toughness
        self.strength = strength
        self.health = health
        self.max_health = health
        self.agility = agility
        self.movement = movement
        self.is_engaged = False
        self.position = None
        self.melee_weapon = Weapon(melee_weapon_mod)
        self.ranged_weapon = Weapon(melee_weapon_mod)
        self.battle_state = battle_state

    def is_alive(self):
        return self.health > 0

    def apply_damage(self, value, attacker):
        self.health -= value
        if self.is_enemy:
            self.battle_state.damage_from_players[attacker.id] += value

    def roll_initiative(self):
        self.initiative = self.agility + roll_dice(10)

    def skill_check(self, attribute_value):
        roll = roll_dice(100)
        # self.battle_state.log_action(f"Rzut:{roll} na {attribute_value}")
        return roll <= attribute_value

    def heal_to_max(self):
        self.health = self.max_health

    def move(self, dx, dy, grid):

        new_x, new_y = self.position[0] + dx, self.position[1] + dy

        if 0 <= new_x < grid.shape[0] and 0 <= new_y < grid.shape[1]:
            if grid[new_x, new_y] is None:
                grid[self.position] = None
                grid[(new_x, new_y)] = self
                self.position = (new_x, new_y)
                # self.battle_state.log_action(f"{self.id if not self.is_enemy else 'Przeciwnik'}
                # przesunął się na {self.position}")
                return True
        return False

    def move_away(self, enemy, max_steps, grid):

        self.melee_weapon.test_bonus = 0
        self.ranged_weapon.test_bonus = 0

        target_x, target_y = enemy.position

        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)
        ]

        for _ in range(max_steps):
            sorted_moves = sorted(directions, key=lambda d: -abs(self.position[0] + d[0] - target_x) - abs(
                self.position[1] + d[1] - target_y))

            for dx, dy in sorted_moves:
                if self.move(dx, dy, grid):
                    break
            else:
                break

        return self.position

    def move_to_enemy(self, enemy, max_steps, grid):

        self.melee_weapon.test_bonus = 0
        self.ranged_weapon.test_bonus = 0

        target_x, target_y = enemy.position

        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)
        ]

        for _ in range(max_steps):
            if self.distance_from_enemy(enemy) == 1:
                # self.battle_state.log_action(f"Gracz {self.id if not self.is_enemy else 'Przeciwnik'}
                # jest w zasięgu ataku – zatrzymuje ruch.")
                break

            sorted_moves = sorted(directions, key=lambda d: abs(self.position[0] + d[0] - target_x) + abs(
                self.position[1] + d[1] - target_y))

            for dx, dy in sorted_moves:
                if self.move(dx, dy, grid):
                    break
            else:
                break

        return self.position

    def defense(self, is_melee_attack=False):
        if self.weapon_skill > self.agility and is_melee_attack:
            if self.skill_check(self.weapon_skill):
                # self.battle_state.log_action(f"Gracz {self.id if not self.is_enemy else 'Przeciwnik'} sparował atak.")
                return True
        elif self.skill_check(self.agility):
            # self.battle_state.log_action(f"Gracz {self.id if not self.is_enemy else 'Przeciwnik'} uniknął ataku.")
            return True
        return False

    def reload(self):
        # self.battle_state.log_action(f"Gracz {self.id if not self.is_enemy else 'Przeciwnik'} przeładował broń.")
        self.ranged_weapon.reload()
        self.melee_weapon.test_bonus = 0
        self.ranged_weapon.test_bonus = 0

    def ranged_attack(self, enemy):
        # self.battle_state.log_action(f"{self.id if not self.is_enemy else 'Przeciwnik'} atakuje dystansowo")
        test_modifications = self.ranged_weapon.test_bonus
        if enemy.is_engaged:
            test_modifications -= 20
        attacked_successfully = self.skill_check(self.ballistic_skill + test_modifications)
        self.ranged_weapon.test_bonus = 0
        self.ranged_weapon.weapon_load = False
        if attacked_successfully and not enemy.defense():
            damage = max((roll_dice(10) + self.ranged_weapon.modifier - enemy.armor_and_toughness), 0)
            # self.battle_state.log_action(f"{self.id if not self.is_enemy else 'Przeciwnik'}
            # zadaje obrażenia: {damage} ")
            enemy.apply_damage(damage, self)

    def charge(self, enemy, grid):
        # self.battle_state.log_action(f"{self.id if not self.is_enemy else 'Przeciwnik'} szarżuje")
        self.move_to_enemy(enemy, self.movement * 2, grid)
        attacked_successfully = self.skill_check(self.weapon_skill + 20)

        if attacked_successfully and not enemy.defense(True):
            damage = max((roll_dice(10) + self.melee_weapon.modifier + self.strength - enemy.armor_and_toughness), 0)
            # self.battle_state.log_action(f"{self.id if not self.is_enemy else 'Przeciwnik'}
            # zadaje obrażenia: {damage} ")
            enemy.apply_damage(damage, self)

    def melee_attack(self, enemy):
        # self.battle_state.log_action(f"{self.id if not self.is_enemy else 'Przeciwnik'} atakuje wręcz")
        attacked_successfully = self.skill_check(self.weapon_skill + self.melee_weapon.test_bonus)
        self.melee_weapon.test_bonus = 0
        if attacked_successfully and not enemy.defense(True):
            damage = max((roll_dice(10) + self.melee_weapon.modifier + self.strength - enemy.armor_and_toughness), 0)
            # self.battle_state.log_action(f"{self.id if not self.is_enemy else 'Przeciwnik'}
            # zadaje obrażenia: {damage} ")
            enemy.apply_damage(damage, self)

    def distance_from_enemy(self, enemy):
        x1, y1 = self.position
        x2, y2 = enemy.position
        return max(abs(x1 - x2), abs(y1 - y2))

    def calculate_melee_weapon_ev(self, bonus=0):
        skill_with_bonus = self.weapon_skill + bonus + self.melee_weapon.test_bonus
        p_hit = min(max(skill_with_bonus / 100, 0), 1)
        damage = 5.5 + self.melee_weapon.modifier + self.strength
        return p_hit * damage

    def calculate_ranged_weapon_ev(self, enemy, bonus):
        skill_with_bonus = self.ranged_weapon.test_bonus + bonus + self.ballistic_skill
        if enemy.is_engaged:
            skill_with_bonus -= 20
        p_hit = min(max(skill_with_bonus / 100, 0), 1)
        damage = 5.5 + self.ranged_weapon.modifier
        return p_hit * damage

    def danger_factor(self, distance):
        distance = min(max(1, distance), 10)
        return ((10 / math.sqrt(max(1, self.armor_and_toughness))) * (1 / (distance + 1))
                * self.max_health / self.health)

    def get_closest_opponent(self, players):
        opponents = [p for p in players if p.is_alive()]

        return min(opponents, key=lambda o: self.distance_from_enemy(o))

    def check_possible_actions(self, weapon_load, test_bonus, distance):

        possible_actions = []
        if distance == 1:
            possible_actions += ["RETREAT", "AIM_MELEE_ATTACK"]
        else:
            possible_actions += ["RUN_TO", "RUN_AWAY"]
            if distance <= self.movement:
                possible_actions += ["MOVE_MELEE_ATTACK"]
            if 4 <= distance <= 2 * self.movement:
                possible_actions += ["CHARGE"]
            if weapon_load:
                if test_bonus == 0:
                    possible_actions += ["AIM_RANGED_ATTACK"]
                possible_actions += ["RANGED_ATTACK_MOVE_TO", "RANGED_ATTACK_MOVE_AWAY", "RANGED_ATTACK_RELOAD"]
            else:
                possible_actions += ["MOVE_AWAY_RELOAD", "MOVE_TO_RELOAD", "RELOAD_AIM", "RELOAD_RANGED_ATTACK"]
        return possible_actions

    def choose_best_actions(self, enemy, players):
        if not self.is_alive():
            print(f"Wywołana postać nie żyje. ID:{self.id}, health:{self.health} ")
            return None

        opponent = self.get_closest_opponent(players) if self.is_enemy else enemy
        distance_from_opponent = self.distance_from_enemy(opponent)

        possible_actions = self.check_possible_actions(self.ranged_weapon.weapon_load, self.ranged_weapon.test_bonus,
                                                       distance_from_opponent)

        expected_value_dict = {
            "RETREAT": -self.danger_factor(1 + self.movement),
            "AIM_MELEE_ATTACK": self.calculate_melee_weapon_ev(10) - self.danger_factor(distance_from_opponent),
            "RANGED_ATTACK_RELOAD": self.calculate_ranged_weapon_ev(enemy, 0) - self.danger_factor(
                distance_from_opponent),
            "RELOAD_RANGED_ATTACK": self.calculate_ranged_weapon_ev(enemy, 0) - self.danger_factor(
                distance_from_opponent),
            "AIM_RANGED_ATTACK": self.calculate_ranged_weapon_ev(enemy, 10) - self.danger_factor(
                distance_from_opponent),
            "CHARGE": self.calculate_melee_weapon_ev(20) - self.danger_factor(1),
            "MOVE_MELEE_ATTACK": self.calculate_melee_weapon_ev() - self.danger_factor(1),
            "RELOAD_AIM": -self.danger_factor(distance_from_opponent + self.movement),
            "RANGED_ATTACK_MOVE_TO": self.calculate_ranged_weapon_ev(enemy, 0) - self.danger_factor(
                distance_from_opponent - self.movement),
            "RANGED_ATTACK_MOVE_AWAY": self.calculate_ranged_weapon_ev(enemy, 0) - self.danger_factor(
                distance_from_opponent + self.movement),
            "MOVE_TO_RELOAD": -self.danger_factor(distance_from_opponent - self.movement),
            "MOVE_AWAY_RELOAD": -self.danger_factor(distance_from_opponent + self.movement),
            "RUN_TO": - self.danger_factor(1),
            "RUN_AWAY": - self.danger_factor(10)
        }

        next_action_params = {
            "RETREAT": (self.ranged_weapon.weapon_load, 0, self.movement),
            "AIM_MELEE_ATTACK": (self.ranged_weapon.weapon_load, 0, 1),
            "MOVE_MELEE_ATTACK": (self.ranged_weapon.weapon_load, 0, 1),
            "CHARGE": (self.ranged_weapon.weapon_load, 0, 1),
            "RELOAD_RANGED_ATTACK": (False, 0, distance_from_opponent),
            "RANGED_ATTACK_RELOAD": (True, 0, distance_from_opponent),
            "AIM_RANGED_ATTACK": (False, 0, distance_from_opponent),
            "RELOAD_AIM": (True, 10, distance_from_opponent),
            "RANGED_ATTACK_MOVE_TO": (False, 0, -self.movement),
            "RANGED_ATTACK_MOVE_AWAY": (False, 0, self.movement),
            "MOVE_TO_RELOAD": (True, 0, -self.movement),
            "MOVE_AWAY_RELOAD": (True, 0, self.movement),
            "RUN_TO": (self.ranged_weapon.weapon_load, 0, 1),
            "RUN_AWAY": (self.ranged_weapon.weapon_load, 0, 10)
        }

        best_action = None
        best_ev = float("-inf")

        for action in possible_actions:
            params = next_action_params.get(action)

            future_actions = self.check_possible_actions(*params) if params else []

            if future_actions:
                best_future_action = max(future_actions, key=lambda a: expected_value_dict.get(a, 0))
                max_ev = expected_value_dict.get(best_future_action, 0)
            else:
                best_future_action = None
                max_ev = 0

            expected_value = expected_value_dict.get(action, 0) + 0.8 * max_ev

            # self.battle_state.log_action(f"Akcja: {action}, EV: {expected_value_dict.get(action, 0)}")
            # self.battle_state.log_action(f"Możliwe następne: {future_actions},
            # Najlepsza:{best_future_action}, Max EV: {max_ev}")
            # self.battle_state.log_action(f"Razem (EV = {expected_value})\n")

            if expected_value > best_ev:
                best_ev = expected_value
                best_action = action

        # self.battle_state.log_action(f"\nNajlepsza akcja: {best_action} (EV = {best_ev})")
        return best_action

    def perform_best_action(self, best_action, enemy, grid):
        action_map = {
            "RETREAT": [
                lambda: self.move_away(enemy, self.movement, grid)
            ],
            "AIM_MELEE_ATTACK": [
                lambda: self.melee_weapon.aim(),
                lambda: self.melee_attack(enemy)
            ],
            "RANGED_ATTACK_RELOAD": [
                lambda: self.ranged_attack(enemy),
                lambda: self.reload()
            ],
            "RELOAD_RANGED_ATTACK": [
                lambda: self.reload(),
                lambda: self.ranged_attack(enemy)
            ],
            "AIM_RANGED_ATTACK": [
                lambda: self.ranged_weapon.aim(),
                lambda: self.ranged_attack(enemy)
            ],
            "CHARGE": [
                lambda: self.charge(enemy, grid)
            ],
            "MOVE_MELEE_ATTACK": [
                lambda: self.move_to_enemy(enemy, self.movement, grid),
                lambda: self.melee_attack(enemy)
            ],
            "RELOAD_AIM": [
                lambda: self.reload(),
                lambda: self.ranged_weapon.aim()
            ],
            "RANGED_ATTACK_MOVE_TO": [
                lambda: self.ranged_attack(enemy),
                lambda: self.move_to_enemy(enemy, self.movement, grid)
            ],
            "RANGED_ATTACK_MOVE_AWAY": [
                lambda: self.ranged_attack(enemy),
                lambda: self.move_away(enemy, self.movement, grid)
            ],
            "MOVE_TO_RELOAD": [
                lambda: self.move_to_enemy(enemy, self.movement, grid),
                lambda: self.reload()
            ],
            "MOVE_AWAY_RELOAD": [
                lambda: self.move_away(enemy, self.movement, grid),
                lambda: self.reload()
            ],
            "RUN_TO": [
                lambda: self.move_to_enemy(enemy, self.movement * 3, grid)
            ],
            "RUN_AWAY": [
                lambda: self.move_away(enemy, self.movement * 3, grid)
            ],
        }

        if best_action in action_map:
            for action_fn in action_map[best_action]:
                action_fn()
