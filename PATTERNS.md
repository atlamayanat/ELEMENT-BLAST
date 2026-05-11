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
