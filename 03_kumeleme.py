"""DataQuest 2026 - Q4: ulkeleri gostergelerin zaman icindeki ortak hareketine gore kumeleme.
Girdi : profil_gozlem_ozet.csv  (01_veri_hazirlik.py uretir)
Cikti : kumeler.csv, kumeleme_k_secimi.csv, kumeleme_kararlilik.csv
"""
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, adjusted_rand_score

SEED = 42
GIRDI = "profil_gozlem_ozet.csv"
K_ARALIK = range(2, 9)
N_BOOT = 100
CLIP = 3.0      # z-skor winsorization siniri
MIN_BOYUT = 5   # tek ulkelik/cok kucuk kumeleri reddet

df = pd.read_csv(GIRDI)
zcols = [c for c in df.columns if c.endswith("_z")]

# Her ulke = tek satir: (gosterge x yil) yorungesi duzlestirilir
wide = df.pivot_table(index=["ISO3_code", "Location", "Region", "Subregion",
                             "small_territory"], columns="Time", values=zcols)
wide = wide.dropna()
meta = wide.index.to_frame(index=False)
X = np.clip(wide.to_numpy(), -CLIP, CLIP)  # asiri uc degerleri (ornegin Kuwait gocu) sinirla
print("Yorunge matrisi:", X.shape)

# PCA ile gurultuyu azalt (aciklanan varyansin %95'i)
pca = PCA(n_components=0.95, random_state=SEED).fit(X)
Z = pca.transform(X)
print("PCA bilesen sayisi:", Z.shape[1])

# k secimi: silhouette
rows = []
for k in K_ARALIK:
    km = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(Z)
    rows.append({"k": k, "silhouette": silhouette_score(Z, km.labels_),
                 "inertia": km.inertia_, "min_kume_boyutu": int(np.bincount(km.labels_).min())})
ksec = pd.DataFrame(rows)
print(ksec.round(3).to_string(index=False))
K = 3  # silhouette k=2'yi onerir, k=3 yorumlanabilirlik icin secildi
print("Secilen k:", K)

final = KMeans(n_clusters=K, n_init=50, random_state=SEED).fit(Z)
meta["kume"] = final.labels_

# Kararlilik: %80 ulke ornegiyle kumele, tum ulkeleri atayip ARI hesapla
rng = np.random.default_rng(SEED)
ari = []
for _ in range(N_BOOT):
    idx = rng.choice(len(Z), size=int(0.8 * len(Z)), replace=False)
    km = KMeans(n_clusters=K, n_init=10, random_state=int(rng.integers(1e6))).fit(Z[idx])
    ari.append(adjusted_rand_score(final.labels_, km.predict(Z)))
ari = np.array(ari)
print(f"Kararlilik ARI: ort={ari.mean():.3f}, %2.5-%97.5=({np.percentile(ari,2.5):.3f}, {np.percentile(ari,97.5):.3f})")

# Kume profilleri (ortalama yorunge ozeti: 1950 ve 2020 degerleri)
prof = pd.DataFrame(X, columns=wide.columns)
prof["kume"] = final.labels_
for ind in ["TFR_z", "LEx_z", "MedianAgePop_z"]:
    print(ind, "1950/2020 kume ortalamalari:")
    print(prof.groupby("kume")[[(ind, 1950), (ind, 2020)]].mean().round(2).to_string())

meta.to_csv("kumeler.csv", index=False)
ksec.to_csv("kumeleme_k_secimi.csv", index=False)
pd.DataFrame({"ari": ari}).to_csv("kumeleme_kararlilik.csv", index=False)
print(meta.kume.value_counts().sort_index().to_string())
