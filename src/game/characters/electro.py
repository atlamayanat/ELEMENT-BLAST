from src.game.characters.base import Character


class ElectroCharacter(Character):
    @property
    def element(self):
        return "electro"

    @classmethod
    def default_stats(cls):
        return {"hp": 22, "attack_power": 11}
