# Mini Oyun Motoru — Yazılım Tasarım Örüntüleri Ödevi

**Konu Seçimi: C — Mini Oyun Motoru**

3v3 sıra tabanlı elemental dövüş seçildi: dört element arasındaki reaksiyon kuralları (Fire→Cryo 2x, Cryo→Hydro freeze, Hydro→Electro yayılma, …) ve karaktere özel yetenekler, tasarım örüntülerini "neden gerekli" sorusuna doğal yanıt veren bir alan oluşturuyor; aynı sistem pygame ile sonradan görselleştirildiğinde motorun gerçekten genişletilebilir olduğunu kanıtlıyor.

---

## Sistem Özeti

**Elementler:** Fire, Cryo, Electro, Hydro

**Reaksiyon Tablosu:**

| Saldıran | Hedef | Etki |
|----------|-------|------|
| Fire | Cryo | 2× hasar |
| Electro | Fire | Normal hasar + rasgele başka düşmana hasarın %75'i sıçrar |
| Hydro | Electro | Hasar 1.5× ile çarpılıp **tüm rakip takıma** paylaştırılır |
| Cryo | Hydro | Normal hasar + hedef 1 tur **donar** (sırasını atlar) |
| Fire | Hydro | 1.5× hasar |
| Hydro | Fire | 1.5× hasar |

Diğer kombinasyonlar normal hasar verir.

**Karakter modeli:** her karakterin `name`, `hp`, `attack_power`, `element` ve **tek bir özel yeteneği** (`ability_name`) var. Yetenekler karakteri tanımlar.

**Takım yapısı:** her oyuncu 3 karakter kontrol eder. Tüm takım üyeleri ölünce dövüş biter.

---

## Durum: Faz 0 (Başlangıç)

Şu anda kasıtlı olarak kötü tasarlanmış bir başlangıç kodu var:

- Tek bir `GameEngine` God Class her şeyi yapıyor (yaratım, hasar, reaksiyonlar, yetenekler, AI, render).
- Element tipleri ve reaksiyonlar `if-elif` zincirleriyle ayırt ediliyor.
- Yetenekler karakter ismine göre dispatch ediliyor; karakter ile motor sıkı kenetlenmiş.

Tüm sorunların listesi: [PROBLEMS.md](./PROBLEMS.md).

## Nasıl Çalıştırılır

Python 3.11+ gerekli. Proje kökünden (bu README'nin bulunduğu klasör):

```bash
python run.py
# veya
python -m src.game.main
```

> IDE'den (VS Code "Run Python File") çalıştırırken **`run.py`'yi açıp çalıştırın**, `main.py`'yi değil — `main.py` paket içinden çağrıldığı varsayımıyla import yapıyor.

Her tur:
1. Karakter no seç (0/1/2),
2. Aksiyon seç (`a` saldırı, `s` özel yetenek),
3. Saldırı ise hedef no seç (rakip takımdan).

Sonra düşman takımı otomatik aksiyonunu yapar.

## Yol Haritası

| Faz | Branch | Konu | Puan |
|-----|--------|------|------|
| 0 | `main` | Bilinçsiz başlangıç kodu (3v3 + 4 element + 6 reaksiyon, tek God Class) | — |
| 1 | `phase-1` | Creational örüntüler (Factory Method + Builder) | 25 |
| 2 | `phase-2` | Structural örüntüler (Decorator + Composite + Facade) | 30 |
| 3 | `phase-3` | Behavioral örüntüler (Strategy + Observer + Chain of Responsibility) | 35 |
| Bonus | `feat/pygame-ui` | pygame UI (Observer'ın meyvesi) | — |

## Repo Yapısı

```
.
├── README.md           ← bu dosya
├── PATTERNS.md         ← her fazda eklenir
├── PROBLEMS.md         ← Faz 0 analizi
├── pyproject.toml
├── src/game/           ← kaynak kod
├── tests/              ← pytest
├── docs/
│   ├── diagrams/       ← UML
│   └── ai-log/         ← AI etkileşim kayıtları
└── .github/workflows/  ← CI (Faz 3)
```
