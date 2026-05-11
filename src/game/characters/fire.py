from src.game.characters.base import Character


class FireCharacter(Character):
    @classmethod
    def default_element(cls):
        return "fire"

    @classmethod
    def default_stats(cls):
        return {"hp": 25, "attack_power": 10}
