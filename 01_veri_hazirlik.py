"""DataQuest 2026 - ortak veri hazirligi (Q3 endeks + Q4 kumeleme + Q5 buyume ayristirmasi).
Girdi : wpp2024_ulke_temiz.csv
Cikti : ulke_yil_panel.csv, profil_gozlem_ozet.csv, buyume_ayristirma.csv
"""
import numpy as np, pandas as pd

GIRDI = "wpp2024_ulke_temiz.csv"
PROFIL = ["TFR", "LEx", "MedianAgePop", "CDR", "CNMR"]
LAST_OBS = 2023  # 2024+ UN projeksiyonu (is_projection=1)

df = pd.read_csv(GIRDI, encoding="utf-8-sig")
assert df.groupby("ISO3_code").size().nunique() == 1, "panel dengeli degil"

# --- Buyume ayristirmasi (Q5): PopGrowthRate(%) ~ (NatChangeRT + CNMR)/10 ---
df["buyume_pct"] = df["PopGrowthRate"]
df["dogal_pct"] = df["NatChangeRT"] / 10
df["goc_pct"] = df["CNMR"] / 10
df["kalan_pct"] = df["buyume_pct"] - df["dogal_pct"] - df["goc_pct"]
print("Kimlik kontrolu |kalan| ortalama / max:",
      df["kalan_pct"].abs().mean().round(4), df["kalan_pct"].abs().max().round(4))

# --- Gozlem donemi, 5 yillik adimlarla profil tablosu (Q3/Q4) ---
obs = df[(df.is_projection == 0) & (df.Time % 5 == 0)].copy()
print("Profil gostergelerinde eksik:", int(obs[PROFIL].isna().sum().sum()))

# gostergeleri yila gore degil, TUM donemde z-skorla (zaman icinde karsilastirilabilir kalsin)
z = (obs[PROFIL] - obs[PROFIL].mean()) / obs[PROFIL].std()
obs_z = pd.concat([obs[["ISO3_code", "Location", "Region", "Subregion", "Time",
                        "small_territory", "extreme_event_flag"]], z.add_suffix("_z")], axis=1)

df.to_csv("ulke_yil_panel.csv", index=False)
obs_z.to_csv("profil_gozlem_ozet.csv", index=False)
df[["ISO3_code", "Location", "Region", "Time", "is_projection", "buyume_pct",
    "dogal_pct", "goc_pct", "kalan_pct", "small_territory", "extreme_event_flag"]
   ].to_csv("buyune_ayristirma.csv".replace("buyune", "buyume"), index=False)
print("Yazildi:", df.shape, obs_z.shape)
