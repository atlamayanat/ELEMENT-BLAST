class Team:
    """Composite pattern: oyuncu ve dusman takimlarini tek bir nesne olarak yonetir.

    Bir Team uyelerinin toplami gibi davranabilir:
      * AoE hasar dagitma (Hydro->Electro, Thunder Chain, Tidal Wave)
      * Status tick'i toplu cagirma
      * Defeat kontrolu (uyelerden hicbiri hayatta degil mi?)

    Engine list[Character] yerine Team'i tutar; boylece HP-cap hack ve tekrarlanan
    AoE doNguleri tek yerden yonetilir.

    __iter__/__len__/__getitem__ destekledigi icin mevcut "for c in team" kullanimi
    tek satir bile degistirmeden calismaya devam eder.
    """

    def __init__(self, label):
        self.label = label
        self._members = []

    def add(self, character):
        self._members.append(character)
        return character

    def members(self):
        return list(self._members)

    def alive_members(self):
        return [m for m in self._members if m.hp > 0]

    def is_defeated(self):
        return not self.alive_members()

    def __len__(self):
        return len(self._members)

    def __iter__(self):
        return iter(self._members)

    def __getitem__(self, index):
        return self._members[index]

    def index_of(self, member):
        return self._members.index(member)

    def apply_to_each(self, fn):
        for m in self.alive_members():
            fn(m)

    def take_damage_each(self, amount, source_element=None):
        applied = []
        for m in self.alive_members():
            actual = m.take_damage(amount, source_element)
            applied.append((m, actual))
        return applied

    def tick_statuses(self):
        logs = []
        for m in self._members:
            logs.extend(m.tick())
        return logs

    def apply_effect_to(self, member, effect_factory):
        idx = self._members.index(member)
        wrapped = effect_factory(member)
        self._members[idx] = wrapped
        return wrapped
