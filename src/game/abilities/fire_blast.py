from src.game.abilities.base import AbilityStrategy


class FireBlastStrategy(AbilityStrategy):
    name = "fire_blast"
    display_name = "Fire Blast (tek hedef, 1.5x hasar)"
    is_single_target = True

    def execute(self, engine, character, target_index):
        target = engine.resolve_single_target(character, target_index)
        if target is None:
            return
        damage = int(character.attack_power * 1.5)
        engine.log.append(f"  ## {character.name} 'Fire Blast' kullandi!")
        actual = target.take_damage(damage, source_element="fire")
        engine.announce_hit(character, target, actual)
