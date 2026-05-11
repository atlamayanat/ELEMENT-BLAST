from src.game.characters.base import Character


class CryoCharacter(Character):
    @property
    def element(self):
        return "cryo"

    @classmethod
    def default_stats(cls):
        return {"hp": 28, "attack_power": 8}
