from dataclasses import dataclass


@dataclass
class ReactionContext:
    """Reaksiyon handler'larina engine durumunu aktaran tasiyici.

    Handler'lar bu context'in alanlarini okur ve engine uzerinden side
    effect uygular (hasar, log, status decorator).
    """

    attacker: object
    target: object
    opp_team: object
    base_damage: int
    engine: object
