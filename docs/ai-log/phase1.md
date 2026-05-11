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

### Tartışma 1: Registry-based Factory mı, Klasik GoF Factory Method mu?

**AI'a sorduğum:**
> "Karakter yaratımı için Factory Method uygulayacağım — 4 element var. İki yaklaşım düşünüyorum:
> (a) Tek bir CharacterFactory sınıfı + element→Class registry dict'i.
> (b) Soyut CharacterCreator sınıfı + her element için bir concrete Creator alt sınıfı.
> Hangisi daha uygun?"

**AI'ın yanıtı (özet):**
- (a) yaklaşımı (registry-based) daha Pythonic ve daha az boilerplate üretir.
- (b) yaklaşımı klasik GoF kitabına daha sadık ama 4 element için 4 boş Creator sınıfı yazmak overengineering olur.
- Pratikte (a) "Simple Factory" olarak adlandırılır ama OOP literatüründe Factory Method şemsiyesi altında değerlendirilir.

**Benim kararım:**
- (a)'yı seçtim. Sebep: 4 element için 4 ayrı Creator sınıfı yazmak gerçek bir kazanç sağlamıyor — her biri tek satırda `return XCharacter(...)` döndürecekti. Registry tablosu hem OCP uyumlu (yeni element = bir satır) hem de okunabilir.
- Ödevin değerlendirme kriterindeki "doğru örüntü seçimi, uygun bağlam, zorunluluk gerekçesi" maddesi için (a) daha güçlü argümana sahip: gerçek bir sorunu (engine'deki if-elif) çözüyor, sırf "GoF kitabında öyle yazıyor" diye sınıf üretmemiş oluyoruz.

---

### Tartışma 2: Builder Karakter Sınıfını Doğrudan mı Yaratmalı, Factory'ye mi Delege Etmeli?

**AI'a sorduğum:**
> "CharacterBuilder.build() metodunda iki seçeneğim var:
> (a) Builder doğrudan FireCharacter/CryoCharacter vb. instantiate eder.
> (b) Builder, CharacterFactory.create()'a delege eder.
> Hangisi daha temiz?"

**AI'ın yanıtı (özet):**
- (b) daha iyi: tek bir yaratım noktası (CharacterFactory), Builder sadece konfigürasyon toplar.
- (a)'da Builder'ın element string'i tekrar parse etmesi gerekirdi — Factory'nin yaptığı işi tekrar.
- (b)'de Factory registry'ye yeni element eklendiğinde Builder otomatik destekler.

**Benim kararım:**
- (b)'yi seçtim. Bu, "her örüntü kendi sorumluluğunda kalsın" prensibine uygun: Builder = konfigürasyon, Factory = instantiation.
- Test edilebilirlik açısından da kolay: Factory'yi izole test edebilirim, Builder'ın testi de Factory'yi mock edebilir.

---

### Tartışma 3: AI'ın Yanılttığı / Eksik Önerdiği Bir Şey Var Mı?

> *(Buraya AI'a Faz 1 kodunu gösterip review yaptırınca aldığın yanıtla ne kadar hemfikir olduğunu yaz. Özellikle AI'ın yanıldığı, yanlış yorumladığı veya gözden kaçırdığı bir nokta varsa kritik şekilde belirt — ödev refleksiyon puanı bu kısma bakar.)*

**Buraya örnek bir refleksiyon yapısı (kendi yaşadığına göre değiştir):**
- "AI 'Factory'yi static method yapma, Dependency Injection için instance method yap' önerdi. Ama bu projede DI ihtiyacımız yok — Factory tek bir global registry'yi yönetiyor. AI genel bir prensibi (testability) somut bağlamdan koparmıştı; ben classmethod ile kaldım."
- "AI 'Builder'a `reset()` metodu ekle ki aynı builder objesini tekrar kullanasın' dedi — ama bu kullanım senaryomda yok (her karakter için yeni builder yaratıyorum); gereksiz API yüzeyi olacaktı, eklemedim."
- *(Gerçek tartışmandan örnekler ekle)*

---

## 3. Faz 1 Süresince Geçen Süre

- **Tahmini:** ~6 saat (plan dosyasında)
- **Gerçek:** *(burayı doldur)*
- **AI olmadan ne kadar sürerdi?** *(spekülatif tahmin)*

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

**Çözülen PROBLEMS.md Maddeleri:**
- #2 (element type-check zincirleri) — engine.create_character'daki if-elif gitti
- #3 (yaratım sabit kodlanmış) — Builder ile esnek kurulum

**Henüz Çözülmemiş:**
- Engine'in attack ve use_ability metodlarındaki if-elif'ler **bilinçli olarak** Faz 1'de dokunulmadı; Faz 3'te Strategy + Chain of Responsibility ile çözülecek.
