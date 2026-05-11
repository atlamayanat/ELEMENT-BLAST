from abc import ABC, abstractmethod


class Character(ABC):
    def __init__(self, name, ability_name, hp, attack_power, is_player):
        self.name = name
        self.element = self.default_element()
        self.ability_name = ability_name
        self.hp = hp
        self.max_hp = hp
        self.attack_power = attack_power
        self.is_player = is_player
        self.frozen_turns = 0

    @classmethod
    @abstractmethod
    def default_element(cls):
        ...

    @classmethod
    @abstractmethod
    def default_stats(cls):
        ...
