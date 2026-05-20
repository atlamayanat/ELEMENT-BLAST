from src.game.characters.factory import CharacterFactory


class CharacterBuilder:
    def __init__(self):
        self._name = None
        self._element = None
        self._ability_name = None
        self._is_player = True
        self._hp = None
        self._attack_power = None
        self._ai_strategy = None

    def with_name(self, name):
        self._name = name
        return self

    def with_element(self, element):
        self._element = element
        return self

    def with_ability(self, ability_name):
        self._ability_name = ability_name
        return self

    def for_team(self, team_label):
        if team_label not in ("player", "enemy"):
            raise ValueError("team_label must be 'player' or 'enemy'")
        self._is_player = team_label == "player"
        return self

    def with_hp(self, hp):
        self._hp = hp
        return self

    def with_attack_power(self, attack_power):
        self._attack_power = attack_power
        return self

    def with_ai(self, ai_strategy):
        self._ai_strategy = ai_strategy
        return self

    def build(self):
        missing = [
            name
            for name, value in (
                ("name", self._name),
                ("element", self._element),
                ("ability", self._ability_name),
            )
            if value is None
        ]
        if missing:
            raise ValueError(f"CharacterBuilder eksik alanlar: {', '.join(missing)}")

        return CharacterFactory.create(
            element=self._element,
            name=self._name,
            ability_name=self._ability_name,
            is_player=self._is_player,
            hp=self._hp,
            attack_power=self._attack_power,
            ai_strategy=self._ai_strategy,
        )
