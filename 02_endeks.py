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