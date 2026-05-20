from abc import ABC, abstractmethod


class Character(ABC):
    def __init__(self, name, ability, hp, attack_power, is_player, ai_strategy=None):
        self.name = name
        self.element = self.default_element()
        self.ability = ability
        self.hp = hp
        self.max_hp = hp
        self.attack_power = attack_power
        self.is_player = is_player
        self.ai_strategy = ai_strategy

    @classmethod
    @abstractmethod
    def default_element(cls):
        ...

    @classmethod
    @abstractmethod
    def default_stats(cls):
        ...

    def take_damage(self, amount, source_element=None):
        actual = max(0, amount)
        self.hp = max(0, self.hp - actual)
        return actual

    def tick(self):
        return []

    def should_skip_turn(self):
        return False

    def apply_effect(self, effect_factory):
        return effect_factory(self)

    def has_status(self, status_name):
        return False
