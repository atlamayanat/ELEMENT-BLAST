from src.game.characters.base import Character


class StatusEffect(Character):
    """Decorator pattern base.

    Sarsılan karaktere yeni davranıs ekler ama Character sözlesmesini bozmaz.
    Tanımlanmamıs ozellikler ve attribut yazımları wrapped'a iletilir; böylece
    engine target.hp -= damage gibi mevcut kullanımları da kollar.

    Sadece "_" ön ekli alanlar dekoratorun kendi üzerinde durur (ornek: _remaining).
    """

    def __init__(self, wrapped):
        object.__setattr__(self, "_wrapped", wrapped)

    @classmethod
    def default_element(cls):
        return "neutral"

    @classmethod
    def default_stats(cls):
        return {"hp": 0, "attack_power": 0}

    def __getattr__(self, name):
        wrapped = object.__getattribute__(self, "_wrapped")
        return getattr(wrapped, name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            setattr(self._wrapped, name, value)

    def take_damage(self, amount, source_element=None):
        return self._wrapped.take_damage(amount, source_element)

    def tick(self):
        return list(self._wrapped.tick())

    def should_skip_turn(self):
        return self._wrapped.should_skip_turn()

    def apply_effect(self, effect_factory):
        return effect_factory(self)

    def has_status(self, status_name):
        return self._wrapped.has_status(status_name)

    def unwrap(self):
        return self._wrapped


class BurningStatus(StatusEffect):
    """Yanma: 3 tur boyunca her tur sabit DoT hasari."""

    DURATION = 3
    DOT_DAMAGE = 2

    def __init__(self, wrapped):
        super().__init__(wrapped)
        object.__setattr__(self, "_remaining", self.DURATION)

    def tick(self):
        logs = list(self._wrapped.tick())
        if self._remaining <= 0:
            return logs
        actual = self._wrapped.take_damage(self.DOT_DAMAGE, source_element="fire")
        logs.append(f"  ~ {self._wrapped.name} yaniyor: {actual} hasar")
        object.__setattr__(self, "_remaining", self._remaining - 1)
        if self._remaining <= 0:
            logs.append(f"  ~ {self._wrapped.name} yanmaktan kurtuldu")
        return logs

    def has_status(self, status_name):
        if status_name == "burning" and self._remaining > 0:
            return True
        return self._wrapped.has_status(status_name)


class FrozenStatus(StatusEffect):
    """Donma: belirli tur boyunca should_skip_turn True doner."""

    DURATION = 1

    def __init__(self, wrapped, duration=None):
        super().__init__(wrapped)
        object.__setattr__(self, "_remaining", duration if duration is not None else self.DURATION)

    def should_skip_turn(self):
        if self._remaining > 0:
            return True
        return self._wrapped.should_skip_turn()

    def tick(self):
        logs = list(self._wrapped.tick())
        if self._remaining > 0:
            object.__setattr__(self, "_remaining", self._remaining - 1)
        return logs

    def has_status(self, status_name):
        if status_name == "frozen" and self._remaining > 0:
            return True
        return self._wrapped.has_status(status_name)


class ShockedStatus(StatusEffect):
    """Sok: bir sonraki gelen hasari 1.5x artirir, sonra dagilir."""

    AMPLIFIER = 1.5

    def __init__(self, wrapped):
        super().__init__(wrapped)
        object.__setattr__(self, "_active", True)

    def take_damage(self, amount, source_element=None):
        if self._active and amount > 0:
            object.__setattr__(self, "_active", False)
            amplified = int(amount * self.AMPLIFIER)
            return self._wrapped.take_damage(amplified, source_element)
        return self._wrapped.take_damage(amount, source_element)

    def has_status(self, status_name):
        if status_name == "shocked" and self._active:
            return True
        return self._wrapped.has_status(status_name)
