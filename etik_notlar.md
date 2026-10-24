# Etik not listesi (Dilara)

Kapsam: profil endeksi (Q3), büyüme ayrıştırması (Q5), endeks duyarlılığı ve bölgeler arası göç payı bootstrap'i. Tüm sayılar `wpp2024_ulke_temiz.csv` ve `buyume_ayristirma.csv` üzerinden bu repodaki kodlarla üretilmiştir (`02_endeks.py`, `05_ayristirma.py`, `06_bootstrap.py`). Her maddede üç şey var: nokta nedir, neden önemli, analizde ne yaptık.

## 1. Göç çerçevesi

1. **Net göç, giriş ve çıkışın farkıdır.**
   - Nokta: `CNMR` ve `goc_pct` ülkeye giren ile çıkan kişi sayısının farkını gösterir. Girişlerin ve çıkışların büyüklüğünü ayrı ayrı vermez.
   - Önemi: Girişler ve çıkışlar birbirini dengeliyorsa göç büyük olsa bile net göç sıfıra yakın görünür. "Net göçü küçük, o halde göç az" sonucuna varılamaz.
   - Ne yaptık: Göç payını net göçten hesapladık ve bunu "nüfus değişiminin ne kadarı net göç dengesinden geliyor" olarak yorumladık, "göç hareketinin yoğunluğu" olarak değil.

2. **Göç payı, büyüme küçük ve bileşenler zıt işaretliyken yanıltır.**
   - Nokta: Avrupa 2000–2023'te doğal artış negatif (−0,10 puan), net göç pozitif (+0,20 puan), toplam büyüme yalnızca 0,10 puan. Göçün büyümeye oranı 2,07 çıkar (doğal artışınki −1,07), yani "göç büyümenin %207'si" gibi bir cümle ortaya çıkar.
   - Önemi: Bu cümle göçü gerçekte olduğundan çok daha belirleyici gösterir ve doğal artışın nüfusu azalttığını saklar.
   - Ne yaptık: Bu satırda oranı değil, işaretten bağımsız mutlak göç payını kullandık (|göç| / (|doğal| + |göç|) = 0,66) ve iki bileşenin puan değerlerini birlikte verdik.

3. **Bölge toplamındaki göç, bölge içi hareketleri de içerir.**
   - Nokta: Bir bölgenin net göçü, ülkelerin net göçlerinin toplamıdır. Bölge içindeki hareketler (örneğin bir Avrupa ülkesinden diğerine) bu toplamın içinde yer alır.
   - Önemi: "Avrupa'ya göç" ya da "Avrupa dışına çıkış" gibi ifadeler bu veriyle desteklenmez.
   - Ne yaptık: Sonuçları "ülkelerin net göçlerinin toplamı" olarak adlandırdık.

4. **Uç olaylar sıradan göç gibi okunmamalı.**
   - Nokta: Kuveyt 1990'da büyüme −71 puan, göç katkısı −71 puan; Ruanda 1994'te büyüme −42 puan. Bu satırlarda kalan terim de büyük (Kuveyt −2,85 puan).
   - Önemi: Bu değerler olağanüstü olayları yansıtıyor olabilir. Bunları ortalamaların içine katıp "tipik göç" gibi yorumlamak yanıltıcıdır. Veri nedenlerini söylemez, biz de bir neden iddia etmiyoruz. `extreme_event_flag` Ruanda 1994'ü işaretlerken Kuveyt 1990'ı işaretlememiş, yani bayrak tutarlı bir ölçüt olarak kullanılamaz.
   - Ne yaptık: Bu satırları ayrı olarak raporladık ve nedenlerine dair varsayımda bulunmadık.

5. **Gelecek göç hakkında iddia yok.**
   - Nokta: 2024 ve sonrası UN'nin projeksiyonudur, gözlem değildir.
   - Ne yaptık: Ayrıştırma ve bölgeler arası bootstrap yalnızca 2023 ve öncesi yıllarla yapıldı. Endeks 2023 kesitidir.

## 2. Küçük bölgeler

6. **"Küçük bölge" etiketi yanıltıcı olabilir.**
   - Nokta: `small_territory = 1` olan 76 birim yalnızca dış topraklar değil, Fiji, Samoa, Tonga gibi bağımsız devletleri de kapsar. Etiketin eşik tanımı Serengül'ün veri kalitesi belgesine bağlıdır.
   - Önemi: Bu birimlere "bölge" demek bazı bağımsız ülkelerin statüsünü yanlış gösterir.
   - Ne yaptık: Metinde "küçük nüfuslu ülke/bölge" ifadesini kullanmayı tercih ettik.

7. **Küçük birimler sonuçları aşırı etkiler ve uçlarda yer kaplar.**
   - Nokta: Kalan terimi 0,5 puanı aşan 53 ülke-yıl satırının 51'i küçük birimlerdedir (Holy See tek başına 19). Holy See'nin nüfusu 2023'te yaklaşık 500 kişidir ve endekste birinci sıradadır; endeksin ilk 20'sinin 10'u küçük birimdir (verinin yaklaşık üçte birini oluşturdukları halde).
   - Önemi: Çok küçük bir nüfusta birkaç kişilik değişim yüzde olarak çok büyük görünür. Bu birimlerin endeks sırası yaşam kalitesi hakkında bir şey söylemez.
   - Ne yaptık: Endeksi, ayrıştırmayı ve bootstrap'leri hem tüm birimlerle hem küçük birimler hariç iki sürüm olarak çalıştırdık ve yan yana raporladık.

8. **Etki, yöntem seçimine bağlıdır.**
   - Nokta: Nüfus ağırlıklı ayrıştırmada küçük birimler sonucu neredeyse değiştirmedi (tek istisna Okyanusya: Fiji, Samoa, Tonga gibi birimlerin net çıkışı bölge ortalamasını aşağı çekiyordu; küçükler çıkınca 2000–2023 göç katkısı 0,556'dan 0,680'e yükseldi). Her ülkenin eşit sayıldığı ülke bazlı bootstrap'te ise etki büyüktü: Asya – Latin Amerika farkı −0,100'den +0,024'e döndü ve anlamlılığını yitirdi.
   - Önemi: "Küçük birimler sonucu etkilemiyor" ya da "çok etkiliyor" gibi tek bir cümle doğru olmaz.
   - Ne yaptık: Her sonucun hangi ağırlıkla hesaplandığını açıkça belirttik.

9. **Çok az ülkeli bölgelerde bootstrap güvenilmezdir.**
   - Nokta: Küçük birimler çıkarıldığında Kuzey Amerika'da 2, Okyanusya'da 3 ülke kalır (tüm ülkelerle 5 ve 23).
   - Önemi: İki değerden yapılan yeniden örnekleme yeni bilgi üretmez, aralıklar anlamsızlaşır.
   - Ne yaptık: Bu bölgeler için "küçükler hariç" satırlarını sonuç olarak kullanmadık, değerleri tek tek gösterdik.

## 3. Ülke ortalamaları

10. **Ülke ortalaması, tipik ülkeyi anlatır, tipik insanı değil.**
    - Nokta: Ülke bazlı bootstrap'te her ülke eşit sayılır; çok küçük bir ülke ile çok büyük bir ülke aynı ağırlığı taşır.
    - Önemi: Sonuç "bir bölgede yaşayan insanların durumu" olarak okunursa yanlış olur.
    - Ne yaptık: Ayrıştırmayı nüfusla ağırlıklandırdık (bölgenin gerçek toplam büyümesine karşılık gelir), bootstrap'i ise PDF'in istediği gibi ülke bazında yaptık. İkisinin farklı sorulara cevap verdiğini açıkça yazdık.

11. **Ortalama aykırı değerlere duyarlıdır.**
    - Nokta: Asya'da göç payının ortalaması 0,153, medyanı 0,074'tür. BAE (0,718), Katar (0,656) ve Kuveyt (0,458) gibi birkaç ülke ortalamayı yukarı çeker. Afrika – Asya farkı da bu nedenle kırılgandır (medyanlar 0,073 ve 0,074).
    - Önemi: Bölge ortalamaları, bölgenin tipik ülkesini yansıtmayabilir.
    - Ne yaptık: Ortalama ve medyanı birlikte gösterdik ve Afrika – Asya farkını zayıf kanıt olarak raporladık. Bu ülkelerin neden uçta olduğuna dair veri dışı bir neden öne sürmedik.

12. **Gelir grubu yoktur, bölge bir vekildir.**
    - Nokta: Veri setinde gelir grubu sütunu yok; ayrıştırma `Region` (6 sınıf) düzeyinde yapıldı. Kuzey Amerika yalnızca 5 ülkeden, Okyanusya'nın nüfusu büyük ölçüde Avustralya'dan oluşur.
    - Önemi: Bölge, ülkelerin ekonomik durumunu temsil etmez, bölge içi çeşitlilik gizlenir.
    - Ne yaptık: Karşılaştırmaları "gelir grubu" gibi bir dille yapmadık.

## 4. Küme adları

13. **Küme adları betimleyici olmalı, değer yargısı taşımamalı.**
    - Nokta: Kümeleme, göstergelerin zaman içindeki ortak hareketine göre ülkeleri gruplar. Bir kümeye "gelişmiş", "geri kalmış" ya da "başarılı" gibi bir ad vermek, ölçülmeyen bir yargıyı veriye yükler.
    - Önemi: Küme adı, bir ülkeyi sunumda tek kelimeyle tanımlar ve izleyicide kalıcı bir izlenim bırakır.
    - Ne yaptık / yapılmalı: Adlar yalnızca ölçülen özellikleri anlatmalı (örneğin yaşam beklentisi, doğurganlık, medyan yaş yönünde bir eğilim). Nihai adlar Zeynep'in `kume_profilleri.csv` dosyasıyla birlikte gözden geçirilmelidir.

14. **Endeks adı ve yönü de değer yargısı taşımamalı.**
    - Nokta: Endeks (LEx, TFR, MedianAgePop; 2023) yüksek yaşam beklentisi, düşük doğurganlık ve yüksek medyan yaşta yüksek değer alır. En alttaki 10 ülkenin tamamı Afrika'dandır.
    - Önemi: "Yüksek endeks = iyi" okuması yanlıştır; endeks yalnızca üç özelliğin bir arada bulunduğu demografik bir profili gösterir. Alt sıralardaki bölgeleri "kötü" diye etiketlemek haksız bir çerçeve yaratır.
    - Ne yaptık: Endeksi "Demografik Profil Endeksi" olarak adlandırmayı ve "gelişmişlik" demekten kaçınmayı seçtik. Sıra tablosunu sunarken "en iyi / en kötü" yerine gruplar ya da aralıklar kullanılmalıdır.

## 5. Belirsizlik ve çoklu karşılaştırma

15. **Bootstrap yalnızca örnekleme belirsizliğini ölçer.**
    - Nokta: Bootstrap, "bu ülkeler başka bir ülke kümesi olsaydı sonuç değişir miydi" sorusunu cevaplar. Tüm 237 ülke zaten elimizde ve UN'nin göstergelerdeki tahmin hatası aralıklara yansımaz. Bu hata özellikle eski yıllarda ve çok küçük nüfuslarda büyük olabilir.
    - Önemi: Dar bir aralık "sonuç kesin" anlamına gelmez.
    - Ne yaptık: Aralıkları bu sınırla birlikte raporladık.

16. **Eşit ve PCA ağırlığının aynı çıkması göstergelerin yapısından gelir.**
    - Nokta: Eşit ve PCA ağırlıklı endeks arasındaki sıra korelasyonu 0,99998'dir (%95 aralık: 0,99986–1,00000), çünkü üç gösterge birbirine çok yakındır (r = 0,80–0,85; PC1 varyansın %88,3'ünü açıklar).
    - Önemi: Bu, "ağırlık hiç önemli değil" demek değil. Başka göstergelerle sıralama daha duyarlı olabilir.
    - Ne yaptık: Bunu yöntemin değil, gösterge setinin sonucu olarak yorumladık.

17. **15 bölge çifti birden sınandı.**
    - Nokta: Her çiftte %5 yanılma payı bırakmak, gerçek fark olmasa bile bazı çiftlerin "anlamlı" çıkmasına yol açabilir.
    - Önemi: Düzeltilmemiş sonuçlar fazla iddialı olur.
    - Ne yaptık: Bonferroni düzeltmeli aralıklar da hesaplandı. Düzeltme sonrası 6 fark ayakta kaldı; yalnızca düzeltmesiz anlamlı olanlar (örneğin Afrika – Asya) zayıf kanıt olarak anıldı.
