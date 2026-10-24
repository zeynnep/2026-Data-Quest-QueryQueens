"""DataQuest 2026 - Kumeleri endeks ve buyume ayristirmasiyla baglama (Zeynep).
Girdi : kumeler.csv, buyume_ayristirma.csv, endeks.csv (Dilara)
Cikti : kume_buyume_ayristirma.csv, kume_endeks.csv
"""
import os
import numpy as np, pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score as ari

SEED, N_BOOT = 42, 1000
rng = np.random.default_rng(SEED)
kum = pd.read_csv("kumeler.csv")
K = kum["kume"].nunique()

# ---------- A) Her kumede buyume: dogal artis mi, goc mu? ----------
b = pd.read_csv("buyume_ayristirma.csv")
b = b[b["is_projection"] == 0].merge(kum[["ISO3_code", "kume_adi"]], on="ISO3_code")
b["donem"] = pd.cut(b["Time"], bins=[1949, 1974, 1999, 2023],
                    labels=["1950-1974", "1975-1999", "2000-2023"])
# once ulke-donem ortalamasi (her ulke esit agirlikli), sonra ulkeler uzerinden bootstrap
ulke = (b.groupby(["kume_adi", "donem", "ISO3_code"], observed=True)
          [["buyume_pct", "dogal_pct", "goc_pct"]].mean().reset_index())
rows = []
for (ad, dn), g in ulke.groupby(["kume_adi", "donem"], observed=True):
    r = {"kume_adi": ad, "donem": dn, "n_ulke": len(g)}
    for col in ["buyume_pct", "dogal_pct", "goc_pct"]:
        v = g[col].to_numpy()
        bs = np.array([v[rng.integers(0, len(v), len(v))].mean() for _ in range(N_BOOT)])
        r[f"{col}_ort"] = round(v.mean(), 3)
        r[f"{col}_medyan"] = round(float(np.median(v)), 3)
        r[f"{col}_alt"] = round(np.percentile(bs, 2.5), 3)
        r[f"{col}_ust"] = round(np.percentile(bs, 97.5), 3)
    rows.append(r)
kb = pd.DataFrame(rows)
kb.to_csv("kume_buyume_ayristirma.csv", index=False)
print("A) Kume x donem: ortalama buyume, dogal artis, goc (yuzde puan / yil)")
print(kb[["kume_adi", "donem", "n_ulke", "buyume_pct_ort", "dogal_pct_ort",
          "goc_pct_ort", "goc_pct_alt", "goc_pct_ust"]].to_string(index=False))

# ---------- B) Endeks kumeleri ayiriyor mu? ----------
if not os.path.exists("endeks.csv"):
    print("\nB) endeks.csv bulunamadi, bu bolum atlandi (git pull yapin).")
else:
    e = pd.read_csv("endeks.csv")
    adaylar = [c for c in e.columns if "endeks" in c.lower() or "index" in c.lower()]
    sayisal = [c for c in e.select_dtypes("number").columns]
    kol = adaylar[0] if adaylar else (sayisal[-1] if sayisal else None)
    isoc = next((c for c in e.columns if c.lower() in ("iso3_code", "iso3")), None)
    if kol is None or isoc is None:
        print("\nB) endeks.csv sutunlari taninamadi:", e.columns.tolist())
    else:
        m = kum.merge(e[[isoc, kol]].rename(columns={isoc: "ISO3_code", kol: "endeks"}),
                      on="ISO3_code").dropna(subset=["endeks"])
        print(f"\nB) Kullanilan endeks sutunu: '{kol}', eslesen ulke: {len(m)}/{len(kum)}")
        ozet = m.groupby("kume_adi")["endeks"].agg(["count", "mean", "std", "min", "max"]).round(2)
        ozet.to_csv("kume_endeks.csv")
        print(ozet.to_string())
        gruplar = [g["endeks"].to_numpy() for _, g in m.groupby("kume_adi")]
        H, p = stats.kruskal(*gruplar)
        ss_tot = ((m["endeks"] - m["endeks"].mean()) ** 2).sum()
        ss_btw = sum(len(g) * (g.mean() - m["endeks"].mean()) ** 2 for g in gruplar)
        lab1d = KMeans(n_clusters=K, n_init=50, random_state=SEED).fit(m[["endeks"]]).labels_
        print(f"Kruskal-Wallis H={H:.1f}, p={p:.2g}; kumeler arasi varyans payi (eta^2)={ss_btw/ss_tot:.2f}")
        print(f"Endeksle tek boyutlu kumeleme ile ARI = {ari(m['kume'], lab1d):.2f}")
