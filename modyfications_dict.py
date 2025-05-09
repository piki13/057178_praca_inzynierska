def modifications_list(strategy):
    if strategy == "Tank":
        return tank_modifications
    elif strategy == "Sniper":
        return sniper_modifications


stats_range = {
    "weapon_skill": {"min": 10, "max": 80},
    "ballistic_skill": {"min": 10, "max": 80},
    "agility": {"min": 10, "max": 80},
    "health": {"min": 8, "max": 25},
    "strength": {"min": 1, "max": 8},
    "movement": {"min": 3, "max": 8},
    "armor_and_toughness": {"min": 1, "max": 7},
    "melee_weapon_mod": {"min": -4, "max": 4},
    "ranged_weapon_mod": {"min": -4, "max": 4},
}
input_stats_range = {
    "weapon_skill": {"min": 20, "max": 65},
    "ballistic_skill": {"min": 20, "max": 65},
    "agility": {"min": 20, "max": 65},
    "strength": {"min": 1, "max": 5},
    "health": {"min": 8, "max": 16},
    "movement": {"min": 3, "max": 6},
    "armor_and_toughness": {"min": 1, "max": 5},
    "melee_weapon_mod": {"min": -2, "max": 2},
    "ranged_weapon_mod": {"min": -2, "max": 2},
}
tank_modifications = [
    (5, "weapon_skill", 5, "ballistic_skill"),
    (5, "weapon_skill", 5, "agility"),
    (14, "weapon_skill", 1, "movement"),
    (9, "weapon_skill", 1, "ranged_weapon_mod"),
    (1, "health", 4, "ballistic_skill"),
    (1, "health", 4, "agility"),
    (1, "health", 4, "ranged_weapon_mod"),
    (1, "armor_and_toughness", 12, "agility"),
    (1, "armor_and_toughness", 12, "ballistic_skill"),
    (1, "armor_and_toughness", 1, "movement"),
    (1, "strength", 1, "movement"),
    (1, "strength", 10, "ballistic_skill"),
    (1, "strength", 10, "agility"),
    (1, "strength", 1, "ranged_weapon_mod"),
]
sniper_modifications = [
    (5, "ballistic_skill", 5, "weapon_skill"),
    (9, "ballistic_skill", 5, "melee_weapon_mod"),
    (10, "ballistic_skill", 1, "strength"),
    (1, "ranged_weapon_mod", 9, "weapon_skill"),
    (1, "ranged_weapon_mod", 1, "melee_weapon_mod"),
    (1, "ranged_weapon_mod", 1, "strength"),
    (1, "health", 4, "weapon_skill"),
    (2, "health", 1, "melee_weapon_mod"),
    (2, "health", 1, "strength"),
    (5, "agility", 5, "weapon_skill"),
    (9, "agility", 5, "melee_weapon_mod"),
    (10, "agility", 1, "strength"),
]
