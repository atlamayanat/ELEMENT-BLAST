import random

from src.game.characters import CharacterFactory


class GameEngine:
    def __init__(self):
        self.player_team = []
        self.enemy_team = []
        self.turn = 0
        self.log = []
        self.game_over = False
        self.winner = None

    def create_character(self, name, element, ability_name, is_player):
        character = CharacterFactory.create(
            element=element,
            name=name,
            ability_name=ability_name,
            is_player=is_player,
        )
        return self.add(character)

    def add(self, character):
        if character.is_player:
            self.player_team.append(character)
        else:
            self.enemy_team.append(character)
        return character

    def opponent_team_of(self, character):
        return self.enemy_team if character.is_player else self.player_team

    def alive(self, team):
        return [c for c in team if c.hp > 0]

    def attack(self, attacker, target):
        if target.hp <= 0:
            self.log.append(f"  {target.name} zaten olu, saldiri iptal.")
            return

        if attacker.element == "fire":
            damage = attacker.attack_power
        elif attacker.element == "cryo":
            damage = attacker.attack_power
        elif attacker.element == "electro":
            damage = attacker.attack_power
        elif attacker.element == "hydro":
            damage = attacker.attack_power
        else:
            damage = 1

        if attacker.element == "fire" and target.element == "cryo":
            damage *= 2
            self.log.append(
                f"  >> REAKSIYON: Fire->Cryo, hasar 2x ({attacker.name} -> {target.name})"
            )
            target.hp -= damage
            self._announce_hit(attacker, target, damage)
        elif attacker.element == "electro" and target.element == "fire":
            target.hp -= damage
            self._announce_hit(attacker, target, damage)
            opp_team = self.opponent_team_of(attacker)
            others = [c for c in self.alive(opp_team) if c is not target]
            if others:
                bounce_target = random.choice(others)
                bounce_damage = max(1, int(damage * 0.75))
                bounce_target.hp -= bounce_damage
                self.log.append(
                    f"  >> REAKSIYON: Electro->Fire, sicrama %75 -> {bounce_target.name}"
                )
                self._announce_hit(attacker, bounce_target, bounce_damage)
            else:
                self.log.append("  >> REAKSIYON: Electro->Fire ama sicrayacak hedef yok")
        elif attacker.element == "hydro" and target.element == "electro":
            total_damage = int(damage * 1.5)
            opp_team = self.opponent_team_of(attacker)
            living = self.alive(opp_team)
            if not living:
                return
            split = max(1, total_damage // len(living))
            self.log.append(
                f"  >> REAKSIYON: Hydro->Electro, 1.5x hasar tum takima ({split}/kisi)"
            )
            for victim in living:
                victim.hp -= split
                self._announce_hit(attacker, victim, split)
        elif attacker.element == "cryo" and target.element == "hydro":
            target.hp -= damage
            target.frozen_turns = 1
            self.log.append(f"  >> REAKSIYON: Cryo->Hydro, {target.name} 1 tur dondu")
            self._announce_hit(attacker, target, damage)
        elif attacker.element == "fire" and target.element == "hydro":
            damage = int(damage * 1.5)
            self.log.append(f"  >> REAKSIYON: Fire->Hydro, hasar 1.5x")
            target.hp -= damage
            self._announce_hit(attacker, target, damage)
        elif attacker.element == "hydro" and target.element == "fire":
            damage = int(damage * 1.5)
            self.log.append(f"  >> REAKSIYON: Hydro->Fire, hasar 1.5x")
            target.hp -= damage
            self._announce_hit(attacker, target, damage)
        else:
            target.hp -= damage
            self._announce_hit(attacker, target, damage)

        for team in (self.player_team, self.enemy_team):
            for c in team:
                if c.hp < 0:
                    c.hp = 0

    def _announce_hit(self, attacker, target, damage):
        self.log.append(f"  {attacker.name} -> {target.name}: {damage} hasar")
        if target.hp <= 0:
            self.log.append(f"  X {target.name} oldu!")

    def _resolve_single_target(self, character, target_index):
        opp = self.opponent_team_of(character)
        if 0 <= target_index < len(opp) and opp[target_index].hp > 0:
            return opp[target_index]
        living = self.alive(opp)
        return living[0] if living else None

    def use_ability(self, character, target_index=0):
        if character.ability_name == "fire_blast":
            target = self._resolve_single_target(character, target_index)
            if target is None:
                return
            damage = int(character.attack_power * 1.5)
            self.log.append(f"  ## {character.name} 'Fire Blast' kullandi!")
            saved_element = character.element
            character.element = "fire"
            target.hp -= damage
            self._announce_hit(character, target, damage)
            character.element = saved_element
        elif character.ability_name == "freeze_ray":
            target = self._resolve_single_target(character, target_index)
            if target is None:
                return
            damage = character.attack_power
            target.hp -= damage
            target.frozen_turns = 1
            self.log.append(f"  ## {character.name} 'Freeze Ray' kullandi!")
            self.log.append(f"  >> {target.name} 1 tur dondu (yetenek)")
            self._announce_hit(character, target, damage)
        elif character.ability_name == "thunder_chain":
            opp = self.opponent_team_of(character)
            living = self.alive(opp)
            damage = int(character.attack_power * 0.6)
            self.log.append(f"  ## {character.name} 'Thunder Chain' kullandi!")
            for t in living:
                t.hp -= damage
                self._announce_hit(character, t, damage)
        elif character.ability_name == "tidal_wave":
            opp = self.opponent_team_of(character)
            living = self.alive(opp)
            damage = int(character.attack_power * 0.8)
            self.log.append(f"  ## {character.name} 'Tidal Wave' kullandi!")
            for t in living:
                t.hp -= damage
                self._announce_hit(character, t, damage)
        else:
            self.log.append(f"  Bilinmeyen yetenek: {character.ability_name}")

        for team in (self.player_team, self.enemy_team):
            for c in team:
                if c.hp < 0:
                    c.hp = 0

    def enemy_decide(self, enemy):
        living_players = self.alive(self.player_team)
        if not living_players:
            return
        target = random.choice(living_players)
        target_index = self.player_team.index(target)
        if enemy.hp < enemy.max_hp * 0.3 and random.random() < 0.5:
            self.use_ability(enemy, target_index)
        else:
            self.attack(enemy, target)

    def tick_status(self, character):
        if character.frozen_turns > 0:
            character.frozen_turns -= 1
            self.log.append(f"  ~ {character.name} donmus, sira atladi")
            return False
        return True

    def check_game_over(self):
        if not self.alive(self.player_team):
            self.game_over = True
            self.winner = "enemy"
        elif not self.alive(self.enemy_team):
            self.game_over = True
            self.winner = "player"

    def render(self):
        col = 44
        if self.log:
            print()
            for line in self.log:
                print(line)
            self.log.clear()
        print()
        print("  " + "TAKIMINIZ".ljust(col) + "  RAKIP")
        print("  " + ("-" * (col - 2)).ljust(col) + "  " + "-" * (col - 2))
        n = max(len(self.player_team), len(self.enemy_team))
        for i in range(n):
            left_c = self.player_team[i] if i < len(self.player_team) else None
            right_c = self.enemy_team[i] if i < len(self.enemy_team) else None
            left = self._format_char(i, left_c)
            right = self._format_char(i, right_c)
            print("  " + left.ljust(col) + "  " + right)
        print()

    def _format_char(self, index, c):
        if c is None:
            return ""
        elem = c.element.upper()[:3]
        if c.max_hp:
            filled = max(0, c.hp) * 6 // c.max_hp
        else:
            filled = 0
        bar = "#" * filled + "." * (6 - filled)
        if c.hp <= 0:
            status = "  *OLU*"
        elif c.frozen_turns > 0:
            status = "  *DONUK*"
        else:
            status = ""
        return f"[{index + 1}] {c.name:<9}({elem}) {c.hp:>3}/{c.max_hp:<3} [{bar}]{status}"

    def player_action(self, character, action, target_index):
        if action == "attack":
            opp = self.enemy_team
            living_indices = [i for i, c in enumerate(opp) if c.hp > 0]
            if not living_indices:
                return
            if target_index not in living_indices:
                target_index = living_indices[0]
            self.attack(character, opp[target_index])
        elif action == "ability":
            self.use_ability(character, target_index)
        else:
            self.log.append(f"  Bilinmeyen aksiyon: {action}")

    def is_battle_over(self):
        self.check_game_over()
        return self.game_over
