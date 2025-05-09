import math
from classes.battle_state import BattleState
from modyfications_dict import *
import copy


class Node:
    def __init__(self, state, strategy=None, parent=None):
        self.state = state
        self.strategy = strategy
        self.parent = parent
        self.stats = state.enemy_stats
        self.children = []
        self.n_visits = 0
        self.total_reward = 0
        self.modifications_list = modifications_list(self.strategy)
        self.debug_log = []
        self.is_terminal = False

    def log(self, description):
        self.debug_log.append(description)

    def expand(self, players, debug=False):

        debug and self.log(f"Rozwijanie węzła: {self.stats}, Dla strategii:{self.strategy}, "
                           f"Modyfikacje: {self.modifications_list}")

        for add_value, add_stat, sub_value, sub_stat in self.modifications_list:
            new_stats = self.stats.copy()

            new_add_stat = new_stats.get(add_stat, 0) + add_value
            new_sub_stat = new_stats.get(sub_stat, 0) - sub_value

            if new_add_stat <= stats_range[add_stat]["max"] and new_sub_stat >= stats_range[sub_stat]["min"]:

                new_stats[add_stat] = new_add_stat
                new_stats[sub_stat] = new_sub_stat

                new_players = copy.deepcopy(players)
                new_state = BattleState(new_stats, new_players)

                child_node = Node(new_state, strategy=self.strategy, parent=self)
                self.children.append(child_node)

                debug and self.log(f"Dodano dziecko: {add_stat}+{add_value}, {sub_stat}-{sub_value}")

        if not self.children:
            self.is_terminal = True

        if debug:
            print("\n".join(self.debug_log[-2:]))

    def best_child(self, exploration_weight):
        # Stworzenie listy węzłów potomnych, które są jeszcze możliwe do rozwinięcia.
        possible_children_to_exp = [child for child in self.children if not child.is_terminal]
        # W razie braku węzłów potomnych, zwracany jest aktualny węzeł - przerwie to pętle
        if not possible_children_to_exp:
            return self
        # Funkcja UCB1
        def ucb1(child):
            # Przyznaje nieodwiedzonemu węzłowi największą możliwą wartość(nieskńczoność),
            # aby nadać pierwszeństwo eksploracji
            if child.n_visits == 0:
                return float('inf')
            # Składnik eksploatacyjny będący średnią nagrodą przypadającą na wizytę
            exploitation = child.total_reward / child.n_visits
            # Składnik eksploracyjny będący pierwiastkiem z logarytmu naturalnego liczby wizyt aktualnego węzła,
            # podzielonego przez liczbę wizyt jego potomka, którego wagę określa stała eksploracji
            exploration = exploration_weight * math.sqrt(math.log(self.n_visits) / child.n_visits)
            return exploitation + exploration
        # Wśród możliwych do rozwinięć dzieci szukamy maksymalnej wartości
        # sumy składników: eksploatacyjnego i eksploracyjnego
        return max(possible_children_to_exp, key=ucb1)

    def update(self, reward):
        self.n_visits += 1
        self.total_reward += reward
