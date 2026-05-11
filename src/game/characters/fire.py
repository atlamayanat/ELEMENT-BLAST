from src.game.characters.base import Character


class FireCharacter(Character):
    @property
    def element(self):
        return "fire"

    @classmethod
    def default_stats(cls):
        return {"hp": 25, "attack_power": 10}
