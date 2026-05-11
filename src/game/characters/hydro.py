from src.game.characters.base import Character


class HydroCharacter(Character):
    @property
    def element(self):
        return "hydro"

    @classmethod
    def default_stats(cls):
        return {"hp": 30, "attack_power": 7}
