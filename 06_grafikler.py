"""DataQuest 2026 - Gorev 3 (Serengul): rapor grafikleri.

Girdi (repodaki adlariyla, ayni klasorde):
    endeks.csv                (Dilara)  -> endeks haritasi
    kumeler.csv               (Zeynep)  -> kume yorungeleri
    profil_gozlem_ozet.csv    (01_veri_hazirlik.py uretir) -> kume yorungeleri
    ayristirma.csv            (Dilara)  -> buyume ayristirmasi
Cikti:
    kume_yorungeleri.png, endeks_haritasi.html (+ .png varsa), ayristirma_grafik.png

Calistirma:  python 06_grafikler.py [veri_klasoru]
Girdi dosyalari degistirilmez, yalnizca okunur.
Not: hangi endeks sutunu / hangi kapsam kullanilacagi ekip karariyla netlesecek;
asagidaki ENDEKS_SUTUNU ve KAPSAM degiskenlerinden degistirilir.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")                  # ekransiz ortamda da calissin
import matplotlib.pyplot as plt

KLASOR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

ENDEKS_SUTUNU = "endeks_esit"          # "endeks_esit", "endeks_pca" ya da "endeks_esit_buyuk"
KAPSAM = "tum_ulkeler"                 # "tum_ulkeler" ya da "kucuk_bolgeler_haric"


def oku(ad):
    return pd.read_csv(KLASOR / ad, encoding="utf-8-sig")


# ---------------------------------------------------------------- Grafik 1
def kume_yorungeleri():
    kume = oku("kumeler.csv")
    prof = oku("profil_gozlem_ozet.csv")
    p = prof.merge(kume[["ISO3_code", "kume", "kume_adi"]], on="ISO3_code", how="left")
    assert p.kume.isna().sum() == 0, "kumesi eksik ulke var"

    gostergeler = ["TFR_z", "LEx_z", "MedianAgePop_z", "CDR_z", "CNMR_z"]
    adlar = {"TFR_z": "Doğurganlık (TFR)", "LEx_z": "Yaşam süresi (LEx)",
             "MedianAgePop_z": "Medyan yaş", "CDR_z": "Kaba ölüm hızı (CDR)",
             "CNMR_z": "Net göç hızı (CNMR)"}
    ort = p.groupby(["kume_adi", "Time"])[gostergeler].mean().reset_index()
    n = kume.kume_adi.value_counts()

    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
    for ax, g in zip(axes.ravel(), gostergeler):
        for ad, grp in ort.groupby("kume_adi"):
            ax.plot(grp.Time, grp[g], label=f"{ad} (n={n[ad]})", linewidth=2)
        ax.set_title(adlar[g])
        ax.set_ylabel("z-skor")
        ax.grid(alpha=0.3)
    axes[1, 2].axis("off")
    h, l = axes[0, 0].get_legend_handles_labels()
    axes[1, 2].legend(h, l, loc="center", fontsize=11, title="Küme")
    fig.suptitle("Kümelere göre ortalama gösterge yörüngeleri, 1950–2020", fontsize=14)
    plt.tight_layout()
    fig.savefig(KLASOR / "kume_yorungeleri.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- Grafik 2
def endeks_haritasi():
    try:
        import plotly.express as px
    except ImportError:
        print("plotly yok: endeks haritasi atlandi (pip install plotly)")
        return
    endeks = oku("endeks.csv")
    fig = px.choropleth(
        endeks, locations="ISO3_code", color=ENDEKS_SUTUNU, hover_name="Location",
        color_continuous_scale="Viridis", labels={ENDEKS_SUTUNU: "Profil endeksi"},
        title="Demografik profil endeksi, 2023")
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    fig.write_html(str(KLASOR / "endeks_haritasi.html"))
    try:                                # PNG icin kaleido gerekir
        fig.write_image(str(KLASOR / "endeks_haritasi.png"), scale=2)
    except Exception as e:
        print("PNG yazilamadi (kaleido yok olabilir); HTML yazildi:", type(e).__name__)


# ---------------------------------------------------------------- Grafik 3
def ayristirma_grafigi():
    ay = oku("ayristirma.csv")
    veri = ay[ay.kapsam == KAPSAM]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharey=True)
    for ax, b in zip(axes.ravel(), veri.Region.unique()):
        s = veri[veri.Region == b].set_index("donem")
        # goc cubugu, dogal artisla ayni isaretliyse ustune istiflenir, degilse sifirdan baslar
        alt = s.dogal_pct.where(s.dogal_pct * s.goc_pct > 0, 0)
        ax.bar(s.index, s.dogal_pct, label="Doğal artış", color="#4c78a8")
        ax.bar(s.index, s.goc_pct, bottom=alt, label="Net göç", color="#f58518")
        ax.plot(s.index, s.buyume_pct, "ko", label="Toplam büyüme")
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_title(b, fontsize=11)
        ax.tick_params(axis="x", labelsize=8)
    axes[0, 0].set_ylabel("Yüzde puan")
    axes[1, 0].set_ylabel("Yüzde puan")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=10)
    fig.suptitle("Nüfus büyümesinin ayrıştırması: doğal artış ve net göç katkısı", fontsize=14)
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.savefig(KLASOR / "ayristirma_grafik.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    kume_yorungeleri()
    endeks_haritasi()
    ayristirma_grafigi()
    print("Tamam.")
