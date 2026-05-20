import random

from src.game.ai.base import EnemyAIStrategy


class DefensiveAI(EnemyAIStrategy):
    """HP %30 altinda %50 olasilikla yetenek; aksi halde rastgele saldiri.

    Faz 1-2'deki engine.enemy_decide davranisinin Strategy'ye sarilmis hali.
    """

    name = "defensive"

    HP_THRESHOLD_RATIO = 0.3
    ABILITY_CHANCE_WHEN_LOW = 0.5

    def decide(self, engine, enemy):
        living_players = engine.player_team.alive_members()
        if not living_players:
            return
        target = random.choice(living_players)
        target_index = engine.player_team.index_of(target)
        low_hp = enemy.hp < enemy.max_hp * self.HP_THRESHOLD_RATIO
        if low_hp and random.random() < self.ABILITY_CHANCE_WHEN_LOW:
            engine.use_ability(enemy, target_index)
        else:
            engine.attack(enemy, target)
