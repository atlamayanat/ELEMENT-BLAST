# Faz 1 — AI Etkileşim Kaydı

> Bu dosya Faz 1 (Creational örüntüler) sırasında AI ile yapılan tartışmaları belgeler.
> Format: AI'a sorulan prompt, AI'ın yanıtı, benim kararım ve gerekçesi.
> **Bu dosyadaki içerik öğrencinin kendi kelimeleriyle yazılmalı — AI çıktısı birebir kopyalanmaz.**

---

## 1. Hangi Creational Örüntülerini Seçtim ve Neden?

**Karar:** Factory Method + Builder.

**Gerekçem:**
- PROBLEMS.md'de **madde 2** (element type-check zincirleri) ve **madde 3** (yaratım sabit kodlanmış) bu fazın asıl hedef sorunlarıydı. İlki polimorfizm + dispatch, ikincisi de esnek kurulum çağırıyordu.
- Factory Method, "yeni element eklemek = engine'i değiştirmek" döngüsünü kırıyor; en doğal eşleşme buydu.
- Builder ise 3v3 takım kurulumunu okunabilir kılmak için ekledim — 6 farklı `engine.create_character(...)` satırı yerine veri (roster) + uniform inşa döngüsü daha temiz.
- Singleton veya Prototype değerlendirildi ama bu projede gerçek bir ihtiyaç görmedim — Singleton GameEngine için zorlama olur, Prototype ise karakter clone'lamak için makul ama bu sistemde clone gereksiniyo yok.

---

## 2. AI ile Yapılan Tartışmalar

### Tartışma 1: Karakter oluşturma sistemi

**AI'a sorduğum:**
Karakter oluşturma sistemi oyun başladığında defoult olarak 6 karakter oluşturup bunları 2 takıma ekliyor bu bunun yerine defoult karaketler oyun başladığı anda oluşturulsa ve oyuncular takımları kendi kursa daha mantıklı olur. Tabi bunun için daha cok karakter ekleyeceğim

**AI'ın yanıtı (özet):**
"Quick start" → default takımlar otomatik
"Custom draft" → oyuncu havuzdan seçer, Builder her seçimde aynı arayüzle çalışır

Karakter havuzu  — Bir liste : 8-10 hazır karakter şablonu (isim, element, yetenek üçlüleri). Yeni bir pattern değil, sadece data.
Takım kurma akışı (draft phase) — main.py'da yeni bir prompt fonksiyonu: oyuncuya havuzdan karakter seçtirir, seçilenleri Builder'la inşa eder. Bu UI mantığı, pattern değil.
Setup fonksiyonu — Mevcut setup_default_battle ya kaldırılır ya da "default" modu olarak korunur.

**Benim kararım:**
Hazır takım sistemini kaldıralım sadece ozel takım oluşturma sistemi olsun. Boylece sadece seçilen karakterler build edilerek iş yükü azaltılır.
bunu faz 1 de uygulamak dogru bir karar olmalı

---

### Tartışma 2: Builder karakteri kendisi mi oluştursun, yoksa Factory'ye mi yaptırsın?

**AI'a sorduğum:**
> Sence builder Sınıfları direk kendi mi oluştursun yoksa builder bilgileri alıp Factroy e oluşturması ıcın gondersin mi?? 

**AI'ın yanıtı (özet):**
- Factoru mantığı daha mantıklı. Karakter oluşturma işi tek bir yerde — Factory'de — kalsın. Builder sadece kullanıcının seçtiği isim/element/yetenek bilgilerini toplar.
- diğerini yı seçersem Builder'ın element ismine bakıp hangi sınıfı çağıracağını kendisi seçmesi gerekirdi. Bu, Factory'nin zaten yaptığı işi tekrar yapmak demek.


**Benim kararım:**
Factroyde tum build işini birleştirmek iş yükünü azaltacagı ıcın bu mantıgı seçtim 

---

### Tartışma 3: Karakterlerim ÖLEMİYOR

> oyunu test ettiğimde karakterlerin ölmesi gereken yerede
  File "c:\Users\mehme\Desktop\Yazılım_tasarım-Oruntuleri\run.py", line 5, in <module>
    main()
    ~~~~^^
  File "c:\Users\mehme\Desktop\Yazılım_tasarım-Oruntuleri\src\game\main.py", line 205, in main
    player_phase(engine)
    ~~~~~~~~~~~~^^^^^^^^
  File "c:\Users\mehme\Desktop\Yazılım_tasarım-Oruntuleri\src\game\main.py", line 164, in player_phase
    player_turn(engine, c)
    ~~~~~~~~~~~^^^^^^^^^^^
  File "c:\Users\mehme\Desktop\Yazılım_tasarım-Oruntuleri\src\game\main.py", line 150, in player_turn
    engine.player_action(character, "ability", target_idx)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\mehme\Desktop\Yazılım_tasarım-Oruntuleri\src\game\engine.py", line 242, in player_action
    self.use_ability(character, target_index)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\mehme\Desktop\Yazılım_tasarım-Oruntuleri\src\game\engine.py", line 132, in use_ability
    character.element = "fire"
    ^^^^^^^^^^^^^^^^^
AttributeError: property 'element' of 'FireCharacter' object has no setter

bu hataları aldım 1

 - element'i @property yapınca PROBLEMS.md madde 10'da bahsi geçen fire_blast element mutasyonu hack'i kazara kırıldı. Çözüm: element'i alt sınıfın default_element() classmethod'undan inşa edip mutable attribute olarak tuttum. Polimorfizm korundu, hack hala çalışıyor

- Bu sorun normalde faz 3 de otomatik olarak çöülecek bir sorun ama simdi bu yapay yontemle çözerek kodun her fazda çalışır olması sağlandı



---

## 3. Faz 1 Süresince Geçen Süre

- **Tahmini:** ~6 saat (plan dosyasında)
- **Gerçek:** *3 saat
- **AI olmadan ne kadar sürerdi?** ÇOK

---

## 4. Faz 1 Özeti

**Yeni Dosyalar:**
- `src/game/characters/base.py` — Soyut Character ABC
- `src/game/characters/fire.py`, `cryo.py`, `electro.py`, `hydro.py` — 4 concrete element sınıfı
- `src/game/characters/factory.py` — Registry-based Factory
- `src/game/characters/builder.py` — Fluent Builder
- `src/game/characters/__init__.py` — Public API

**Değiştirilen Dosyalar:**
- `src/game/engine.py` — `Character` sınıfı kaldırıldı, `create_character` factory'ye delege ediyor, `add()` metodu eklendi
- `src/game/main.py` — `setup_default_battle` Builder ile veri-odaklı

**Çözülen problemler*
- #1  - Class mantıgı eklendi 
- #2  — engine.create_character'daki if-elif gitti
- #3  — Builder ile esnek kurulum
- #4  - ÖLEMEME sorunu düzeldi

**Henüz Çözülmemiş:**
- Engine'in attack ve use_ability metodlarındaki if-elif'ler **bilinçli olarak** Faz 1'de dokunulmadı; Faz 3'te Strategy + Chain of Responsibility ile çözülecek.


