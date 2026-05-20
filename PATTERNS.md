# PATTERNS.md — Uygulanan Tasarım Örüntüleri

Bu dosya her fazda eklenen örüntüleri, neden seçildiklerini ve hangi sorunu çözdüklerini belgeler.

---

## Faz 1 — Creational Örüntüler

### 1. Factory Method

**Kategori:** Creational
**Konum:** [`src/game/characters/factory.py`](src/game/characters/factory.py)
**İlgili PROBLEMS.md maddesi:** #2 (Element type-check zincirleri) ve #4 (Yetenekler isim-bağımlı — kısmen)

#### Sorun
faz 0 da her karakter basit el if donguleri ile olusturuluyordu. Bu hem karısık bir kod yapısı hem de karakter olsustırma oynama ve kullanma aşamasında uzun kod yapıları kullanmamı gerekitiiriyordu

#### Çözüm
Önce soyut bir Character hiyerarşisi kuruldu: Bu soyut sınıf altına 4 adet alt sınıf acarak 4 elementteki karakterlerin ayrılmasını sağladım. Her alt sınıf kendi element property'sini ve default_stats classmethod'unu taşıyor.

Sonra `CharacterFactory` bir **registry tablosu** ile görevlendirme yapıyor:
```python
_registry = {
    "fire": FireCharacter,
    "cryo": CryoCharacter,
    "electro": ElectroCharacter,
    "hydro": HydroCharacter,
}
```


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


### 2. Builder

**Kategori:** Creational
**Konum:** [`src/game/characters/builder.py`](src/game/characters/builder.py)
**İlgili PROBLEMS.md maddesi:** #3 

#### Sorun
`engine.create_character(name, element, ability_name, is_player)` bir karakter oluşturulmaya çalışırken if els sorgu zincirleri ile uzun sorugular yapılarak karakter oluşturulabiliyordu

#### Çözüm
`CharacterBuilder` fonksiyonu ile sadece gerekli veriler girilerek karakter basitça oluşturulur.
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

build() zorunlu alanları kontrol eder; eksiklikleri açık hata mesajıyla reddeder.
 Opsiyonel `with_hp()` / `with_attack_power()` ile element default'larını override edebilir

Builder içinde nesneyi gerçekten yaratan yine Factory'dir — yani iki örüntü birlikte çalışıyor: Builder konfigürasyonu toplar, Factory üretir.

---


## Faz 2 

### 3. Composite — Team

**Kategori:** Structural
**Konum:** [`src/game/team.py`](src/game/team.py)
**İlgili PROBLEMS.md maddeleri:** #5 (kod tekrarı — AoE döngüleri), #7 (HP-cap hack iki yerde tekrarlanıyor)

#### Sorun
Faz 1 sonunda engine.player_team ve engine.enemy_team direk  `list[Character]` olarak tanımlanıstı . Engine içinde "hayatta olanlara dağıt" desenli üç ayrı kod bloğu vardı:
- `Hydro→Electro` reaksiyonu — tüm rakip takıma 1.5x AoE
- `Thunder Chain` yeteneği — tüm rakipler 0.6x
- `Tidal Wave` yeteneği — tüm rakipler 0.8x

Üçünde de aynı for dongulu kodlar tekrarlanıyordu: . Ayrıca her saldırı ve yetenek sonunda HP'leri 0'a çekmek için aynı 4 satırlık döngü iki kere yazılmıştı.

#### Çözüm
`Team` sınıfı üyeleri tek bir nesne gibi yönetir  boylece takıma hasar dağıtma işlemleri tüm takımın ölmesi gibi durumlarda kod pratikliği sağlanır.

```python
class Team:
    def alive_members(self): 
    def is_defeated(self): 
    def apply_to_each(self, fn): 
    def take_damage_each(self, amount, source_element=None): 
    def tick_statuses(self): 
    def apply_effect_to(self, member, effect_factory): 
```


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




- **Tek kaynak:** AoE mantığı tek yerde ; reaksiyonlar ve yetenekler aynı yapıyı kullanıyor
- **Defeat kontrolü adlı bir kavram oldu:** 

- **Adapter** roster dict→Character dönüşümünü Builder zaten yapıyor; ekstra bir adapter katmanı gereksiz tekrar olurdu.


### 4. Decorator
**Kategori:** Structural
**Konum:** [`src/game/effects/status.py`](src/game/effects/status.py)
**İlgili PROBLEMS.md maddesi:** #6, #8 

#### Sorun
Faz 1'de tek status vardı: `frozen_turns: int` alanı. Yanma eklemek için `burning_turns`'a yeni bir alan demekti. Üstelik bir karakter aynı anda hem donmuş hem yanıyor olamıyordu.

#### Çözüm
`StatusEffect` sınıfı Characteri ve aynı arayüzü konuşur. Status'lar yığılabilir: Character → BurningStatus → FrozenStatus. Her sarmal kendi davranışını ekler, geri kalanı içeriye iletir.


- **`BurningStatus`** — 3 tur, her tur 2 hasar (Fire→Hydro tetikler)
- **`FrozenStatus`** — 1 tur sıra atlatır (Cryo→Hydro ve Freeze Ray tetikler)
- **`ShockedStatus`** — bir sonraki hasarı 1.5x büyütür, sonra biter (Electro→Fire tetikler)

#### Önce / Sonra
**Önce:** `target.frozen_turns = 1` — Character'a doğrudan field yazılıyordu.

**Sonra:** `opp_team.apply_effect_to(target, FrozenStatus)` — target bir FrozenStatus ile sarılıyor, engine field'ı bilmiyor.

#### Ne Kazandık
- **Yeni etki = yeni sınıf:** Character'a alan eklemeden yeni davranış (OCP).
- **Birden fazla etki üst üste:** Bir karakter hem yanıyor hem donmuş olabilir.
- **Engine sade kaldı:** `tick()` ve `should_skip_turn()` çağırıyor, status'un kendisini bilmiyor.

---

## Faz 2 UML
## Faz 2 AI Etkileşim Kaydı

- [docs/ai-log/phase2.md](docs/ai-log/phase2.md) — Faz 2 sırasında AI ile yapılan tartışmalar, AI'ın eksik/yanlış önerilerinin eleştirisi.
