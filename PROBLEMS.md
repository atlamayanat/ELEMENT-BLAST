# PROBLEMS.md — Faz 0 Tasarım Analizi

Bu dosya, `src/game/engine.py`'deki başlangıç kodunda tespit edilen tasarım sorunlarını listeler. Her sorun, ilerleyen fazlarda hangi tasarım örüntüsüyle çözüleceğine bir yol haritası sunar.

**Sistem özeti:** 3v3 sıra tabanlı dövüş, 4 element (Fire/Cryo/Electro/Hydro), 6 reaksiyon kuralı, her karakterin tek özel yeteneği. Tüm bu mantık tek bir `GameEngine` sınıfında.

---

## 1. God Class — `GameEngine` her şeyi yapıyor

`GameEngine` sınıfı tek başına **karakter yaratımı, taban hasar hesabı, 6 farklı elemental reaksiyon kuralı, 4 farklı yeteneğin gövdesi, düşman AI'ı, durum efektleri (frozen), oyun durumu kontrolü, takım render** sorumluluklarını üstleniyor. SRP'nin her satırı ihlal ediliyor. Bir reaksiyon formülünü değiştirmek için aynı dosyada yetenek mantığının ve AI'ın yanından geçmek gerekiyor.

> **Çözüm:** Faz 2 Facade (dış API'yi sadeleştir), Faz 3 Strategy/Observer/CoR (sorumlulukları dağıt).

## 2. Element Type-Check Zincirleri — yeni element 4 yeri değiştirir

`engine.py`'de element bazlı `if-elif` zincirleri **dört farklı yere** yayılmış:
- `create_character` (taban stat ataması)
- `attack` taban hasar bloku (her element için ayrı dal — şu anda hepsi aynı `attack_power` veriyor olsa bile blok olarak duruyor)
- `attack` reaksiyon bloku (saldıran ve hedef element'ine göre 6 dallı zincir)
- `use_ability` (her yetenek farklı element semantiği taşıyor)

Yeni bir element (örn. `geo`) eklemek için bu dört bloğun hepsini güncellemek gerekiyor. OCP açıkça ihlal.

> **Çözüm:** Faz 1 Factory Method + element-aware Character alt sınıfları; Faz 3 Chain of Responsibility ile reaksiyonları handler zincirine taşı.

## 3. Reaksiyon Kuralları Hard-Coded — yeni reaksiyon = engine patch

6 reaksiyon kuralı `attack` metodu içinde **iç içe `elif` bloklarında** gömülü:
```python
if attacker.element == "fire" and target.element == "cryo": damage *= 2
elif attacker.element == "electro" and target.element == "fire": ...
elif attacker.element == "hydro" and target.element == "electro": ...
```
"Cryo + Burning hedefi → buharlaşma" gibi yeni bir reaksiyon eklemek için `attack` metodunun gövdesini patch'lemek şart. Bu blok hem büyüyor hem de tek metodda 80+ satır olmaya başladı bile.

> **Çözüm:** Faz 3 Chain of Responsibility — her reaksiyon bağımsız bir `ReactionHandler` sınıfı, zincir runtime'da kurulur.

## 4. Yetenekler İsme Bağımlı — yeni karakter = motora dokun

`use_ability` metodu karakterin `ability_name` string'ine göre `if-elif` ile dispatch yapıyor:
```python
if character.ability_name == "fire_blast": ...
elif character.ability_name == "freeze_ray": ...
```
Yeni karakter eklemek (yeni yetenek demek) **GameEngine'in içine yeni `elif` yazmak** demek. Karakter ile motor sıkıca kenetlenmiş; karakteri başka bir oyuna taşımak imkansız.

> **Çözüm:** Faz 3 Strategy — her yetenek bir `AbilityStrategy` sınıfı. Karakter yaratılırken yetenek inject edilir; engine sadece `character.ability.execute(ctx)` çağırır.

## 5. AI Davranışı Tek Tip — varyant kavramı yok

`enemy_decide` tüm düşmanlar için aynı: "HP %30'un altına düştüyse %50 ihtimalle yetenek, yoksa saldır." "Saldırgan goblin" / "savunmacı dragon" / "iyileştirici şaman" gibi davranış varyantları yok; eklemek için yeni `if enemy.name == ...` patch'i gerekirdi.

> **Çözüm:** Faz 3 Strategy — `AggressiveAI`, `DefensiveAI`, `HealerAI` strategy'leri runtime'da takılıp çıkarılabilir.

## 6. Durum Efektleri Patlamaya Hazır — `Character`'a alan yığacağız

Şu an `Character.frozen_turns` field'ı var. "Burning her tur 2 hasar", "Wet sonraki Cryo'ya freeze garantisi", "Charged sonraki saldırıyı 2x yapar" gibi durumlar eklemek için Character'a 3 yeni alan, `attack`'a 3 yeni `if`, tur başına `tick_status`'a 3 yeni dal eklemek gerekirdi. Üstelik aynı karakter aynı anda hem Burning hem Wet olabilir; kombinasyonlar `Character`'ı şişirir.

> **Çözüm:** Faz 2 Decorator — `Frozen(char)`, `Burning(char)`, `Wet(Burning(char))` gibi sarma. Character sınıfına dokunmadan yeni status ekleme.

## 7. 3v3 Hedefleme Inline — takım kavramı yok

Engine `self.player_team` ve `self.enemy_team` için iki ayrı liste tutuyor; saldırı/yetenek metodları her seferinde manuel index'leme yapıyor (`opp = self.opponent_team_of(c); living = [x for x in opp if x.hp > 0]`). "Tüm rakip takıma hasarı paylaştır" semantiği `attack`'a hard-coded yazıldı. Takım bir kavram değil, iki listenin teknik adı.

> **Çözüm:** Faz 2 Composite — `Team(Character)`. Team aynı arayüzü sunar (`take_damage`, `is_alive`, `members`); Hydro→Electro paylaşımı, AoE yetenekler hep `team.broadcast(damage)` ile çalışır.

## 8. Test Edilemez — saf fonksiyon yok

Reaksiyon hesabını test etmek istesek `GameEngine` instance'ı kurmak, takımları doldurmak, `attack`'ı çağırıp `target.hp`'yi karşılaştırmak gerekiyor. Saf bir `compute_damage(attacker, target) -> int` fonksiyonu yok; mantık state mutasyonuyla iç içe. Otomatik test pratik olarak imkansız.

> **Çözüm:** Faz 1-3 boyunca davranışlar küçük sınıflara çıktıkça her biri izole test edilebilir hale gelecek; Faz 3 sonu CI'da pytest yeşili.

## 9. UI Motora Gömülü — render = print

`render` metodu `print()` çağırıyor; engine doğrudan terminale bağımlı. pygame UI eklemek istesek motor her yerine `if ui_mode == "pygame":` koşulları serpiştirmek gerekirdi.

> **Çözüm:** Faz 3 Observer — engine olay yayınlar (`DamageDealt`, `ReactionTriggered`, `CharacterFrozen`), konsol logger ve pygame view bunlara abone olur. Motor UI'dan habersiz.

## 10. Yetenek Kullanırken Element Geçici Değişiyor (kod kokusu)

`use_ability` metodunda `fire_blast` yeteneği için karakterin `element` alanı **geçici olarak `"fire"` yapılıyor**, sonra geri alınıyor:
```python
saved_element = character.element
character.element = "fire"
target.hp -= damage   # reaksiyon ister
character.element = saved_element
```
Bu, "yetenek kendi elementiyle reaksiyon tetiklemeli" gereksinimini kötü bir hack ile çözüyor. Yetenek bir `ElementalAttack` kavramı taşımıyor; hasar formülü reaksiyon hesabıyla ayrışmadığı için inline mutasyon yapmak zorunda kalıyoruz.

> **Çözüm:** Faz 3 Strategy + CoR birlikte — yetenek bir `DamageContext(source_element=Fire)` üretir, Chain of Responsibility bunu işler. Karakterin alanını mutasyona uğratmaya gerek kalmaz.

---

## AI Karşılaştırması (Ödev Adımı 4-5)

> **Bu bölüm, AI aracına aynı kodu gösterip "hangi sorunları görüyorsun, hangi tasarım örüntüleri çözer?" diye sorduğumda aldığım yanıtla benim listemi karşılaştırmak için.**

### Kullanılan AI Aracı
- (örn. Claude / ChatGPT / Copilot Chat — ödev sırasında doldurulacak)

### AI'a Sorulan Prompt
> "Bu kodda hangi tasarım sorunlarını görüyorsun? Hangi tasarım örüntüleri bu sorunları çözebilir? Her sorun için kısa bir açıklama yaz."

### AI'ın Tespit Ettiği Sorunlar (özet)
- (AI yanıtı geldiğinde buraya madde madde özetlenecek)

### Örtüşen Sorunlar
- (Hem benim hem AI'ın işaret ettiği sorunlar)

### Sadece Benim Gördüğüm
- (AI'ın atladığı, benim listemdeki sorunlar — ör. madde 10 "geçici element mutasyonu" kod kokusunu AI yakaladı mı?)

### Sadece AI'ın Gördüğü
- (Benim listemde olmayan ama AI'ın haklı olduğu sorunlar)

### Yorum
- (AI ne kadar isabetliydi? Yanılttığı bir nokta var mıydı? Öğrendiğim ne oldu?)
