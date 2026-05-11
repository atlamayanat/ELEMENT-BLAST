from src.game.characters.base import Character


class HydroCharacter(Character):
    @classmethod
    def default_element(cls):
        return "hydro"

    @classmethod
    def default_stats(cls):
        return {"hp": 30, "attack_power": 7}
