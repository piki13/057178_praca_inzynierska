class Weapon:
    def __init__(self, w_modifier):
        self.modifier = w_modifier
        self.test_bonus = 0
        self.weapon_load = True

    def reload(self):
        self.weapon_load = True

    def aim(self):
        self.test_bonus += 10
