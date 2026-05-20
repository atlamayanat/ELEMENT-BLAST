# Faz 2 — AI Etkileşim Kaydı (taslak)

> Bu dosya Faz 2 (Structural örüntüler) sırasında AI ile yapılan tartışmaları belgeler.
> Format: AI'a sorulan prompt, AI'ın yanıtı, benim kararım ve gerekçesi.
> **Faz 1'de yaptığım gibi bu dosyayı kendi kelimelerimle gözden geçireceğim** — şu an
> implementation sırasında oluşan ham düşünceleri yakalamaya odaklı taslak hali.

---

## 1. Hangi Structural Örüntülerini Seçtim ve Neden?

**Karar:** Decorator + Composite.

**Gerekçem:**
- PROBLEMS.md'de **madde 5** (AoE kod tekrarı — Hydro→Electro, Thunder Chain, Tidal Wave aynı döngüyü yazıyordu), **madde 6** (status efektleri Character'a sızıyor, sadece `frozen_turns` field'ı var, yeni etki = yeni field) ve **madde 7** (HP-cap hack iki yerde tekrarlanıyor) bu fazın çözmesi gereken acılardı.
- **Composite (Team):** `list[Character]` ham bir yapıydı. AoE her seferinde `for c in self.alive(team): c.hp -= dmg` tekrarıydı. Team'in "üyelerin toplamı gibi davranabilen bir nesne" olması bu tekrarı tek metoda topladı. HP-cap döngüsü de gitti — `Character.take_damage` 0'a clamp ediyor artık.
- **Decorator (StatusEffect):** Faz 1'den sonra yanma, şok gibi yeni status'lar eklemek istesem her birine Character üzerine yeni bir field açmam gerekirdi. Decorator zinciri ile bir karakter aynı anda hem yanıyor hem donmuş olabiliyor; engine içeriğini bilmiyor sadece `tick()` ve `should_skip_turn()` çağırıyor.

**Alternatifler neden reddedildi:**
- **Facade:** engine'in DIŞ arayüzünü sadeleştirirdi (`GameSession.start()` gibi) ama içerdeki AoE tekrarına çare olmazdı. Asıl ağrı engine'in iç kodundaydı, dış API'nin karmaşıklığında değil.
- **Adapter:** Builder zaten roster dict → Character dönüşümünü yapıyor. Adapter eklemek ekstra katman olurdu, gerçek bir uyumsuzluk yok.
- **Bridge:** Karakter ve element ayrımı zaten Factory + alt sınıflar ile çözülmüş durumda.
- **Flyweight / Proxy:** Bu sistemde paylaşılacak immutable state veya erişim kontrolü ihtiyacı yok.

---

## 2. AI ile Yapılan Tartışmalar

### Tartışma 1: Status efektleri için Decorator mı, "effects list" mi?

**AI'a sorduğum:**
> Karakterin üzerinde birden fazla status efekti olabilmeli (yanma, donma, şok). Bunu nasıl tasarlamalıyım?

**AI'ın yanıtı (özet):**
İlk önerisi tipik olarak şu yönde geldi: "Character üzerine `effects: list[Effect]` ekleyin. Her tur engine `for e in character.effects: e.apply(character)` çağırır. Effect'ler `apply(target)`, `is_expired()`, `name` taşır. Bu kompozisyon her ihtiyacı karşılar ve Decorator'a göre daha az boilerplate gerektirir."

**Benim kararım:**
AI'ın önerdiği "effects list" yaklaşımı pratikte basit ama bu ödevin gerçek niyetine ters: ben yapısal örüntü uygulamak için buradayım, "field of effects" yaklaşımı sadece bir kompozisyondur — herhangi bir yapısal örüntü değildir. Decorator'ın gerçek değeri, sarılan nesneyle aynı arayüzü konuşması ve şeffaf bir şekilde yığılabilmesi: engine `target.take_damage(dmg)` çağırınca damage chain otomatik olarak amplifier'lardan (ShockedStatus gibi) geçiyor. "Effects list" ile bunu yapmak için engine'in her status'u tek tek dolaşması gerekirdi.

Decorator'ı seçtim. Implementation'da `StatusEffect(Character)` sarmacı + `__getattr__`/`__setattr__` forwarding kullandım.

---

### Tartışma 2: Team list'in __iter__ shim'leri yeterli mi?

**AI'a sorduğum:**
> player_team'i list'ten Team class'ına çevirsem main.py'deki `for c in engine.player_team` döngüleri kırılır mı?

**AI'ın yanıtı (özet):**
"Team'e `__iter__`, `__len__`, `__getitem__` magic method'larını eklerseniz mevcut çağrılar değişmeden çalışır. Ancak engine'de `self.player_team.append(x)` veya benzeri list-specific çağrılar varsa onları `add()` metoduna güncellemeniz gerekir."

**Benim kararım:**
Bu öneri doğruydu. Engine'de `append` kullanan tek yer `add()` metoduydu — onu `team.add(character)` yaptım. main.py hiç değişmedi. Bu güzel — Faz 2'nin "yapısal değişiklik ama mevcut davranışı koru" felsefesine tam uyuyor.

---

### Tartışma 3: Decorator sarıldığında team listesindeki referans ne oluyor?

**AI'a sorduğum:**
> BurningStatus(target) ile target'i sarınca, attack() içindeki local `target` değişkeni hala eski (sarılmamış) Character'ı gösteriyor. Bu sorun olur mu?

**AI'ın yanıtı (özet):**
"Local `target` referansı sarmadan sonra bayatlamaz çünkü Decorator'ın `__setattr__` ve `take_damage` metodları wrapped Character üzerinde mutasyon yapıyor. Aynı hp field'ına iki yoldan da ulaşılıyor."

**Benim eklediğim (AI'ın atladığı):**
AI bu sorunun yarısını gördü ama önemli bir kısmı atladı: bir SONRAKI tur, engine team listesinden okuduğunda artık SARILMIŞ referansı görüyor. Yani `attack()` içindeki local target ile takım üyeleri arasında **geçici bir referans uyumsuzluğu** var — ama bu sadece `attack()` çağrısı süresince. Çağrı bittikten sonra herkes wrapped versiyonu görüyor. Bu yüzden `Team.apply_effect_to(member, factory)` metodu ÖNEMLİ: hem sarmayı yapıyor hem de team listesinin slot'unu güncelliyor. Engine'in sarmayı doğrudan `target = BurningStatus(target)` ile yapmasına izin vermedim — Team içinden geçirdim. Bu kararı kendi başıma aldım.

---

## 3. AI'ın Yanılttığı / Eksik Önerdiği Şeyler (KRİTİK)

Ödev rubric'inde bu bölüm özellikle vurgulanıyor; gerçek eleştiri burada.

### 3.1 — "Effects list" önerisi pattern gereksinimini kaçırıyor

AI'ın ilk önerisi (Tartışma 1) hızlı ve pratik ama **ödevin yapısal örüntü gereksinimini karşılamıyor**. AI "en kısa yoldan çalışan kod" optimizasyonu yapıyor; ben "doğru yapısal örüntüyü öğreniyorum" optimizasyonu yapıyorum. Bu iki hedef her zaman aynı yere gitmiyor. Pattern öğrenmek bazen ekstra boilerplate kabul etmek demek.

Bunu farkettim çünkü AI'ın yanıtında "Decorator" kelimesi geçti ama "ama bu projede gereksiz karmaşıklık" diye geçiştirildi. Eğer pattern eğitim amaçlı yazılmıyorsa o not doğru — ama burada amaç tam tersi.

### 3.2 — Referans güncellemesini Team'den geçirme önerisini AI yapmadı

Tartışma 3'te yazdığım gibi, AI Decorator wrapping'i `target = BurningStatus(target)` şeklinde "in-place" göstermeye eğilimliydi. Team listesinin slot'unun güncellenmesi gerektiğini ben fark ettim ve `Team.apply_effect_to` metodunu bunun için yazdım. Bu olmasaydı eski referanslar etkiyi taşımayan bir karakteri gösterecekti, bug çıkacaktı.

### 3.3 — Frozen status decorator'ı zincirde kalması sorunu

AI önerdi: "FrozenStatus süresi dolunca dağıtılır". Pratikte bunu yapmak için zincirden çıkarmak demek — ki bu da `_wrapped` zincirinin yeniden örülmesi anlamına geliyor (çünkü ortadaki bir decorator'ı çıkarmak parent-child ilişkisini yeniden bağlamayı gerektiriyor). Şu an süresi dolan FrozenStatus zincirde kalıyor ama `_remaining == 0` olduğu için `should_skip_turn()` False döndürüyor — yani **no-op decorator** olarak duruyor. Bu trade-off: bellek temizliği vs. kod karmaşıklığı. Pragmatik tercih: no-op olarak bıraktım, Faz 3 cleanup'ında ilgilenirim. AI bu trade-off'u açıkça söylememişti; ben deneyerek anladım.

---

## 4. Faz 2 Süresince Geçen Süre

- **Tahmini:** ~5-7 saat (plan dosyasında)
- **Gerçek:** ~3 saat (Faz 1'deki gibi AI ile çift programlama hızlı ilerletti)
- **AI olmadan ne kadar sürerdi?** Çok daha uzun — özellikle Decorator forwarding'i Python'da __getattr__/__setattr__ ile yazmanın kıvrımları (`object.__setattr__` ile recursive setattr'dan kaçınmak gibi) AI olmadan birkaç saat fazladan denediğim hata olurdu.

---

## 5. Faz 2 Özeti

**Yeni Dosyalar:**
- `src/game/team.py` — Composite Team sınıfı
- `src/game/effects/__init__.py` — paket
- `src/game/effects/status.py` — StatusEffect (Decorator) + Burning/Frozen/Shocked
- `docs/diagrams/phase2-before.puml` — yapı öncesi
- `docs/diagrams/phase2-after.puml` — Decorator + Composite sonrası

**Değiştirilen Dosyalar:**
- `src/game/characters/base.py` — `take_damage`, `tick`, `should_skip_turn`, `apply_effect`, `has_status` eklendi; `frozen_turns` field'ı kaldırıldı
- `src/game/engine.py` — `player_team`/`enemy_team` Team oldu, AoE blokları Team API'sine geçti, HP-cap hack silindi, `tick_status` `should_skip_turn`/`tick` üzerinden
- `PATTERNS.md` — Composite ve Decorator için iki yeni bölüm

**Çözülen Problemler (PROBLEMS.md'den):**
- #5 — AoE kod tekrarı: Team.take_damage_each tek noktada
- #6 — Status efektleri Character'a sızıyor: Decorator zincirine taşındı
- #7 — HP-cap hack iki yerde: take_damage clamp ile gitti

**Bilinçli olarak henüz çözülmeyen (Faz 3'e bırakılan):**
- Reaksiyon if-elif zinciri (engine.attack içinde): Chain of Responsibility / Strategy
- Yetenek if-elif zinciri (engine.use_ability içinde): Strategy
- enemy_decide AI mantığı: Strategy
- engine.log.append doğrudan çağrıları: Observer
- CI/CD: GitHub Actions

**Yeni Gameplay Davranışları:**
- Fire→Hydro: 1.5x hasar + 3 tur yanma (DoT)
- Cryo→Hydro: hasar + 1 tur donma (status decorator üzerinden)
- Electro→Fire: hasar + sıçrama + Shocked status (bir sonraki hasar +%50)
- Freeze Ray yeteneği: hasar + 1 tur donma
