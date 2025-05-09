from classes.character import Character
from mcts_optimize_enemy_stats import mcts_optimize_enemy, test_battle
import random
import statistics
import copy

player1 = Character(
    char_id=1, is_enemy=False, weapon_skill=60, ballistic_skill=22, agility=25, strength=4, health=10, movement=3,
    armor_and_toughness=2, melee_weapon_mod=2, ranged_weapon_mod=-2
)

player2 = Character(
    char_id=2, is_enemy=False, weapon_skill=28, ballistic_skill=60, agility=35, strength=2, health=9, movement=5,
    armor_and_toughness=2, melee_weapon_mod=-1, ranged_weapon_mod=1
)

player3 = Character(
    char_id=3, is_enemy=False, weapon_skill=45, ballistic_skill=45, agility=45, strength=3, health=12, movement=4,
    armor_and_toughness=3, melee_weapon_mod=0, ranged_weapon_mod=0
)

player4 = Character(
    char_id=4, is_enemy=False, weapon_skill=35, ballistic_skill=50, agility=60, strength=2, health=8, movement=6,
    armor_and_toughness=1, melee_weapon_mod=-2, ranged_weapon_mod=2
)

player5 = Character(
    char_id=5, is_enemy=False, weapon_skill=46, ballistic_skill=22, agility=34, strength=5, health=16, movement=3,
    armor_and_toughness=5, melee_weapon_mod=2, ranged_weapon_mod=2
)

player6 = Character(
    char_id=6, is_enemy=False, weapon_skill=65, ballistic_skill=27, agility=25, strength=4, health=14, movement=3,
    armor_and_toughness=3, melee_weapon_mod=1, ranged_weapon_mod=-2
)

player7 = Character(
    char_id=7, is_enemy=False, weapon_skill=37, ballistic_skill=35, agility=65, strength=1, health=10, movement=6,
    armor_and_toughness=1, melee_weapon_mod=-2, ranged_weapon_mod=1
)

player8 = Character(
    char_id=8, is_enemy=False, weapon_skill=40, ballistic_skill=46, agility=30, strength=3, health=13, movement=5,
    armor_and_toughness=2, melee_weapon_mod=0, ranged_weapon_mod=0
)

player9 = Character(
    char_id=9, is_enemy=False, weapon_skill=55, ballistic_skill=25, agility=40, strength=5, health=11, movement=4,
    armor_and_toughness=4, melee_weapon_mod=2, ranged_weapon_mod=-1
)

player10 = Character(
    char_id=10, is_enemy=False, weapon_skill=25, ballistic_skill=65, agility=52, strength=1, health=9, movement=5,
    armor_and_toughness=1, melee_weapon_mod=1, ranged_weapon_mod=2
)

players = [player1, player2, player3, player4, player5, player6, player7, player8, player9, player10]

for _ in range(5):
    print(f"Próba:{_+1}")
    k = 4
    drawn_players = copy.deepcopy(random.sample(players, k))
    print("Wylosowani gracze:")
    for player in drawn_players:
        print(f"Gracz {player.id}")
    optimal_enemy_stats, reward = mcts_optimize_enemy(drawn_players, iterations=150, simulations_per_node=100,
                                                      graphic_mode=False, debug=False)
    win_rate_list = []
    print(f"Współczynniki wygranych graczy: ")
    for i in range(10):
        win_rate = test_battle(drawn_players, optimal_enemy_stats, graphic_mode=False, print_logs=False,
                               num_simulations=1000)
        print(f"{win_rate:.2f},")
        win_rate_list.append(win_rate)
    print(f"\nŚrednia:{statistics.mean(win_rate_list):.2f}")
