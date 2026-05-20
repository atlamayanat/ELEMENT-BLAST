from src.game.abilities.base import AbilityStrategy
from src.game.effects import FrozenStatus


class FreezeRayStrategy(AbilityStrategy):
    name = "freeze_ray"
    display_name = "Freeze Ray (tek hedef, 1 tur dondurur)"
    is_single_target = True

    def execute(self, engine, character, target_index):
        target = engine.resolve_single_target(character, target_index)
        if target is None:
            return
        damage = character.attack_power
        actual = target.take_damage(damage, source_element="cryo")
        engine.log.append(f"  ## {character.name} 'Freeze Ray' kullandi!")
        engine.announce_hit(character, target, actual)
        opp_team = engine.opponent_team_of(character)
        if target.hp > 0:
            opp_team.apply_effect_to(target, FrozenStatus)
            engine.log.append(f"  >> {target.name} 1 tur dondu (yetenek)")
