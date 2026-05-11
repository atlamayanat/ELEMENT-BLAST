import random

from src.game.characters import DEFAULT_ROSTER, TEAM_SIZE, CharacterBuilder
from src.game.engine import GameEngine


SINGLE_TARGET_ABILITIES = {"fire_blast", "freeze_ray"}

ABILITY_DISPLAY = {
    "fire_blast": "Fire Blast (tek hedef, 1.5x hasar)",
    "freeze_ray": "Freeze Ray (tek hedef, 1 tur dondurur)",
    "thunder_chain": "Thunder Chain (TUM rakip, 0.6x hasar)",
    "tidal_wave": "Tidal Wave (TUM rakip, 0.8x hasar)",
}


def _build(name, element, ability, team_label):
    return (
        CharacterBuilder()
        .with_name(name)
        .with_element(element)
        .with_ability(ability)
        .for_team(team_label)
        .build()
    )


def setup_default_battle(engine):
    player_picks = [
        ("Pyra", "fire", "fire_blast"),
        ("Frost", "cryo", "freeze_ray"),
        ("Volt", "electro", "thunder_chain"),
    ]
    enemy_picks = [
        ("Marin", "hydro", "tidal_wave"),
        ("Glacius", "cryo", "freeze_ray"),
        ("Ignis", "fire", "fire_blast"),
    ]
    for name, element, ability in player_picks:
        engine.add(_build(name, element, ability, "player"))
    for name, element, ability in enemy_picks:
        engine.add(_build(name, element, ability, "enemy"))


def prompt_game_mode():
    print("\n  Mod sec:")
    print("    [q] Quick start  - default 6 karakter ile baslar")
    print("    [c] Custom draft - kendi takimini havuzdan secersin")
    while True:
        raw = input("  Mod: ").strip().lower()
        if raw in ("q", "quick"):
            return "quick"
        if raw in ("c", "custom", "draft"):
            return "custom"
        print("  Gecersiz mod.")


def _render_roster(entries, picked_indices):
    print()
    for i, entry in enumerate(entries):
        marker = "X" if i in picked_indices else " "
        ability = ABILITY_DISPLAY.get(entry["ability"], entry["ability"])
        print(
            f"    [{marker}] {i + 1:>2}. {entry['name']:<9}"
            f"({entry['element']:<7}) {ability}"
        )


def prompt_player_draft(roster, count):
    print(f"\n  TAKIMINI KUR - havuzdan {count} karakter sec.")
    picked = []
    while len(picked) < count:
        _render_roster(roster, set(picked))
        raw = input(f"  Secim {len(picked) + 1}/{count} (no): ").strip()
        if not raw.isdigit():
            print("  Sayi gir.")
            continue
        idx = int(raw) - 1
        if idx < 0 or idx >= len(roster):
            print("  Havuzda yok.")
            continue
        if idx in picked:
            print("  Zaten secildi.")
            continue
        picked.append(idx)
    return picked


def setup_custom_battle(engine):
    roster = list(DEFAULT_ROSTER)
    player_indices = prompt_player_draft(roster, TEAM_SIZE)

    remaining = [i for i in range(len(roster)) if i not in player_indices]
    enemy_indices = random.sample(remaining, TEAM_SIZE)

    print("\n  Rakip takim havuzdan otomatik secildi:")
    for idx in enemy_indices:
        entry = roster[idx]
        print(f"    - {entry['name']} ({entry['element']})")

    for idx in player_indices:
        e = roster[idx]
        engine.add(_build(e["name"], e["element"], e["ability"], "player"))
    for idx in enemy_indices:
        e = roster[idx]
        engine.add(_build(e["name"], e["element"], e["ability"], "enemy"))


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


def prompt_target(engine):
    living = [(i, c) for i, c in enumerate(engine.enemy_team) if c.hp > 0]
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


def player_turn(engine, character):
    print(f"\n  >>> Sira: {character.name} ({character.element})")
    action = prompt_action_choice(character)
    if action == "attack":
        target_idx = prompt_target(engine)
        engine.player_action(character, "attack", target_idx)
    elif action == "ability":
        if character.ability_name in SINGLE_TARGET_ABILITIES:
            target_idx = prompt_target(engine)
            engine.player_action(character, "ability", target_idx)
        else:
            engine.player_action(character, "ability", 0)


def player_phase(engine):
    for c in list(engine.player_team):
        if engine.is_battle_over():
            return
        if c.hp <= 0:
            continue
        if not engine.tick_status(c):
            engine.render()
            continue
        player_turn(engine, c)
        engine.check_game_over()
        engine.render()


def enemy_phase(engine):
    for e in list(engine.enemy_team):
        if engine.is_battle_over():
            return
        if e.hp <= 0:
            continue
        print(f"\n  >>> Rakip: {e.name} ({e.element}) hareket ediyor...")
        if not engine.tick_status(e):
            engine.render()
            continue
        engine.enemy_decide(e)
        engine.check_game_over()
        engine.render()


def main():
    print("=" * 92)
    print("  MINI OYUN MOTORU - 3v3 Elemental Dovus (Faz 0)".center(92))
    print("=" * 92)
    print("\n  Elementler: Fire, Cryo, Electro, Hydro")
    print(
        "  Reaksiyonlar: Fire->Cryo 2x | Fire/Hydro karsilikli 1.5x | "
        "Cryo->Hydro freeze | Hydro->Electro AoE | Electro->Fire sicrar"
    )

    engine = GameEngine()
    mode = prompt_game_mode()
    if mode == "custom":
        setup_custom_battle(engine)
    else:
        setup_default_battle(engine)
    engine.render()

    while not engine.is_battle_over():
        engine.turn += 1
        turn_header(engine.turn)
        player_phase(engine)
        if engine.is_battle_over():
            break
        enemy_phase(engine)

    print()
    print("=" * 92)
    if engine.winner == "player":
        print("  *** ZAFER! Tum dusmanlar yenildi.".center(92))
    else:
        print("  *** YENILGI! Takiminiz yenik dustu.".center(92))
    print("=" * 92)


if __name__ == "__main__":
    main()
