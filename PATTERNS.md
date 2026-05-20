# PATTERNS.md — Uygulanan Tasarım Örüntüleri

Bu dosya her fazda eklenen örüntüleri, neden seçildiklerini ve hangi sorunu çözdüklerini belgeler.

---

## Faz 1 — Creational Örüntüler

### 1. Factory Method

**Kategori:** Creational
**Konum:** [`src/game/characters/factory.py`](src/game/characters/factory.py)
**İlgili PROBLEMS.md maddesi:** #2 (Element type-check zincirleri) ve #4 (Yetenekler isim-bağımlı — kısmen)

#### Sorun
Faz 0'da `engine.create_character` metodu element string'ine göre `if-elif` ile dallanıyordu; her yeni element için 4 ayrı metoda dokunmak gerekiyordu (OCP ihlali). Karakter tipi tek bir sınıfta string field olarak tutuluyordu, polimorfizm yoktu.

#### Çözüm
Önce **soyut bir `Character` hiyerarşisi** kuruldu: `Character` (ABC) + 4 concrete alt sınıf (`FireCharacter`, `CryoCharacter`, `ElectroCharacter`, `HydroCharacter`). Her alt sınıf kendi `element` property'sini ve `default_stats` classmethod'unu taşıyor.

Sonra `CharacterFactory` bir **registry tablosu** ile dispatch yapıyor:
```python
_registry = {
    "fire": FireCharacter,
    "cryo": CryoCharacter,
    "electro": ElectroCharacter,
    "hydro": HydroCharacter,
}
```

`CharacterFactory.create(element=...)` çağrısı kaydın doğru sınıfını bulup uygun taban stat'lerle başlatıyor.

#### Önce / Sonra
**Önce** (`engine.py` Faz 0):
```python
def create_character(self, name, element, ability_name, is_player):
    if element == "fire":
        hp = 25; atk = 10
    elif element == "cryo":
        hp = 28; atk = 8
    elif element == "electro":
        hp = 22; atk = 11
    elif element == "hydro":
        hp = 30; atk = 7
    else:
        raise ValueError(...)
    c = Character(name, element, ability_name, hp, atk, is_player)
    ...
```

**Sonra** (`engine.py` Faz 1):
```python
def create_character(self, name, element, ability_name, is_player):
    character = CharacterFactory.create(
        element=element, name=name,
        ability_name=ability_name, is_player=is_player,
    )
    return self.add(character)
```

#### Ne Kazandık
- **OCP uyumu:** Yeni element eklemek için `engine.py`'yi değiştirmek gerekmiyor; sadece yeni `Character` alt sınıfı yazıp `CharacterFactory.register("geo", GeoCharacter)` çağırmak yeterli.
- **Polimorfizm:** `character.element` artık bir property, string field değil; alt sınıf tarafından override ediliyor.
- **Sorumluluk ayrımı:** Yaratım mantığı motordan çıkıp `characters/` paketine taşındı — God Class biraz daha küçüldü.

---

### 2. Builder

**Kategori:** Creational
**Konum:** [`src/game/characters/builder.py`](src/game/characters/builder.py)
**İlgili PROBLEMS.md maddesi:** #3 (Yaratım sabit — runtime esnekliği yok)

#### Sorun
`engine.create_character(name, element, ability_name, is_player)` pozisyonel/keyword argüman zinciri ile çalışıyordu. Yeni bir özellik eklemek (örn. başlangıç HP ya da custom attack power) imzayı değiştirip mevcut tüm çağırımları güncellemek demekti. Ayrıca 3v3 dövüşte 6 karakter kurulumu okuması zor bir cümle dizisine dönüşmüştü.

#### Çözüm
`CharacterBuilder` fluent API ile karakter inşa eder:
```python
character = (
    CharacterBuilder()
    .with_name("Pyra")
    .with_element("fire")
    .with_ability("fire_blast")
    .for_team("player")
    .build()
)
```

`build()` zorunlu alanları kontrol eder; eksiklikleri açık hata mesajıyla reddeder. Opsiyonel `with_hp()` / `with_attack_power()` ile element default'larını override edebilirsin.

Builder içinde nesneyi gerçekten yaratan yine Factory'dir — yani iki örüntü birlikte çalışıyor: Builder konfigürasyonu toplar, Factory üretir.

#### Ne Kazandık
- **Okunabilirlik:** Takım kurulumu artık veri (rosters listesi) + uniform inşa döngüsü; 6 satır kopyala-yapıştır kodu yerine.
- **Esneklik:** Yeni opsiyonel alan eklemek (örn. başlangıç buff'ı) Builder'a tek metot eklemek demek; mevcut çağrılar bozulmaz.
- **Validasyon noktası:** Eksik field'lar build zamanında yakalanır, runtime'da değil.
- **Gerçek değer "custom draft"ta görünür:** `src/game/characters/roster.py` 8 hazır karakter şablonu sunuyor. `main.setup_custom_battle` oyuncuya havuzdan seçtirir, her seçim için aynı Builder akışı çalışır. Aynı altyapı hem "quick start" (default takımlar) hem de "custom draft" (kullanıcı seçer) modunu destekliyor — Builder'ın esnekliğinin somut karşılığı.

---

## UML

- **Önce:** [docs/diagrams/phase1-before.puml](docs/diagrams/phase1-before.puml)
- **Sonra:** [docs/diagrams/phase1-after.puml](docs/diagrams/phase1-after.puml)

## AI Etkileşim Kaydı

- [docs/ai-log/phase1.md](docs/ai-log/phase1.md) — Faz 1 sırasında AI ile yapılan tartışmalar.

---

## Faz 2 — Structural Örüntüler

### 3. Composite — Team

**Kategori:** Structural
**Konum:** [`src/game/team.py`](src/game/team.py)
**İlgili PROBLEMS.md maddeleri:** #5 (kod tekrarı — AoE döngüleri), #7 (HP-cap hack iki yerde tekrarlanıyor)

#### Sorun
Faz 1 sonunda `engine.player_team` ve `engine.enemy_team` ham `list[Character]` idi. Engine içinde "hayatta olanlara dağıt" desenli üç ayrı kod bloğu vardı:
- `Hydro→Electro` reaksiyonu — tüm rakip takıma 1.5x AoE
- `Thunder Chain` yeteneği — tüm rakipler 0.6x
- `Tidal Wave` yeteneği — tüm rakipler 0.8x

Üçünde de aynı pattern tekrarlanıyordu: `for c in self.alive(team): c.hp -= damage`. Ayrıca her saldırı ve yetenek sonunda HP'leri 0'a çekmek için aynı 4 satırlık döngü iki kere yazılmıştı.

#### Çözüm
`Team` sınıfı üyeleri tek bir nesne gibi yönetir — Composite örüntüsünün hedefi tam bu:

```python
class Team:
    def alive_members(self): ...
    def is_defeated(self): ...
    def apply_to_each(self, fn): ...
    def take_damage_each(self, amount, source_element=None): ...
    def tick_statuses(self): ...
    def apply_effect_to(self, member, effect_factory): ...
```

Engine artık `opp_team.take_damage_each(split)` çağırıyor — döngü Team içinde. `__iter__`, `__len__`, `__getitem__` shim'leri sayesinde `for c in engine.player_team` gibi mevcut kullanımlar değişmedi.

#### Önce / Sonra
**Önce** (Faz 1, `engine.py`):
```python
opp_team = self.opponent_team_of(attacker)
living = self.alive(opp_team)
split = max(1, total_damage // len(living))
for victim in living:
    victim.hp -= split
    self._announce_hit(attacker, victim, split)
# ... ve her saldırının sonunda:
for team in (self.player_team, self.enemy_team):
    for c in team:
        if c.hp < 0: c.hp = 0
```

**Sonra** (Faz 2):
```python
opp_team = self.opponent_team_of(attacker)
for victim, actual in opp_team.take_damage_each(split, source_element=attacker.element):
    self._announce_hit(attacker, victim, actual)
# HP-cap döngüsü tamamen silindi — take_damage zaten 0'a clamp ediyor.
```

#### Ne Kazandık
- **Tek kaynak:** AoE mantığı tek yerde (`Team.take_damage_each`); reaksiyonlar ve yetenekler aynı API'yi kullanıyor.
- **HP-cap hack silindi:** `Character.take_damage` artık negatif HP'ye izin vermiyor; iki yerdeki post-loop temizlik kodu gitti.
- **Defeat kontrolü adlı bir kavram oldu:** `team.is_defeated()` — engine artık `not self.alive(team)` gibi negatif okumalar yapmıyor.
- **Decorator zinciri için altyapı:** `Team.apply_effect_to` üyenin slot'unu wrapped versiyonla değiştirir — Decorator referans bütünlüğünü Team koruyor.

#### Neden Composite (Adapter/Facade değil)
- **Adapter** roster dict→Character dönüşümünü Builder zaten yapıyor; ekstra bir adapter katmanı gereksiz tekrar olurdu.
- **Facade** engine'in dış arayüzünü sadeleştirirdi (`GameSession.start()` gibi) ama içerdeki AoE tekrarına çare olmazdı. Composite tam olarak "bir grup nesneyi tek nesne gibi davrandır" sorununa odaklı.

---

### 4. Decorator — StatusEffect

**Kategori:** Structural
**Konum:** [`src/game/effects/status.py`](src/game/effects/status.py)
**İlgili PROBLEMS.md maddesi:** #6 (status efektleri Character'a sızıyor), #8 (frozen_turns özel mantığı engine'e dağılmış)

#### Sorun
Faz 1'de tek bir status efekti vardı: `frozen_turns: int` alanı [src/game/characters/base.py](src/game/characters/base.py) üzerinde. Bu yaklaşım her yeni etki için Character'a yeni alan eklemek demek (yanma için `burning_turns`, şok için `shocked`, vs.) — God Class büyür, render kodu her status'u ayrı kontrol etmek zorunda kalır, statuslar birbiriyle compose edilemez.

#### Çözüm
`StatusEffect` soyut Decorator'ı Character'ı sarar ve aynı arayüzü konuşur. Concrete decorator'lar yığılabilir (Character → BurningStatus → FrozenStatus → ShockedStatus), her biri kendi davranışını ekler.

```python
class StatusEffect(Character):
    def __init__(self, wrapped):
        object.__setattr__(self, "_wrapped", wrapped)

    def __getattr__(self, name):
        return getattr(self._wrapped, name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            setattr(self._wrapped, name, value)

    def take_damage(self, amount, source_element=None):
        return self._wrapped.take_damage(amount, source_element)

    def tick(self): ...
    def should_skip_turn(self): ...
    def has_status(self, name): ...
```

Concrete'ler:
- **`BurningStatus`** — 3 tur boyunca her tur 2 sabit DoT. Fire→Hydro reaksiyonu tetikler.
- **`FrozenStatus`** — `should_skip_turn() → True` 1 tur boyunca. Cryo→Hydro reaksiyonu ve Freeze Ray yeteneği tetikler.
- **`ShockedStatus`** — bir sonraki gelen hasarı 1.5x amplifiye eder, sonra dağılır. Electro→Fire reaksiyonu tetikler (zaten var olan sıçrama mekaniğine ek).

#### Önce / Sonra
**Önce** (Faz 1, `engine.py`):
```python
elif attacker.element == "cryo" and target.element == "hydro":
    target.hp -= damage
    target.frozen_turns = 1   # Character üzerine field yaz
    self.log.append(...)
    self._announce_hit(attacker, target, damage)
# ...
def tick_status(self, character):
    if character.frozen_turns > 0:
        character.frozen_turns -= 1
        return False
    return True
```

**Sonra** (Faz 2):
```python
elif attacker.element == "cryo" and target.element == "hydro":
    actual = target.take_damage(damage, source_element=attacker.element)
    self._announce_hit(attacker, target, actual)
    opp_team = self.opponent_team_of(attacker)
    if target.hp > 0:
        opp_team.apply_effect_to(target, FrozenStatus)
        self.log.append(...)
# ...
def tick_status(self, character):
    if character.should_skip_turn():
        self.log.extend(character.tick())
        self.log.append(f"  ~ {character.name} donmus, sira atladi")
        return False
    self.log.extend(character.tick())
    return True
```

#### Ne Kazandık
- **Yeni etki = yeni sınıf:** Burning'i eklemek için Character'a `burning_turns` field'ı koymadık; `BurningStatus(StatusEffect)` yazdık. OCP burada somut.
- **Compose edilebilirlik:** Bir karakter aynı anda hem yanıyor hem donmuş olabilir; iki decorator zincire eklenir.
- **Status mantığı kendi sınıfında:** Engine `frozen_turns -= 1` gibi ayrıntıları bilmez; sadece `tick()` ve `should_skip_turn()` çağırır.
- **Render decoupled:** `c.has_status("frozen")`, `c.has_status("burning")` — her status için ayrı field okumak yerine uniform sorgu.

#### Referans bütünlüğü
Decorator sarıldığında team listesindeki referans değişir — eski Character pointer'ı bayatlamasın diye `Team.apply_effect_to` hem sarar hem listeyi günceller. Engine her zaman team listesi üzerinden okuduğu için (`opp_team[idx]`, `_resolve_single_target`) wrap sonrası tutarlılık otomatik korunur.

---

## Faz 2 UML

- **Önce:** [docs/diagrams/phase2-before.puml](docs/diagrams/phase2-before.puml)
- **Sonra:** [docs/diagrams/phase2-after.puml](docs/diagrams/phase2-after.puml)

## Faz 2 AI Etkileşim Kaydı

- [docs/ai-log/phase2.md](docs/ai-log/phase2.md) — Faz 2 sırasında AI ile yapılan tartışmalar, AI'ın eksik/yanlış önerilerinin eleştirisi.
