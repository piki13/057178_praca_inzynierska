from classes.node import Node
from classes.battle_state import BattleState
import copy
import statistics
import math
from modyfications_dict import *


def test_battle(players, enemy_stats, graphic_mode, print_logs=False, num_simulations=100):
    wins_for_players = 0
    for _ in range(num_simulations):

        battle = BattleState(enemy_stats, players)
        result = battle.simulate_battle(print_logs)
        if result == 1:
            wins_for_players += 1

    win_rate = wins_for_players / num_simulations
    if graphic_mode:
        from GUI import OptimizeEnemyGUI
        OptimizeEnemyGUI.instance.root.after(0, lambda: OptimizeEnemyGUI.instance.finish_simulation(win_rate))
    return win_rate


def calculate_reward(simulation_results):
    total = len(simulation_results)
    failed = simulation_results.count(-1.0)

    if failed > 50:
        return 0.0

    valid_results = [r for r in simulation_results if r != -1.0]
    win_rate = sum(valid_results) / len(valid_results)
    reward = 1 - abs(0.5 - win_rate)

    penalty_factor = failed / total
    reward *= (1 - penalty_factor)

    return reward


def find_best_stats(node, players):
    best_stats_list = []
    best_stats = {}
    best_avg_reward = float('-inf')
    best_strategy = ''

    def search(n):
        nonlocal best_stats_list, best_avg_reward, best_strategy
        current_strategy = n.strategy if n.strategy else "Nieznany"
        if n.n_visits > 0:
            avg_reward = n.total_reward / n.n_visits
            if avg_reward > best_avg_reward:
                best_stats_list.clear()
                best_stats_list.append(n.state.enemy_stats)
                best_avg_reward = avg_reward
                best_strategy = current_strategy
            elif avg_reward == best_avg_reward:
                best_stats_list.append(n.state.enemy_stats)
        for child in n.children:
            search(child)

    search(node)
    if len(best_stats_list) > 1:
        print("Więcej niż 1 wynik o najwyższej nagrodzie, powtórne testowanie najlepszych wyników...")
        best_final_score = float('inf')

        for stats in best_stats_list:
            score = test_battle(players, stats, graphic_mode=False, num_simulations=1000)
            if abs(score - 0.5) < abs(best_final_score - 0.5):
                best_final_score = score
                best_stats = stats

    else:
        best_stats = best_stats_list[0]

    return best_stats, best_avg_reward, best_strategy


def mcts_optimize_enemy(players, iterations, simulations_per_node, graphic_mode, debug=False):
    # Główna funkcja algorytmu odpowiedzialna za optymalizację statystyk przeciwnika z pomocą metody MCTS
    from GUI import OptimizeEnemyGUI
    progress = 0
    logs = []
    stat_keys = ["weapon_skill", "ballistic_skill", "agility", "strength", "health", "movement",
                 "armor_and_toughness", "melee_weapon_mod", "ranged_weapon_mod"]

    # Skala statystyk zmienia się wraz z liczbą graczy - im więcej graczy tym wyższy mnożnik
    scale_factor = 1

    if len(players) == 2:
        scale_factor = 1.1
    elif len(players) == 3:
        scale_factor = 1.3
    elif len(players) == 4:
        scale_factor = 1.55

    avg_stats = {}
    # Wyliczenie bazowych statystyk przeciwnika dla korzenia
    # na podstawie przeskalowanej średniej ograniczonej do wartości maksymalnych
    for key in stat_keys:
        base_mean = statistics.mean([getattr(player, key) for player in players])
        scaled = math.ceil(base_mean * scale_factor)
        # Ograniczenie statystyk do wartości maksymalnych
        capped = max(stats_range[key]["min"], min(scaled, stats_range[key]["max"]))
        avg_stats[key] = capped

    # Inicjalizacja korzenia drzewa
    root = Node(BattleState(avg_stats, players))
    # Strategie bazowe
    strategies = ["Sniper", "Tank"]

    # Stworzenie dzieci korzenia – po jednej strategii
    for strategy in strategies:
        initial_stats = root.state.enemy_stats.copy()
        new_players = copy.deepcopy(players)
        new_state = BattleState(initial_stats, new_players)
        strategy_node = Node(new_state, strategy=strategy, parent=root)
        root.children.append(strategy_node)
    print("Rozpoczynam optymalizacje...\n")
    # Stworzenie
    for iteration in range(iterations):
        print(f"iteracja {iteration+1}/150")
        node = root
        if iteration % 15 == 0 and iteration >= 15 and graphic_mode:
            progress += 10
            OptimizeEnemyGUI.instance.root.after(0, lambda: OptimizeEnemyGUI.instance.update_progress(progress))

        # Faza selekcji
        while node.children:
            next_node = node.best_child(exploration_weight=0.9)
            if next_node == node:
                node.is_terminal = True
                break
            if next_node.is_terminal:
                break
            node = next_node

        # Faza ekspansji
        if not node.children:
            if not node.is_terminal:
                node.expand(players, debug)

        # Faza symulacji
        for child in node.children:
            if debug:
                logs.append(f"Symulacja dla statystyk: {child.state.enemy_stats}")
            simulation_results = []
            for _ in range(simulations_per_node):
                players_deep_cp = copy.deepcopy(child.state.players)
                fresh_battle_state = BattleState(child.state.enemy_stats.copy(), players_deep_cp)
                result = fresh_battle_state.simulate_battle()
                simulation_results.append(result)

            reward = calculate_reward(simulation_results)

            # Propagacja wstecz
            current_node = child
            while current_node is not None:
                current_node.update(reward)
                current_node = current_node.parent

    # Znajdywanie najlepszych statystyk
    best_stats, best_avg_reward, best_strategy = find_best_stats(root, players)

    print("\nNajlepsze statystyki:")
    print(f"Statystyki: {best_stats}, Średnia nagroda: {best_avg_reward:.4f}, Strategia: {best_strategy}")
    if debug:
        print("\n".join(logs[-2:]))

    return best_stats, best_avg_reward
