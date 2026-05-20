from abc import ABC, abstractmethod


class EnemyAIStrategy(ABC):
    """Strategy pattern: dusman AI davranisi.

    Mevcut tek varyant DefensiveAI; bu Strategy boilerplate'i ile yeni
    varyant eklemek (Aggressive, Healer vs) = yeni alt sinif + Builder'da
    inject, engine'e dokunmadan.
    """

    @property
    @abstractmethod
    def name(self):
        ...

    @abstractmethod
    def decide(self, engine, enemy):
        """Sirasi gelen dusman icin engine uzerinden bir aksiyon tetikler."""
