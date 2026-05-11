from src.game.characters.base import Character


class ElectroCharacter(Character):
    @classmethod
    def default_element(cls):
        return "electro"

    @classmethod
    def default_stats(cls):
        return {"hp": 22, "attack_power": 11}
