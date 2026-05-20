from abc import ABC, abstractmethod


class AbilityStrategy(ABC):
    """Strategy pattern: yetenek davranisini ayri bir sinifa cikarir.

    Engine.use_ability artik dev bir if-elif zinciri tutmuyor; her yetenek
    kendi execute() metodunu uygular. Yeni yetenek eklemek = yeni Strategy
    alt sinifi yazip registry'e kaydetmek; engine'e dokunmadan (OCP).
    """

    @property
    @abstractmethod
    def name(self):
        """Internal name (e.g. 'fire_blast'). Registry key olarak kullanilir."""

    @property
    @abstractmethod
    def display_name(self):
        """Ekranda gosterilen ad."""

    @property
    @abstractmethod
    def is_single_target(self):
        """True ise main.py hedef secimi prompt'unu acar."""

    @abstractmethod
    def execute(self, engine, character, target_index):
        """Yetenegi uygula: hasar, log, status hepsi burada."""
