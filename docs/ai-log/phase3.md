# Faz 3 — AI Etkileşim Kaydı (taslak)

> Bu dosya Faz 3 (Behavioral örüntüler + CI + README) sırasında AI ile yapılan ≥30 dk pair programming oturumunun kaydıdır.
> Format: AI'a sorulan prompt, AI'ın yanıtı, benim kararım ve gerekçesi.
> **Faz 1-2'de yaptığım gibi bu dosyayı kendi kelimelerimle gözden geçireceğim** — şu an implementation sırasında oluşan ham düşünceleri yakalamaya odaklı taslak hali.

---

## 1. Hangi Behavioral Örüntülerini Seçtim ve Neden?

**Karar:** Strategy (yetenekler + enemy AI) + Chain of Responsibility (reaksiyonlar).

**Gerekçem:**
- PROBLEMS.md **madde 4** (yetenek if-elif) ve **madde 5** (AI tek tip) için en doğal çözüm Strategy. Her yetenek ve AI varyantı kendi sınıfına çıkarılır, engine sadece `character.ability.execute(...)` çağırır.
- engine.attack içindeki 7 reaksiyon if-elif'i için Chain of Responsibility ideal: her reaksiyon bir handler, zincir sırayla denenir, ilk eşleşen kazanır. Yeni reaksiyon = yeni handler + chain.append. OCP demosu burada somut.
- enemy AI için sadece **1 varyant** (DefensiveAI — mevcut davranışı sarıyor) seçtim. Boilerplate'i koyalım, Strategy'nin yapısı net olsun. İkinci varyant gerektiğinde sadece yeni sınıf yazılır.

**Alternatifler neden reddedildi:**
- **Observer:** `engine.log.append` çağrılarını event bus'a çevirmek temiz olurdu (özellikle ileride pygame'e geçişte) ama 2 örüntü minimum yeterli; scope'u şişirmemek için Faz 3'te eklenmedi. Future work olarak duruyor.
- **Command:** undo/redo gereksinimi yok; sıra tabanlı dövüşte aksiyonlar zaten anlık.
- **State:** Game phases (Setup/PlayerTurn/EnemyTurn/GameOver) için iyi olurdu ama main.py while-loop'u zaten yeterince sade.

---

## 2. AI ile Yapılan Tartışmalar

### Tartışma 1: Reaksiyon CoR'da context dataclass mı, parameter passing mi?

**AI'a sorduğum:**
> Her ReactionHandler.apply'a 5 farklı parametre geçirmek istemiyorum. Context dataclass mı yapayım, yoksa **kwargs ile mi geçeyim?

**AI'ın yanıtı (özet):**
"Dataclass kullan. Avantajlar: tip ipuçları, IDE autocompletion, immutability (frozen=True ile), test edilebilirlik. **kwargs runtime'a kadar hata vermez."

**Benim kararım:**
Dataclass'ı seçtim — `ReactionContext(attacker, target, opp_team, base_damage, engine)`. Frozen=True yapmadım çünkü engine referansını handler'lar üzerinden mutate ediyor (log.append vs.); dataclass mutable ama field'lar tip ipucu sağlıyor.

---

### Tartışma 2: Handler'lar engine'e doğrudan side-effect mi uygulasın yoksa ReactionResult mı döndürsün?

**AI'a sorduğum:**
> Handler bir Result dataclass döndürse de engine bunu okuyup log/status uygulasa daha temiz olur mu? Şu an handler'lar engine.log.append ve opp_team.apply_effect_to çağırıyor — bu sıkı kenetlenme değil mi?

**AI'ın yanıtı (özet):**
"İdeal olarak Result döndürsün — handler pure function olur, test edilebilirlik artar. Ama bu refactor ek 50-100 satır demek (Result dataclass + per-handler result kurma + engine'de switch ile uygulama). Pragmatik tercih: handler'lar side-effect uygulasın, bu Single Responsibility'yi minimal şekilde ihlal eder ama kod basitleşir."

**Benim kararım:**
AI'ın pragmatik önerisini aldım. Handler'lar ctx.engine üzerinden side-effect uyguluyor. Refactor istenirse ReactionResult sonradan eklenebilir. Şu an "engine'i ince tut + handler'lar her şeyi yapsın" tercihi okunabilirliği koruyor.

---

### Tartışma 3: fire_blast element-mutate hack'inden nasıl kurtuluruz?

**AI'a sorduğum:**
> Faz 1-2'de fire_blast use_ability içinde `character.element = "fire"; ...; character.element = saved` hack'i vardı çünkü take_damage element tipinden reaksiyon tetikliyordu. Strategy'de bu hack nasıl yok olur?

**AI'ın yanıtı (özet):**
"Take_damage zaten `source_element` parametresi alıyor (Faz 2'de eklendi). Strategy execute içinde `target.take_damage(damage, source_element='fire')` yeterli — character.element'i değiştirmeye gerek yok. Yetenek hasarı reaksiyon tetiklemiyor zaten (engine.attack ↔ engine.use_ability ayrı yollar). source_element parametresi sadece bilgi amaçlı/log için."

**Benim kararım:**
Aynen önerildiği gibi: `FireBlastStrategy.execute` artık element mutate etmiyor, source_element="fire" parametresini doğrudan geçiriyor. Hack tamamen silindi. **Bu Strategy'nin Phase 3'teki temizleme efektine somut bir örnek** — eski hack'lar pattern uygulayınca kendiliğinden gereksiz hale geliyor.

---

## 3. AI'ın Yanılttığı / Eksik Önerdiği Şeyler (KRİTİK)

### 3.1 — Circular import'u baştan görmedi

İlk implementation'da factory.py top-level `from src.game.abilities import registry as ability_registry` yaptım. AI bunu sorgulamadan kabul etti. Test çalıştırınca circular import patladı:

```
abilities → effects → characters.base → characters/__init__ → factory → abilities (LOOP)
```

AI'a sormuş olsam "lazy import yapalım" diyebilirdi ama proaktif olarak söylemedi. Ben pytest hatası gördükten sonra çözdüm — `factory.py` `create()` içine lazy import koydum. Bu Python import sistemini iyi bilmenin AI üstüne çıktığı bir nokta.

### 3.2 — DefensiveAI tek varyant olunca "OCP demo" zayıflığı

Plan'da AI Strategy için 3 varyant öneriliyordu (Aggressive/Defensive/Berserker). Ben tek varyant seçtim. AI bu kararı sorgulamadan kabul etti ama eklemesi gerekirdi: "Tek varyantla Strategy'nin gücü gösterilemez — OCP demo için ya yeni AI varyantı ekleyin ya da ana OCP demosunu CoR'a kaydırın." Ben bu trade-off'u kendi başıma fark ettim ve OCP demosunu CoR'a (yeni reaction handler) bağladım. PR description'da bunu açıkça yazdım.

### 3.3 — Smoke test'lerde wrapped reference assertion'ı yanıltıcı olabilirdi

Test yazarken `isinstance(e.enemy_team[0], BurningStatus)` assertion'ı koydum. AI bunu önerdi ama dikkat: BurningStatus zincirin EN ÜSTÜNDEYSE bu çalışır. Eğer önce FrozenStatus ekleyip sonra BurningStatus ekleseydim sıra: `BurningStatus(FrozenStatus(Character))`, isinstance hâlâ True döner (en dış). Ama tersi olsa (`FrozenStatus(BurningStatus(Character))`), `isinstance(..., BurningStatus)` False döner. AI bu nüansı sessiz geçti — gerçek test daha sağlam olmalı (`has_status("burning")` ile).

Şu anki testlerde wrapping sırası tek seviye olduğu için sorun yok ama not aldım.

---

## 4. Faz 3 Süresince Geçen Süre

- **Tahmini:** ~8-10 saat (plan dosyasında)
- **Gerçek:** ~3.5 saat (pair programming ile)
- **AI olmadan ne kadar sürerdi?** En az 2-3 katı. Özellikle:
  - ReactionContext + handler hiyerarşisini sıfırdan kurmak
  - CI YAML syntax'ını ezbere bilmemek
  - Mermaid class diagram syntax'ı (README için)
  - Circular import çözümü (lazy import idiom)

**AI sizi nerede yanılttı?** Yukarıda 3.1, 3.2, 3.3'te detayını verdim. Özetle: AI "şu anda çalışan kod" yazıyor, "uzun vadeli sağlam kod" yazmıyor. Trade-off'ları kendi başıma görmek zorundayım.

---

## 5. Faz 3 Özeti

**Yeni Dosyalar (14 yeni):**
- `src/game/abilities/` — base, 4 strategy, registry, __init__
- `src/game/ai/` — base, DefensiveAI, __init__
- `src/game/reactions/` — context, base, handlers, __init__
- `tests/test_smoke.py` + `tests/__init__.py`
- `.github/workflows/ci.yml`
- `docs/diagrams/phase3-before.puml`, `phase3-after.puml`

**Değişen Dosyalar:**
- `src/game/characters/base.py` — `ability_name: str` → `ability: AbilityStrategy`, `ai_strategy` field eklendi
- `src/game/characters/builder.py` — `with_ai()` metodu eklendi
- `src/game/characters/factory.py` — strategy injection + lazy import
- `src/game/engine.py` — attack/use_ability/enemy_decide tek satıra düştü; fire_blast element hack silindi; ReactionChain field eklendi
- `src/game/main.py` — ability.display_name + ability.is_single_target üzerinden çalışıyor (sabit dict'ler silindi)
- `README.md` — baştan yazıldı (Mermaid mimari diyagramı, pattern tablosu, OCP demo)
- `PATTERNS.md` — Faz 3 bölümü eklendi

**Çözülen Problemler:**
- #2 (kısmen Faz 1'de) — reaksiyon if-elif zinciri tamamen kalktı (CoR)
- #4 — yetenek if-elif zinciri kalktı (Strategy)
- #5 — AI Strategy boilerplate'i hazır (1 varyant ama yapı tamam)
- #10 (bonus) — fire_blast element-mutate hack temizlendi

**Test Kapsamı:**
- 12 smoke test, 12/12 passing
- OCP demo testi (yeni reaction handler ekleyip engine'e dokunmadan)
- CI workflow her push'ta otomatik

**Toplam Kod İstatistiği (yaklaşık):**
- engine.py: 250 satır → 130 satır (-48%)
- Yeni paketler: ~450 satır (modüler, izole, test edilebilir)
- Net: Engine sade, sorumluluk dağılmış, OCP somut.

**Future Work (Faz 4 olsa):**
- Observer — log decoupling, pygame entegrasyonu için temel
- Daha fazla AI varyantı (Aggressive, Berserker, Healer)
- Reaction priority system (handler'lar çakıştığında)
