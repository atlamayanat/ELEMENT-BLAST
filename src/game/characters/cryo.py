from src.game.characters.base import Character


class CryoCharacter(Character):
    @classmethod
    def default_element(cls):
        return "cryo"

    @classmethod
    def default_stats(cls):
        return {"hp": 28, "attack_power": 8}
