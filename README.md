# DataQuest 2026 – Query Queens

ASA DataQuest 2026 yarışması için BM Dünya Nüfus Beklentileri 2024 (WPP2024) verisi üzerine ekip projesi. *(UN WPP2024 demographic indicators: country trajectories, a profile index and cluster analysis.)*

**Ekip:** Zeynep Atik, Dilara Sönmez, Serengül Kara

## Ana soru

*Bir ülkenin demografik hikâyesini tek bir gösterge anlatır mı?*

Kısa cevap: Hayır. Ülkeler 1950–2020 yörüngelerine göre üç gruba ayrılıyor, ama hiçbir tek gösterge (ya da tek bir endeks) bu grupları tam yakalamıyor. Göç ise bu ayrışmadan bağımsız, ayrı bir boyut.

## Önemli bulgular

| Konu | Sonuç |
|---|---|
| Veri | 237 ülke × 1950–2100. 84.360 satırın 48.336'sı ülke olmayan gruplama, 237'si 2101 yılı, geriye 35.787 satır |
| Kümeleme | 5 gösterge (TFR, LEx, MedianAgePop, CDR, CNMR), 1950–2020, k=3: **Erken geçiş** (84 ülke), **Orta dönem geçişi** (97), **Geç geçiş** (56) |
| Kararlılık | %80'lik alt örneklerle ARI ortalaması 0,94. Küçük bölgeler çıkarılınca ARI 0,98 |
| Tek gösterge yeter mi? | Tek göstergeyle yakalanan oran en iyi durumda ARI 0,68 (LEx), TFR 0,67. CNMR kümeleri etkilemiyor (ARI ≈ 0) |
| Endeks | Kümeler arası varyans payı η² = 0,76. Endeksle tek boyutlu kümeleme ile ARI 0,54 |
| Büyüme | Erken geçiş kümesinde 2000–2023'te doğal artış 0,16, göç katkısı 0,26 (yüzde puan/yıl). Geç geçiş kümesinde büyüme neredeyse tamamen doğal artıştan |

Küme adları gelişmişlik düzeyini değil, demografik geçişin **zamanlamasını** anlatır.

## Çalıştırma

1. Repoyu klonlayın ve gereksinimleri kurun:
   ```
   pip install -r requirements.txt
   ```
2. Ham veri GitHub'da yoktur. `wpp2024_ulke_temiz.csv` dosyasını ortak Drive klasöründen indirip bu klasöre koyun.
3. Scriptleri sırayla çalıştırın:

| Sıra | Script | Ne yapar | Ana çıktılar |
|---|---|---|---|
| 1 | `01_veri_hazirlik.py` | Ülke × yıl paneli, profil tablosu, büyüme ayrıştırması | `profil_gozlem_ozet.csv`, `buyume_ayristirma.csv` |
| 2 | `02_endeks.py` | Profil endeksi (LEx, TFR, MedianAgePop; eşit ağırlık ve PCA) | `endeks.csv` |
| 3 | `03_kumeleme.py` | Yörünge kümeleme, k seçimi, kararlılık | `kumeler.csv`, `kumeleme_k_secimi.csv`, `kumeleme_kararlilik.csv` |
| 4 | `04_kume_ek_analizler.py` | Küme adları, küme profilleri, küçük bölge duyarlılığı, tek gösterge testi (Q6) | `kume_profilleri.csv`, `kume_bolge.csv`, `kararlilik_small_territory.csv`, `q6_tek_gosterge.csv` |
| 5 | `05_ayristirma.py` | Bölge × dönem büyüme ayrıştırması | `ayristirma.csv` |
| 6 | `06_bootstrap.py` | Endeks duyarlılığı, bölgeler arası göç payı farkı | `endeks_duyarlilik.csv`, `goc_payi_bootstrap.csv` |
| 7 | `07_grafikler.py` | Rapor grafikleri | `endeks_haritasi.png`, `kume_yorungeleri.png`, `ayristirma_grafik.png` |
| 8 | `08_kume_baglantilari.py` | Kümelerde büyüme ayrıştırması ve endeks bağlantısı | `kume_buyume_ayristirma.csv`, `kume_endeks.csv` |

Tüm rastgelelik `random_state=42` ile sabitlenmiştir.

## Yöntem özeti

- **Veri:** WPP2024 Medium dosyası. Ülkeler `ISO3_code` ile toplamalardan ayrıldı, 2101 yılı atıldı. Ayrıntılar için `Temiz Veri Dosyası Veri Kalitesi Notu (Görev 1).pdf`.
- **Gözlem ve projeksiyon:** Analizler gözlem dönemini (≤2023, `is_projection == 0`) kullanır. Projeksiyon yıllarında çıkarsama yapılmamıştır. İsteğe bağlı OtherVariants dosyası kullanılmamıştır.
- **Kümeleme:** Her ülke 5 göstergenin 1950–2020 (5 yıllık adımlar) z-skor yörüngesiyle temsil edildi. Aşırı değerler (ör. Kuveyt göçü) için z-skorlar ±3'te sınırlandı, PCA (%95 varyans) ve KMeans uygulandı. Silhouette k=2'yi önerir, yorumlanabilirlik için k=3 seçildi.
- **Göstergeler:** Birbirini tekrar eden göstergeler (IMR, CBR) ve büyüme oranı (doğal artış ile göçün toplamı) kümelemeden çıkarıldı.
- **Çıkarsama:** Alt örnekleme ve ülke bazlı bootstrap aralıkları. Bu aralıklar örnekleme kararlılığını gösterir, bağımsız hipotez testi değildir.

## Sınırlılıklar ve etik notlar

- Göç oranları BM modelinin tahminidir, kesin ölçüm değildir. Göç, "yük" ya da "çözüm" olarak yorumlanmaz.
- Küme adları ülkeleri değer yargısıyla etiketlemez. Kümelerin içinde çeşitlilik vardır, ülke ortalamaları ülke içi farkları gizler.
- Ortalamalar ülkeleri eşit ağırlıkla sayar, nüfusa göre ağırlıklandırılmamıştır. Küçük bölgeler gürültülüdür (`small_territory`).
- Endeks 2023 anlık görüntüsüdür, kümeler 1950–2020 yörüngeleridir. İkisi aynı şeyi ölçmez.
- Ayrıntılı etik notlar için `etik_notlar.md`.

## Dosya rehberi

- `*.py`: analiz scriptleri (yukarıdaki sıra)
- `kumeler.csv`: ülke → küme (`kume`, `kume_adi`)
- `endeks.csv`: ülke başına endeks (`endeks_esit`, `endeks_pca`)
- `buyume_ayristirma.csv`: ülke-yıl büyüme = doğal artış + göç + kalan
- `betimsel_tablo_*.csv`: bölge ve alt bölge betimsel tabloları
- `*.png`: grafikler
- `etik_notlar.md`: etik not listesi
