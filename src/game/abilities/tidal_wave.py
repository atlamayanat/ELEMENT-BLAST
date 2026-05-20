from src.game.abilities.base import AbilityStrategy


class TidalWaveStrategy(AbilityStrategy):
    name = "tidal_wave"
    display_name = "Tidal Wave (TUM rakip, 0.8x hasar)"
    is_single_target = False

    def execute(self, engine, character, target_index):
        opp = engine.opponent_team_of(character)
        damage = int(character.attack_power * 0.8)
        engine.log.append(f"  ## {character.name} 'Tidal Wave' kullandi!")
        for t, actual in opp.take_damage_each(damage, source_element="hydro"):
            engine.announce_hit(character, t, actual)
