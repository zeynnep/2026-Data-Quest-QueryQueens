"""Buyume ayristirmasi (Q5): Region x donem, nufus agirlikli.
Girdi : buyume_ayristirma.csv, wpp2024_ulke_temiz.csv
Cikti : ayristirma.csv
"""
import pandas as pd

AYRISTIRMA = "buyume_ayristirma.csv"
ANA_VERI = "wpp2024_ulke_temiz.csv"

# 1) Verileri oku
ay = pd.read_csv(AYRISTIRMA, encoding="utf-8-sig")
d = pd.read_csv(ANA_VERI, encoding="utf-8-sig")

# 2) <= 2023 filtresi, nufus (TPopulation1July) ekle, donem sutunu
o = ay[ay.Time <= 2023].copy()
o = o.merge(d[["ISO3_code", "Time", "TPopulation1July"]],
            on=["ISO3_code", "Time"], how="left")
o["donem"] = pd.cut(o.Time, [1949, 1974, 1999, 2023],
                    labels=["1950-1974", "1975-1999", "2000-2023"])

# 3) Nufus agirlikli bolge-donem ortalamasi
sutunlar = ["buyume_pct", "dogal_pct", "goc_pct", "kalan_pct"]

def ayristir(df):
    w = df.copy()
    for c in sutunlar:
        w[c + "_w"] = w[c] * w.TPopulation1July
    g = w.groupby(["Region", "donem"], observed=True)[[c + "_w" for c in sutunlar] + ["TPopulation1July"]].sum()
    for c in sutunlar:
        g[c] = g[c + "_w"] / g["TPopulation1July"]
    r = g[sutunlar].copy()
    r["goc_pay"] = r.goc_pct / r.buyume_pct
    r["goc_pay_mutlak"] = r.goc_pct.abs() / (r.dogal_pct.abs() + r.goc_pct.abs())
    return r

# 4) Paylar (dogal, goc, kalan, mutlak goc payi)
def paylar(r):
    r = r.copy()
    r["dogal_pay"] = r.dogal_pct / r.buyume_pct
    r["kalan_pay"] = r.kalan_pct / r.buyume_pct
    return r

# 5) Iki kapsam: tum ulkeler ve kucuk bolgeler haric
tum = ayristir(o)
buyuk = ayristir(o[o.small_territory == 0])

cikti = pd.concat([paylar(tum).assign(kapsam="tum_ulkeler"),
                   paylar(buyuk).assign(kapsam="kucuk_bolgeler_haric")]).reset_index()

cikti = cikti[["kapsam", "Region", "donem", "buyume_pct", "dogal_pct", "goc_pct", "kalan_pct",
               "dogal_pay", "goc_pay", "kalan_pay", "goc_pay_mutlak"]]

# 6) ayristirma.csv olarak kaydet
cikti.to_csv("ayristirma.csv", index=False, encoding="utf-8-sig")
print(cikti.shape)