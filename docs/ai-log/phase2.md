# Faz 2 — AI Etkileşim Kaydı

> Bu dosya Faz 2 (Structural örüntüler) sırasında AI ile yapılan tartışmaları belgeler.
> Format: AI'a sorulan prompt, AI'ın yanıtı, benim kararım ve gerekçesi.

---

## 1. Hangi Structural Örüntülerini Seçtim ve Neden?

**Karar:** Composite (Team) + Decorator (StatusEffect).

**Gerekçem:**
- PROBLEMS.md **madde 5** te oyun içerisinde tüm takıma hasar veren bazı etkiler var (electro chain gibi). Bu olaylarda uzun for döngülerinde her karakter için ayrı hasar hesaplanıyordu, karısık bir yapı sunuyordu. 2 takımı da ayrı nesneler olarak ele alınca alan hasar, genel tepkimeler, bir takımın tüm canının bitmesi gibi etkilerin hesaplanması kolaylaştı.
- **Decorator** içinde: Faz 1'den sonra yanma, şok gibi yeni status'lar eklemek istesem her birine Character üzerine yeni bir field açmam gerekirdi. Bu da bir karakterin aynı anda 2 farklı element etkisi altında olmasını engellerdi. Bunu çözmek için statüleri ayrı sınıflar olarak yığın halinde tutuyorum — mesela bir karakter yanma etkisindeyken aynı zamanda donabilir.


---

## 2. AI ile Yapılan Tartışmalar

### Tartışma 1: Status efektleri için Decorator mı, "effects list" mi?

**AI'a sorduğum:**
> Karakterin üzerinde birden fazla status efekti olabilmeli (yanma, donma, şok). Bunu nasıl tasarlamalıyım?

**AI'ın yanıtı (özet):**
İlk önerisi: "Character üzerine `effects: list[Effect]` ekleyin. Her tur engine `for e in character.effects: e.apply(character)` çağırır. Bu kompozisyon her ihtiyacı karşılar ve Decorator'a göre daha az boilerplate gerektirir."

**Benim kararım:**
AI'ın önerdiği "effects list" basit ama bu ödevin niyetine ters: ben yapısal örüntü uygulamak için buradayım, field of effects sadece bir kompozisyon — yapısal örüntü değil. Decorator'ı seçtim çünkü sarılan nesneyle aynı arayüzü konuşuyor: 



---

### Tartışma 2: Decorator etkilendiğinde team listesindeki referans ne oluyor?

**AI'a sorduğum:**
> BurningStatus(target) ile target'i etkileyince, attack() içindeki local `target` değişkeni hala eski Character'ı gösteriyor. Bu sorun olur mu?

**AI'ın yanıtı (özet):**
"Local `target` bayatlamaz çünkü Decorator'ın `__setattr__` ve `take_damage` metodları wrapped Character üzerinde mutasyon yapıyor."

**Benim eklediğim:**
AI sorunun yarısını gördü ama bir SONRAKI tur engine team listesinden okuduğunda artık etkilenmiş targetin referansı görecek. Yani team listesinin slot'unun güncellenmesi gerekiyor bunu AI söylemedi. Ben soyledim yaptı 

---

## 3. AI'ın Yanılttığı / Eksik Önerdiği Şeyler (KRİTİK)

### 3.1 — "Effects list" önerisi pattern gereksinimini kaçırıyor
AI'ın ilk önerisi pratikte basit ama ödevin yapısal örüntü gereksinimini karşılamıyor. AI "en kısa yoldan çalışan kod" istiyor; ben "doğru yapısal örüntüyü öğreniyorum". Bu iki hedef her zaman aynı yere gitmiyor.

### 3.2 — Team slot'unun güncellenmesini AI söylemedi
Tartışma 3'te yazdığım gibi, AI Decorator wrapping'i `target = BurningStatus(target)` şeklinde "in-place" göstermeye eğilimliydi. Team listesinin güncellenmesi gerektiğini ben fark ettim. Bu olmasaydı eski referanslar status'u taşımayan bir karakteri gösterecekti — bug çıkardı.

### 3.3 — Süresi dolan FrozenStatus zincirde kalıyor
AI dedi: "FrozenStatus süresi dolunca dağıtılır". Ama bunu yapmak için decorator zincirini yeniden örmek lazım. Şu an süresi dolan FrozenStatus zincirde duruyor ama `_remaining == 0` olduğu için no-op — yani sessiz. Bu trade-off: bellek temizliği vs. kod karmaşıklığı. Pragmatik tercih: no-op olarak bıraktım, Faz 3 cleanup'ında ilgilenirim. AI bu trade-off'u açıkça söylememişti.

---

## 4. Faz 2 Süresince Geçen Süre

- **Tahmini:** ~5-7 saat
- **Gerçek:** ~3 saat (AI ile çift programlama hızlı ilerletti)
- **AI olmadan ne kadar sürerdi?** Çok daha uzun — özellikle Decorator forwarding'i Python'da `__getattr__`/`__setattr__` ile yazmanın detayları AI olmadan saatler kaybettirirdi.

---

## 5. Faz 2 Özeti

**Yeni Dosyalar:**
- `src/game/team.py` — Composite Team sınıfı
- `src/game/effects/status.py` — StatusEffect (Decorator) + Burning/Frozen/Shocked
- `docs/diagrams/phase2-before.puml`, `phase2-after.puml`

**Değiştirilen Dosyalar:**
- `src/game/characters/base.py` — `take_damage`, `tick`, `should_skip_turn`, `apply_effect`, `has_status` eklendi; `frozen_turns` kaldırıldı
- `src/game/engine.py` — `player_team`/`enemy_team` Team oldu, AoE blokları Team API'sine geçti, HP-cap hack silindi

**Çözülen Problemler:**
- #5 — AoE kod tekrarı: Team.take_damage_each tek noktada
- #6 — Status efektleri Character'a sızıyor: Decorator zincirine taşındı
- #7 — HP-cap hack iki yerde: take_damage clamp ile gitti

**Faz 3'e bırakılan:**
- Reaksiyon ve yetenek if-elif zincirleri (Strategy / Chain of Responsibility)
- enemy_decide AI mantığı (Strategy)
- engine.log.append doğrudan çağrıları (Observer)
- CI/CD pipeline

**Yeni Gameplay:**
- Fire→Hydro: 1.5x hasar + 3 tur yanma
- Cryo→Hydro: hasar + 1 tur donma
- Electro→Fire: hasar + sıçrama + Shocked (sonraki hasar +%50)
- Freeze Ray: hasar + 1 tur donma
