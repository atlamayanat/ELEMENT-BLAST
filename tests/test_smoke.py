"""Smoke tests for Phase 3 — CI coverage and OCP demo."""

from src.game.abilities import FireBlastStrategy, registry as ability_registry
from src.game.ai import DefensiveAI
from src.game.characters import CharacterFactory
from src.game.effects import BurningStatus, FrozenStatus
from src.game.engine import GameEngine
from src.game.reactions import ReactionHandler


# --- Composite (Team) ---

def test_engine_instantiates_with_two_empty_teams():
    e = GameEngine()
    assert e.player_team.is_defeated()
    assert e.enemy_team.is_defeated()
    assert e.turn == 0
    assert e.winner is None


def test_team_aoe_damages_all_living_members():
    e = GameEngine()
    e.create_character("Volt", "electro", "thunder_chain", True)
    for n in ("A", "B", "C"):
        e.create_character(n, "cryo", "freeze_ray", False)
    starting_hps = [c.hp for c in e.enemy_team]
    e.use_ability(e.player_team[0])
    final_hps = [c.hp for c in e.enemy_team]
    for before, after in zip(starting_hps, final_hps):
        assert after < before, "Thunder Chain should damage every living enemy"


def test_defeat_detection_when_all_enemies_dead():
    e = GameEngine()
    e.create_character("Pyra", "fire", "fire_blast", True)
    e.create_character("Glacius", "cryo", "freeze_ray", False)
    e.player_team[0].attack_power = 999
    e.use_ability(e.player_team[0])
    e.check_game_over()
    assert e.game_over is True
    assert e.winner == "player"


# --- Decorator (StatusEffect) ---

def test_overkill_clamps_hp_to_zero_not_negative():
    e = GameEngine()
    e.create_character("Pyra", "fire", "fire_blast", True)
    e.create_character("Glacius", "cryo", "freeze_ray", False)
    e.player_team[0].attack_power = 999
    e.use_ability(e.player_team[0])
    assert e.enemy_team[0].hp == 0


def test_fire_hydro_reaction_applies_burning_status():
    e = GameEngine()
    e.create_character("Pyra", "fire", "fire_blast", True)
    e.create_character("Marin", "hydro", "tidal_wave", False)
    e.attack(e.player_team[0], e.enemy_team[0])
    assert e.enemy_team[0].has_status("burning")
    assert isinstance(e.enemy_team[0], BurningStatus)


def test_cryo_hydro_reaction_applies_frozen_status():
    e = GameEngine()
    e.create_character("Frost", "cryo", "freeze_ray", True)
    e.create_character("Marin", "hydro", "tidal_wave", False)
    e.attack(e.player_team[0], e.enemy_team[0])
    assert e.enemy_team[0].has_status("frozen")
    assert e.enemy_team[0].should_skip_turn()


# --- Strategy (AbilityStrategy + EnemyAIStrategy) ---

def test_character_has_ability_strategy_instance():
    e = GameEngine()
    e.create_character("Pyra", "fire", "fire_blast", True)
    assert isinstance(e.player_team[0].ability, FireBlastStrategy)


def test_enemy_character_has_defensive_ai_by_default():
    e = GameEngine()
    e.create_character("Marin", "hydro", "tidal_wave", False)
    assert isinstance(e.enemy_team[0].ai_strategy, DefensiveAI)


def test_player_character_has_no_ai_strategy():
    e = GameEngine()
    e.create_character("Pyra", "fire", "fire_blast", True)
    assert e.player_team[0].ai_strategy is None


def test_fire_blast_strategy_deals_amplified_damage():
    e = GameEngine()
    e.create_character("Pyra", "fire", "fire_blast", True)
    e.create_character("Marin", "hydro", "tidal_wave", False)
    starting_hp = e.enemy_team[0].hp
    e.use_ability(e.player_team[0])
    assert e.enemy_team[0].hp == starting_hp - int(e.player_team[0].attack_power * 1.5)


# --- Chain of Responsibility (ReactionHandler) ---

def test_default_reaction_when_no_handler_matches():
    e = GameEngine()
    e.create_character("Pyra", "fire", "fire_blast", True)
    e.create_character("Ignis", "fire", "fire_blast", False)
    starting_hp = e.enemy_team[0].hp
    e.attack(e.player_team[0], e.enemy_team[0])
    assert e.enemy_team[0].hp == starting_hp - e.player_team[0].attack_power


# --- OCP DEMO: yeni reaksiyon ekle, engine'e dokunma ---

def test_ocp_new_reaction_handler_appended_without_engine_change():
    """OCP demo: yeni bir CryoElectroHandler ekleyip engine'e dokunmadan
    reaksiyon tetiklenmesini kanitlar. Engine kodu degismedi - chain genisledi.
    """

    class CryoElectroHandler(ReactionHandler):
        """Yeni eklenmis reaksiyon: Cryo -> Electro yarı hasar + dondurma."""

        triggered_on = []

        def can_handle(self, ctx):
            return ctx.attacker.element == "cryo" and ctx.target.element == "electro"

        def apply(self, ctx):
            damage = max(1, ctx.base_damage // 2)
            actual = ctx.target.take_damage(damage, source_element="cryo")
            ctx.engine.announce_hit(ctx.attacker, ctx.target, actual)
            CryoElectroHandler.triggered_on.append(ctx.target.name)
            if ctx.target.hp > 0:
                ctx.opp_team.apply_effect_to(ctx.target, FrozenStatus)

    e = GameEngine()
    e.reaction_chain.append(CryoElectroHandler())
    e.create_character("Frost", "cryo", "freeze_ray", True)
    e.create_character("Volt", "electro", "thunder_chain", False)
    e.attack(e.player_team[0], e.enemy_team[0])

    assert "Volt" in CryoElectroHandler.triggered_on
    assert e.enemy_team[0].has_status("frozen")
