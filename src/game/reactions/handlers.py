import random

from src.game.effects import BurningStatus, FrozenStatus, ShockedStatus
from src.game.reactions.base import ReactionHandler


def _matches(ctx, attacker_element, target_element):
    return ctx.attacker.element == attacker_element and ctx.target.element == target_element


class FireCryoHandler(ReactionHandler):
    """Fire -> Cryo: 2x hasar."""

    def can_handle(self, ctx):
        return _matches(ctx, "fire", "cryo")

    def apply(self, ctx):
        damage = ctx.base_damage * 2
        ctx.engine.log.append(
            f"  >> REAKSIYON: Fire->Cryo, hasar 2x ({ctx.attacker.name} -> {ctx.target.name})"
        )
        actual = ctx.target.take_damage(damage, source_element="fire")
        ctx.engine.announce_hit(ctx.attacker, ctx.target, actual)


class ElectroFireHandler(ReactionHandler):
    """Electro -> Fire: hasar + %75 sicrama + Shocked status."""

    def can_handle(self, ctx):
        return _matches(ctx, "electro", "fire")

    def apply(self, ctx):
        actual = ctx.target.take_damage(ctx.base_damage, source_element="electro")
        ctx.engine.announce_hit(ctx.attacker, ctx.target, actual)
        others = [c for c in ctx.opp_team.alive_members() if c is not ctx.target]
        if others:
            bounce_target = random.choice(others)
            bounce_damage = max(1, int(ctx.base_damage * 0.75))
            bounce_actual = bounce_target.take_damage(bounce_damage, source_element="electro")
            ctx.engine.log.append(
                f"  >> REAKSIYON: Electro->Fire, sicrama %75 -> {bounce_target.name}"
            )
            ctx.engine.announce_hit(ctx.attacker, bounce_target, bounce_actual)
        else:
            ctx.engine.log.append("  >> REAKSIYON: Electro->Fire ama sicrayacak hedef yok")
        if ctx.target.hp > 0:
            ctx.opp_team.apply_effect_to(ctx.target, ShockedStatus)
            ctx.engine.log.append(f"  >> {ctx.target.name} sok altinda (bir sonraki hasar +%50)")


class HydroElectroHandler(ReactionHandler):
    """Hydro -> Electro: 1.5x hasar tum rakip takima bolusturulur."""

    def can_handle(self, ctx):
        return _matches(ctx, "hydro", "electro")

    def apply(self, ctx):
        total_damage = int(ctx.base_damage * 1.5)
        living = ctx.opp_team.alive_members()
        if not living:
            return
        split = max(1, total_damage // len(living))
        ctx.engine.log.append(
            f"  >> REAKSIYON: Hydro->Electro, 1.5x hasar tum takima ({split}/kisi)"
        )
        for victim, actual in ctx.opp_team.take_damage_each(split, source_element="hydro"):
            ctx.engine.announce_hit(ctx.attacker, victim, actual)


class CryoHydroHandler(ReactionHandler):
    """Cryo -> Hydro: hasar + 1 tur dondurma."""

    def can_handle(self, ctx):
        return _matches(ctx, "cryo", "hydro")

    def apply(self, ctx):
        actual = ctx.target.take_damage(ctx.base_damage, source_element="cryo")
        ctx.engine.announce_hit(ctx.attacker, ctx.target, actual)
        if ctx.target.hp > 0:
            ctx.opp_team.apply_effect_to(ctx.target, FrozenStatus)
            ctx.engine.log.append(f"  >> REAKSIYON: Cryo->Hydro, {ctx.target.name} 1 tur dondu")


class FireHydroHandler(ReactionHandler):
    """Fire -> Hydro: 1.5x hasar + 3 tur yanma."""

    def can_handle(self, ctx):
        return _matches(ctx, "fire", "hydro")

    def apply(self, ctx):
        damage = int(ctx.base_damage * 1.5)
        ctx.engine.log.append(f"  >> REAKSIYON: Fire->Hydro, hasar 1.5x")
        actual = ctx.target.take_damage(damage, source_element="fire")
        ctx.engine.announce_hit(ctx.attacker, ctx.target, actual)
        if ctx.target.hp > 0:
            ctx.opp_team.apply_effect_to(ctx.target, BurningStatus)
            ctx.engine.log.append(f"  >> {ctx.target.name} yandi (3 tur DoT)")


class HydroFireHandler(ReactionHandler):
    """Hydro -> Fire: 1.5x hasar."""

    def can_handle(self, ctx):
        return _matches(ctx, "hydro", "fire")

    def apply(self, ctx):
        damage = int(ctx.base_damage * 1.5)
        ctx.engine.log.append(f"  >> REAKSIYON: Hydro->Fire, hasar 1.5x")
        actual = ctx.target.take_damage(damage, source_element="hydro")
        ctx.engine.announce_hit(ctx.attacker, ctx.target, actual)


class DefaultHandler(ReactionHandler):
    """Reaksiyon yoksa varsayilan hasar. Zincirin SONUNDA olmali."""

    def can_handle(self, ctx):
        return True

    def apply(self, ctx):
        actual = ctx.target.take_damage(ctx.base_damage, source_element=ctx.attacker.element)
        ctx.engine.announce_hit(ctx.attacker, ctx.target, actual)
