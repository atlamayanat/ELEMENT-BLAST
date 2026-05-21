from src.game.characters.fire import FireCharacter
from src.game.characters.cryo import CryoCharacter
from src.game.characters.electro import ElectroCharacter
from src.game.characters.hydro import HydroCharacter


class CharacterFactory:
    _registry = {
        "fire": FireCharacter,
        "cryo": CryoCharacter,
        "electro": ElectroCharacter,
        "hydro": HydroCharacter,
    }

    @classmethod
    def create(cls, element, name, ability_name, is_player, hp=None, attack_power=None, ai_strategy=None):
        from src.game.abilities import registry as ability_registry
        from src.game.ai import DefensiveAI

        char_cls = cls._registry.get(element)
        if char_cls is None:
            raise ValueError(
                f"Bilinmeyen element: {element}. "
                f"Desteklenen elementler: {sorted(cls._registry.keys())}"
            )
        defaults = char_cls.default_stats()
        ability = ability_registry.get(ability_name)
        if not is_player and ai_strategy is None:
            ai_strategy = DefensiveAI()
        return char_cls(
            name=name,
            ability=ability,
            hp=hp if hp is not None else defaults["hp"],
            attack_power=attack_power if attack_power is not None else defaults["attack_power"],
            is_player=is_player,
            ai_strategy=ai_strategy,
        )

    @classmethod
    def register(cls, element, character_class):
        cls._registry[element] = character_class
