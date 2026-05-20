from src.game.characters import CharacterFactory
from src.game.reactions import ReactionChain, ReactionContext
from src.game.team import Team


class GameEngine:
    def __init__(self, reaction_chain=None):
        self.player_team = Team("player")
        self.enemy_team = Team("enemy")
        self.turn = 0
        self.log = []
        self.game_over = False
        self.winner = None
        self.reaction_chain = reaction_chain if reaction_chain is not None else ReactionChain.builtin()

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
            self.player_team.add(character)
        else:
            self.enemy_team.add(character)
        return character

    def opponent_team_of(self, character):
        return self.enemy_team if character.is_player else self.player_team

    def resolve_single_target(self, character, target_index):
        opp = self.opponent_team_of(character)
        if 0 <= target_index < len(opp) and opp[target_index].hp > 0:
            return opp[target_index]
        living = opp.alive_members()
        return living[0] if living else None

    def announce_hit(self, attacker, target, damage):
        self.log.append(f"  {attacker.name} -> {target.name}: {damage} hasar")
        if target.hp <= 0:
            self.log.append(f"  X {target.name} oldu!")

    def attack(self, attacker, target):
        if target.hp <= 0:
            self.log.append(f"  {target.name} zaten olu, saldiri iptal.")
            return
        ctx = ReactionContext(
            attacker=attacker,
            target=target,
            opp_team=self.opponent_team_of(attacker),
            base_damage=attacker.attack_power,
            engine=self,
        )
        self.reaction_chain.handle(ctx)

    def use_ability(self, character, target_index=0):
        character.ability.execute(self, character, target_index)

    def enemy_decide(self, enemy):
        enemy.ai_strategy.decide(self, enemy)

    def tick_status(self, character):
        if character.should_skip_turn():
            self.log.extend(character.tick())
            self.log.append(f"  ~ {character.name} donmus, sira atladi")
            return False
        self.log.extend(character.tick())
        return True

    def check_game_over(self):
        if self.player_team.is_defeated():
            self.game_over = True
            self.winner = "enemy"
        elif self.enemy_team.is_defeated():
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
        elif c.has_status("frozen"):
            status = "  *DONUK*"
        elif c.has_status("burning"):
            status = "  *YANIYOR*"
        elif c.has_status("shocked"):
            status = "  *SOKLU*"
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
