from src.game.abilities.base import AbilityStrategy


class ThunderChainStrategy(AbilityStrategy):
    name = "thunder_chain"
    display_name = "Thunder Chain (TUM rakip, 0.6x hasar)"
    is_single_target = False

    def execute(self, engine, character, target_index):
        opp = engine.opponent_team_of(character)
        damage = int(character.attack_power * 0.6)
        engine.log.append(f"  ## {character.name} 'Thunder Chain' kullandi!")
        for t, actual in opp.take_damage_each(damage, source_element="electro"):
            engine.announce_hit(character, t, actual)
