"""Profil endeksi (Q3): LEx, TFR, MedianAgePop, 2023.
Girdi : wpp2024_ulke_temiz.csv
Cikti : endeks.csv
"""
import pandas as pd
from sklearn.decomposition import PCA

GIRDI = "wpp2024_ulke_temiz.csv"
d = pd.read_csv(GIRDI, encoding="utf-8-sig")

# 1) 2023 filtresi ve gosterge secimi
# 2) Z-skor ve TFR isareti
# 3) Esit agirlikli endeks
# 4) Kucuk bolgesiz endeks
# 5) PCA agirliklari, PCA endeksi ve siralar
# 6) endeks.csv olarak kaydet

# 1) 2023 filtresi ve gosterge secimi
gost = ["LEx", "TFR", "MedianAgePop"]
y = d[d.Time == 2023].copy()

# 2) Z-skor ve TFR isareti
z = (y[gost] - y[gost].mean()) / y[gost].std()
z["TFR"] = -1 * z["TFR"]

# 3) Esit agirlikli endeks
endeks = y[["ISO3_code", "Location", "Region"]].copy()
endeks["endeks_esit"] = z.mean(axis=1)

# 4) Kucuk bolgesiz endeks
buyuk = y["small_territory"] == 0
z2 = (y.loc[buyuk, gost] - y.loc[buyuk, gost].mean()) / y.loc[buyuk, gost].std()
z2["TFR"] = -1 * z2["TFR"]
endeks.loc[buyuk, "endeks_esit_buyuk"] = z2.mean(axis=1)

# 5) PCA agirliklari, PCA endeksi ve siralar
pca = PCA(n_components=3).fit(z)
w = pca.components_[0] / pca.components_[0].sum()
endeks["endeks_pca"] = z.values @ w
endeks["sira_esit"] = endeks.endeks_esit.rank(ascending=False)
endeks["sira_pca"] = endeks.endeks_pca.rank(ascending=False)
endeks["sira_farki"] = (endeks.sira_esit - endeks.sira_pca).abs()

# 6) endeks.csv olarak kaydet
cikti = endeks.copy()
cikti["small_territory"] = y["small_territory"]
cikti["Subregion"] = y["Subregion"]
cikti[gost] = y[gost]
cikti = cikti.sort_values("sira_esit")
cikti.to_csv("endeks.csv", index=False, encoding="utf-8-sig")
print(cikti.shape)