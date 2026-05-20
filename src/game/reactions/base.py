from abc import ABC, abstractmethod


class ReactionHandler(ABC):
    """Chain of Responsibility: bir elemental reaksiyonu temsil eder.

    can_handle(ctx) True donerse apply(ctx) cagrilir. ReactionChain ilk
    eslesen handler'da durur. DefaultHandler her zaman True donerek
    fallback gorevi goruyor.
    """

    @abstractmethod
    def can_handle(self, ctx):
        ...

    @abstractmethod
    def apply(self, ctx):
        ...


class ReactionChain:
    """Sirasi onemli handler listesi. Ilk eslesen handler'i calistirir.

    Yeni reaksiyon eklemek = yeni handler class + chain'e append; engine'e
    dokunmadan (OCP). DefaultHandler her zaman zincirin SONUNDA olmalidir.
    """

    def __init__(self, handlers):
        self._handlers = list(handlers)

    def handle(self, ctx):
        for h in self._handlers:
            if h.can_handle(ctx):
                h.apply(ctx)
                return h
        return None

    def append(self, handler):
        """Yeni handler ekle. DefaultHandler hep en sonda kalmali."""
        self._handlers.insert(-1, handler) if self._handlers else self._handlers.append(handler)

    def handlers(self):
        return list(self._handlers)

    @classmethod
    def builtin(cls):
        from src.game.reactions.handlers import (
            FireCryoHandler,
            ElectroFireHandler,
            HydroElectroHandler,
            CryoHydroHandler,
            FireHydroHandler,
            HydroFireHandler,
            DefaultHandler,
        )
        return cls([
            FireCryoHandler(),
            ElectroFireHandler(),
            HydroElectroHandler(),
            CryoHydroHandler(),
            FireHydroHandler(),
            HydroFireHandler(),
            DefaultHandler(),
        ])
