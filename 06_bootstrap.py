"""Bootstrap analizleri (Gun 4):
  (a) Endeks duyarliligi: esit vs PCA agirlikli endeks siralarinin Spearman korelasyonu (ulke bootstrap)
  (b) Bolgeler arasi goc payi farki: ulke bazli bootstrap, yalnizca <= 2023, Bonferroni duzeltmeli
Girdi : wpp2024_ulke_temiz.csv, buyume_ayristirma.csv
Cikti : endeks_duyarlilik.csv, goc_payi_bootstrap.csv
"""
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

ANA_VERI = "wpp2024_ulke_temiz.csv"
AYRISTIRMA = "buyume_ayristirma.csv"
B = 2000
TOHUM = 2026

d = pd.read_csv(ANA_VERI, encoding="utf-8-sig")
ay = pd.read_csv(AYRISTIRMA, encoding="utf-8-sig")

# ---------------------------------------------------------------- (a) endeks duyarliligi
gost = ["LEx", "TFR", "MedianAgePop"]
y = d[d.Time == 2023].copy()


def spearman_esit_pca(df):
    z = (df[gost] - df[gost].mean()) / df[gost].std()
    z["TFR"] = -1 * z["TFR"]
    esit = z.mean(axis=1)
    w = PCA(n_components=1).fit(z).components_[0]
    w = w / w.sum()
    pca = z.values @ w
    return pd.Series(esit.values).corr(pd.Series(pca), method="spearman")


def bootstrap_aralik(df, B=B, tohum=TOHUM):
    rng = np.random.default_rng(tohum)
    boot = np.array([
        spearman_esit_pca(df.sample(n=len(df), replace=True,
                                    random_state=int(rng.integers(1_000_000_000))))
        for _ in range(B)
    ])
    alt, ust = np.percentile(boot, [2.5, 97.5])
    return dict(n=len(df), gozlenen=spearman_esit_pca(df), alt95=alt, ust95=ust, en_kucuk=boot.min())


satir = []
for ad, df in [("tum_ulkeler", y), ("kucuk_bolgeler_haric", y[y.small_territory == 0])]:
    satir.append(dict(kapsam=ad, **bootstrap_aralik(df)))
duyarlilik = pd.DataFrame(satir)
duyarlilik.to_csv("endeks_duyarlilik.csv", index=False, encoding="utf-8-sig")
print(duyarlilik.round(6).to_string())

# ---------------------------------------------------------------- (b) bolgeler arasi goc payi
o = ay[ay.Time <= 2023]          # yalnizca gozlem/tahmin donemi (2024+ projeksiyon)
ulke = (o.groupby(["Location", "Region", "small_territory"])[["dogal_pct", "goc_pct"]]
          .mean().reset_index())
ulke["goc_pay_mutlak"] = ulke.goc_pct.abs() / (ulke.dogal_pct.abs() + ulke.goc_pct.abs())


def bolge_farklari(u, B=B, tohum=TOHUM):
    rng = np.random.default_rng(tohum)
    v = {r: g.goc_pay_mutlak.values for r, g in u.groupby("Region")}
    satirlar = []
    for a, b in combinations(sorted(v), 2):
        fark = np.array([rng.choice(v[a], len(v[a])).mean() - rng.choice(v[b], len(v[b])).mean()
                         for _ in range(B)])
        alt, ust = np.percentile(fark, [2.5, 97.5])
        alt_b, ust_b = np.percentile(fark, [0.167, 99.833])    # 15 cift icin Bonferroni (0.05/15)
        satirlar.append(dict(bolgeA=a, bolgeB=b, nA=len(v[a]), nB=len(v[b]),
                             fark=v[a].mean() - v[b].mean(), alt95=alt, ust95=ust,
                             alt_bonf=alt_b, ust_bonf=ust_b,
                             sifir_disinda=(alt > 0) or (ust < 0),
                             bonf_sifir_disinda=(alt_b > 0) or (ust_b < 0)))
    return pd.DataFrame(satirlar)


tum_f = bolge_farklari(ulke).assign(kapsam="tum_ulkeler")
buyuk_f = bolge_farklari(ulke[ulke.small_territory == 0]).assign(kapsam="kucuk_bolgeler_haric")
goc = pd.concat([tum_f, buyuk_f], ignore_index=True)
goc = goc[["kapsam", "bolgeA", "bolgeB", "nA", "nB", "fark", "alt95", "ust95",
           "alt_bonf", "ust_bonf", "sifir_disinda", "bonf_sifir_disinda"]]
goc.to_csv("goc_payi_bootstrap.csv", index=False, encoding="utf-8-sig")
print(goc.shape)