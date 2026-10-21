"""DataQuest 2026 - Kume ek analizleri (Zeynep).
01_veri_hazirlik.py ve 03_kumeleme.py calistiktan SONRA calistirin.
Girdi : profil_gozlem_ozet.csv, kumeler.csv
Cikti : kumeler.csv (kume_adi eklenir), kume_profilleri.csv, kume_bolge.csv,
        kararlilik_small_territory.csv, q6_tek_gosterge.csv
"""
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score as ari

SEED, CLIP, N_BOOT = 42, 3.0, 100

df = pd.read_csv("profil_gozlem_ozet.csv")
kum = pd.read_csv("kumeler.csv")
zcols = [c for c in df.columns if c.endswith("_z")]
inds = [c[:-2] for c in zcols]
wide = df.pivot_table(index=["ISO3_code", "Location", "Region", "Subregion",
                             "small_territory"], columns="Time", values=zcols).dropna()
iso = wide.index.get_level_values("ISO3_code")
labels = kum.set_index("ISO3_code").loc[iso, "kume"].to_numpy()
K = len(np.unique(labels))
small = wide.index.get_level_values("small_territory").to_numpy() == 1


def embed(cols, mask=None):
    X = np.clip(wide[cols].to_numpy(), -CLIP, CLIP)
    if mask is not None:
        X = X[mask]
    return PCA(n_components=0.95, random_state=SEED).fit_transform(X)


# ---------- 1) Kume adlari (numaraya degil, profile gore) ----------
ym = wide.xs(2020, axis=1, level="Time")["MedianAgePop_z"].groupby(labels).mean()
sirali = ym.sort_values()
ad = {sirali.index[-1]: "Erken gecis", sirali.index[0]: "Gec gecis"}
for k in sirali.index:
    ad.setdefault(k, "Orta donem gecisi")
kum["kume_adi"] = kum["kume"].map(ad)
kum.to_csv("kumeler.csv", index=False)
print("Kume adlari:", {int(k): v for k, v in ad.items()})
print(kum.groupby(["kume", "kume_adi"]).size().to_string())

# ---------- 2) Kume profilleri ----------
rows = []
for k in sorted(ad):
    m = labels == k
    for ind in zcols:
        for yil in (1950, 1990, 2020):
            rows.append({"kume": k, "kume_adi": ad[k], "n_ulke": int(m.sum()),
                         "gosterge": ind[:-2], "yil": yil,
                         "ortalama_z": round(wide[(ind, yil)].to_numpy()[m].mean(), 2)})
pd.DataFrame(rows).to_csv("kume_profilleri.csv", index=False)
reg = pd.crosstab(wide.index.get_level_values("Region"), pd.Series(labels).map(ad).to_numpy())
reg.to_csv("kume_bolge.csv")
print("\nBolge dagilimi:\n", reg.to_string())

# ---------- 3) small_territory duyarliligi ----------
print(f"\nKucuk bolge sayisi: {small.sum()} / {len(small)}")
Zs = embed(zcols, mask=~small)
lab_sub = KMeans(n_clusters=K, n_init=50, random_state=SEED).fit(Zs).labels_
a_small = ari(labels[~small], lab_sub)
ct = pd.crosstab(pd.Series(labels[small]).map(ad), "n_kucuk_bolge")
print(f"Kucuk bolgeler haric kumeleme ile ARI = {a_small:.3f}")
print(ct.to_string())
pd.DataFrame([{"n_kucuk_bolge": int(small.sum()), "ari_kucukler_haric": round(a_small, 3)}]
             ).to_csv("kararlilik_small_territory.csv", index=False)

# ---------- 4) Q6: tek gosterge yeter mi? ----------
Z_full = embed(zcols)
rng = np.random.default_rng(SEED)
out = []
for ind in zcols:
    Z_one = embed([ind])
    lab_one = KMeans(n_clusters=K, n_init=50, random_state=SEED).fit(Z_one).labels_
    a_point = ari(labels, lab_one)
    boots = []
    for _ in range(N_BOOT):
        idx = rng.choice(len(Z_full), size=int(0.8 * len(Z_full)), replace=False)
        s = int(rng.integers(1e6))
        lf = KMeans(n_clusters=K, n_init=10, random_state=s).fit(Z_full[idx]).labels_
        lo = KMeans(n_clusters=K, n_init=10, random_state=s).fit(Z_one[idx]).labels_
        boots.append(ari(lf, lo))
    diger = [c for c in zcols if c != ind]
    lab_loo = KMeans(n_clusters=K, n_init=50, random_state=SEED).fit(embed(diger)).labels_
    out.append({"gosterge": ind[:-2], "ari_tek_gosterge": round(a_point, 2),
                "boot_ort": round(np.mean(boots), 2),
                "boot_alt_2.5": round(np.percentile(boots, 2.5), 2),
                "boot_ust_97.5": round(np.percentile(boots, 97.5), 2),
                "ari_bu_gosterge_haric": round(ari(labels, lab_loo), 2)})
q6 = pd.DataFrame(out)
q6.to_csv("q6_tek_gosterge.csv", index=False)
print("\nQ6: tek gosterge yorungesi ile tam kumelemenin benzerligi (ARI):")
print(q6.to_string(index=False))

snap = wide.xs(2020, axis=1, level="Time")[zcols]
snap = np.clip((snap - snap.mean()) / snap.std(), -CLIP, CLIP)
ev = PCA().fit(snap).explained_variance_ratio_
print("\n2020 kesitinde PCA aciklanan varyans:", np.round(ev, 2))
print("2020 gosterge korelasyonlari:")
print(wide.xs(2020, axis=1, level="Time")[zcols].corr().round(2).to_string())
