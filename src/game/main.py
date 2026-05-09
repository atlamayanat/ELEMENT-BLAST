from src.game.engine import GameEngine


SINGLE_TARGET_ABILITIES = {"fire_blast", "freeze_ray"}

ABILITY_DISPLAY = {
    "fire_blast": "Fire Blast (tek hedef, 1.5x hasar)",
    "freeze_ray": "Freeze Ray (tek hedef, 1 tur dondurur)",
    "thunder_chain": "Thunder Chain (TUM rakip, 0.6x hasar)",
    "tidal_wave": "Tidal Wave (TUM rakip, 0.8x hasar)",
}


def setup_default_battle(engine):
    engine.create_character("Pyra", "fire", "fire_blast", is_player=True)
    engine.create_character("Frost", "cryo", "freeze_ray", is_player=True)
    engine.create_character("Volt", "electro", "thunder_chain", is_player=True)

    engine.create_character("Marin", "hydro", "tidal_wave", is_player=False)
    engine.create_character("Glacius", "cryo", "freeze_ray", is_player=False)
    engine.create_character("Ignis", "fire", "fire_blast", is_player=False)


def prompt_action_choice(character):
    ability_label = ABILITY_DISPLAY.get(character.ability_name, character.ability_name)
    print(f"  Yetenek: {ability_label}")
    while True:
        raw = input("  Aksiyon [a]ttack / [s]kill: ").strip().lower()
        if raw in ("a", "attack"):
            return "attack"
        if raw in ("s", "skill", "ability"):
            return "ability"
        print("  Gecersiz secim.")


def prompt_target(engine, attacker):
    opp = engine.opponent_team_of(attacker)
    living = [(i, c) for i, c in enumerate(opp) if c.hp > 0]
    print("  Hedef:")
    for i, c in living:
        print(f"    [{i + 1}] {c.name} ({c.element})  HP {c.hp}/{c.max_hp}")
    valid_input = {str(i + 1): i for i, _ in living}
    while True:
        raw = input("  Hedef no: ").strip()
        if raw in valid_input:
            return valid_input[raw]
        print("  Olu ya da gecersiz hedef.")


def turn_header(turn):
    print()
    print("=" * 92)
    print(f"  TUR {turn}".center(92))
    print("=" * 92)


def team_header(team_label):
    print()
    print("-" * 92)
    print(f"  {team_label} SIRASI".center(92))
    print("-" * 92)


def character_turn(engine, character):
    print(f"\n  >>> Sira: {character.name} ({character.element})")
    action = prompt_action_choice(character)
    if action == "attack":
        target_idx = prompt_target(engine, character)
        engine.player_action(character, "attack", target_idx)
    elif action == "ability":
        if character.ability_name in SINGLE_TARGET_ABILITIES:
            target_idx = prompt_target(engine, character)
            engine.player_action(character, "ability", target_idx)
        else:
            engine.player_action(character, "ability", 0)


def team_phase(engine, team, team_label):
    team_header(team_label)
    for c in list(team):
        if engine.is_battle_over():
            return
        if c.hp <= 0:
            continue
        if not engine.tick_status(c):
            engine.render()
            continue
        character_turn(engine, c)
        engine.check_game_over()
        engine.render()


def main():
    print("=" * 92)
    print("  MINI OYUN MOTORU - 3v3 Elemental Dovus PvP (Faz 0)".center(92))
    print("=" * 92)
    print("\n  Elementler: Fire, Cryo, Electro, Hydro")
    print(
        "  Reaksiyonlar: Fire->Cryo 2x | Fire/Hydro karsilikli 1.5x | "
        "Cryo->Hydro freeze | Hydro->Electro AoE | Electro->Fire sicrar"
    )
    print("\n  Iki oyuncu sirayla oynar. Klavyeyi sirasi gelene devredin.")

    engine = GameEngine()
    setup_default_battle(engine)
    engine.render()

    while not engine.is_battle_over():
        engine.turn += 1
        turn_header(engine.turn)
        team_phase(engine, engine.player_team, "TAKIM 1")
        if engine.is_battle_over():
            break
        team_phase(engine, engine.enemy_team, "TAKIM 2")

    print()
    print("=" * 92)
    if engine.winner == "player":
        print("  *** TAKIM 1 KAZANDI!".center(92))
    else:
        print("  *** TAKIM 2 KAZANDI!".center(92))
    print("=" * 92)


if __name__ == "__main__":
    main()
