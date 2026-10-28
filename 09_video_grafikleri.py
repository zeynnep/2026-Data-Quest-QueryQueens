"""DataQuest 2026 - Video icin 5 grafik (1920x1080, 16:9).
Kullanim:  python 09_video_grafikleri.py        -> Turkce
           python 09_video_grafikleri.py en     -> Ingilizce (dosya adina _en eklenir)
Girdi : kumeler.csv, buyume_ayristirma.csv, kume_buyume_ayristirma.csv,
        q6_tek_gosterge.csv, endeks.csv
Cikti : video_01_veri.png ... video_05_endeks.png
Dunya haritasi icin Natural Earth 110m verisi ilk calistirmada indirilir (internet gerekir).
"""
import sys, os, json, urllib.request
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib.patches import Polygon, Patch
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score as ari

LANG = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("tr", "en") else "tr"
SUF = "" if LANG == "tr" else "_en"
GEO_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
           "geojson/ne_110m_admin_0_countries.geojson")
GEO_FILE = "ne_110m_admin_0_countries.geojson"

# Kume renkleri (renk koru dostu, Okabe-Ito) - TUM grafiklerde sabit
KEYS = ["Erken gecis", "Orta donem gecisi", "Gec gecis"]
COL = {"Erken gecis": "#0072B2", "Orta donem gecisi": "#E69F00", "Gec gecis": "#CC79A7"}
GRAY, DARK = "#E3E3E3", "#222222"

T = {
 "tr": {
  "clusters": {"Erken gecis": "Erken geçiş", "Orta donem gecisi": "Orta dönem geçişi", "Gec gecis": "Geç geçiş"},
  "src": "Kaynak: BM WPP2024 (Medium). Gözlem dönemi ≤ 2023.",
  "t1": "Temizlik sonrası: 237 ülke × 151 yıl", "raw": "Ham veri (tüm satırlar)",
  "ctry": "Yalnızca ülke satırları", "clean": "Temiz veri",
  "rm1": "− {n} satır: bölge, gelir grubu vb. toplamalar", "rm2": "− {n} satır: 2101 yılı",
  "rows": "satır", "est": "Gözlem / tahmin (analiz bu dönemde)", "proj": "BM projeksiyonu (analizde yok)",
  "t2": "Ülkeler demografik geçişin zamanlamasına göre üç gruba ayrılıyor",
  "nocov": "Gri: veri yok ya da haritada gösterilemeyen küçük ülke/bölge", "ctr": "ülke",
  "t3": "Erken geçiş kümesinde büyümenin kaynağı doğal artıştan göçe kayıyor",
  "nat": "Doğal artış", "mig": "Net göç katkısı", "yl": "Yüzde puan / yıl (ortalama, %95 aralık)",
  "t4": "Hiçbir tek gösterge kümeleri tam yakalamıyor",
  "ind": {"TFR": "Doğurganlık (TFR)", "LEx": "Yaşam süresi (LEx)", "MedianAgePop": "Medyan yaş",
          "CDR": "Ölüm hızı (CDR)", "CNMR": "Net göç (CNMR)"},
  "endx": "Endeks (3 gösterge, 2023)", "x4": "Kümelerle benzerlik (ARI, 1 = birebir)", "perfect": "birebir",
  "t5": "Endeks ülkeleri sıralıyor ama kümelerin sınırlarını çizmiyor", "x5": "Profil endeksi (yüksek: uzun yaşam, düşük doğurganlık, yaşlı nüfus)", "note4": "Endeks 2023 anlık görüntüsüdür; diğerleri 1950–2020 yörüngesidir.",
  "eta": "Kümeler arası varyans payı η² = {a}", "ari": "Endeksle kümeleme benzerliği ARI = {a}",
 },
 "en": {
  "clusters": {"Erken gecis": "Early transition", "Orta donem gecisi": "Mid-period transition", "Gec gecis": "Late transition"},
  "src": "Source: UN WPP2024 (Medium variant). Observed period ≤ 2023.",
  "t1": "After cleaning: 237 countries × 151 years", "raw": "Raw data (all rows)",
  "ctry": "Country rows only", "clean": "Clean data",
  "rm1": "− {n} rows: regional, income-group and other aggregates", "rm2": "− {n} rows: year 2101",
  "rows": "rows", "est": "Observed / estimated (analysis period)", "proj": "UN projection (not analysed)",
  "t2": "Countries fall into three groups by the timing of their demographic transition",
  "nocov": "Grey: no data, or small territory not drawn on the map", "ctr": "countries",
  "t3": "In the early-transition cluster, growth shifts from natural increase to migration",
  "nat": "Natural increase", "mig": "Net migration contribution", "yl": "Percentage points / year (mean, 95% interval)",
  "t4": "No single indicator recovers the clusters",
  "ind": {"TFR": "Fertility (TFR)", "LEx": "Life expectancy (LEx)", "MedianAgePop": "Median age",
          "CDR": "Death rate (CDR)", "CNMR": "Net migration (CNMR)"},
  "endx": "Index (3 indicators, 2023)", "x4": "Similarity to clusters (ARI, 1 = identical)", "perfect": "identical",
  "t5": "The index ranks countries but does not draw cluster boundaries", "x5": "Profile index (high: long life, low fertility, older population)", "note4": "The index is a 2023 snapshot; the others use 1950–2020 trajectories.",
  "eta": "Between-cluster variance share η² = {a}", "ari": "Clustering on the index: ARI = {a}",
 }}[LANG]

plt.rcParams.update({"font.size": 17, "axes.titlesize": 26, "axes.titleweight": "bold",
                     "axes.labelsize": 18, "xtick.labelsize": 16, "ytick.labelsize": 16,
                     "legend.fontsize": 16, "figure.dpi": 120, "axes.spines.top": False,
                     "axes.spines.right": False, "font.family": "DejaVu Sans"})


def num(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".") if LANG == "tr" else s


def new_fig(title, h=9):
    fig = plt.figure(figsize=(16, h))
    fig.suptitle(title, x=0.04, ha="left", fontsize=27, fontweight="bold", y=0.975)
    fig.text(0.04, 0.012, T["src"], fontsize=13, color="#666666")
    return fig


kum = pd.read_csv("kumeler.csv")
panel = pd.read_csv("buyume_ayristirma.csv")

# ---------------- 1) Veri temizleme ----------------
RAW = 84360                                     # Medium dosyasindaki toplam satir
clean_n = len(panel)                            # 35.787
n_ctry = panel["ISO3_code"].nunique()           # 237
ctry_rows = clean_n + n_ctry                    # 2101 yili dahil ulke satirlari (36.024)
fig = new_fig(T["t1"])
ax = fig.add_axes([0.20, 0.36, 0.74, 0.50])
labels = [T["raw"], T["ctry"], T["clean"]]
vals = [RAW, ctry_rows, clean_n]
cols = ["#B8B8B8", "#7FA8C9", "#0072B2"]
ax.barh(labels[::-1], vals[::-1], color=cols[::-1], height=0.58)
for y, v in zip(range(3), vals[::-1]):
    ax.text(v + 1200, y, f"{num(v)} {T['rows']}", va="center", fontsize=19, fontweight="bold")
ax.text(RAW * 0.43, 1.52, T["rm1"].format(n=num(RAW - ctry_rows)), fontsize=16, color="#555555", ha="center")
ax.text(RAW * 0.43, 0.52, T["rm2"].format(n=num(ctry_rows - clean_n)), fontsize=16, color="#555555", ha="center")
ax.set_xlim(0, RAW * 1.25); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax2 = fig.add_axes([0.20, 0.10, 0.74, 0.12])
ax2.barh([0], [2023 - 1950 + 1], left=1950, color="#0072B2", height=0.5)
ax2.barh([0], [2100 - 2024 + 1], left=2024, color="white", edgecolor="#888888", hatch="///", height=0.5)
ax2.text(1986, 0, T["est"], ha="center", va="center", color="white", fontsize=15, fontweight="bold")
ax2.text(2062, 0, T["proj"], ha="center", va="center", color="#444444", fontsize=15,
         bbox=dict(fc="white", ec="none", pad=2))
ax2.set_xlim(1950, 2101); ax2.set_yticks([]); ax2.set_xticks([1950, 2000, 2023, 2050, 2100])
ax2.spines["left"].set_visible(False)
fig.savefig(f"video_01_veri{SUF}.png", dpi=120); plt.close(fig)

# ---------------- 2) Kume haritasi ----------------
if not os.path.exists(GEO_FILE):
    urllib.request.urlretrieve(GEO_URL, GEO_FILE)
geo = json.load(open(GEO_FILE, encoding="utf-8"))
cmap = dict(zip(kum["ISO3_code"], kum["kume_adi"]))
fig = new_fig(T["t2"])
ax = fig.add_axes([0.02, 0.10, 0.96, 0.78])
drawn = set()
for f in geo["features"]:
    p = f["properties"]
    if p["NAME"] == "Antarctica":
        continue
    iso = p.get("ISO_A3_EH")
    iso = p["ADM0_A3"] if iso in (None, "-99") else iso
    c = COL.get(cmap.get(iso), GRAY)
    if iso in cmap:
        drawn.add(iso)
    g = f["geometry"]
    for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        ax.add_patch(Polygon(np.array(poly[0]), closed=True, fc=c, ec="white", lw=0.4))
ax.set_xlim(-170, 180); ax.set_ylim(-57, 84); ax.set_aspect("equal"); ax.axis("off")
cnt = kum["kume_adi"].value_counts()
ax.legend(handles=[Patch(fc=COL[k], label=f"{T['clusters'][k]} ({cnt[k]} {T['ctr']})") for k in KEYS],
          loc="lower left", frameon=True, facecolor="white", edgecolor="#CCCCCC", bbox_to_anchor=(0.02, 0.08))
fig.text(0.04, 0.045, T["nocov"], fontsize=13, color="#666666")
fig.savefig(f"video_02_harita{SUF}.png", dpi=120); plt.close(fig)
print(f"Harita: {len(drawn)}/{len(cmap)} ulke cizildi (kalanlar 110m haritada yok)")

# ---------------- 3) Kume bazli buyume ayristirmasi ----------------
kb = pd.read_csv("kume_buyume_ayristirma.csv")
donem = ["1950-1974", "1975-1999", "2000-2023"]
fig = new_fig(T["t3"])
axs = fig.subplots(1, 3, sharey=True, gridspec_kw=dict(left=0.07, right=0.98, top=0.78, bottom=0.14, wspace=0.08))
ymin = min(kb["goc_pct_alt"].min(), kb["dogal_pct_alt"].min()) - 0.1
ymax = max(kb["dogal_pct_ust"].max(), kb["goc_pct_ust"].max()) + 0.2
for ax, k in zip(axs, KEYS):
    d = kb[kb["kume_adi"] == k].set_index("donem").loc[donem]
    x = np.arange(3); w = 0.36
    for off, pre, fc, hatch in [(-w / 2, "dogal_pct", "#555555", ""), (w / 2, "goc_pct", "#FFFFFF", "///")]:
        m = d[pre + "_ort"].to_numpy()
        err = [m - d[pre + "_alt"].to_numpy(), d[pre + "_ust"].to_numpy() - m]
        ax.bar(x + off, m, w, color=fc, edgecolor="#222222", hatch=hatch, yerr=err,
               error_kw=dict(ecolor="#222222", capsize=5, lw=1.8))
    ax.axhline(0, color="#222222", lw=1)
    ax.set_xticks(x); ax.set_xticklabels([s.replace("-", "–") for s in donem], fontsize=14)
    ax.set_title(T["clusters"][k], color=COL[k], fontsize=23)
    ax.set_ylim(ymin, ymax)
    ax.spines["left"].set_visible(k == KEYS[0])
    if k == KEYS[0]:
        ax.set_ylabel(T["yl"], fontsize=15)
axs[0].legend(handles=[Patch(fc="#555555", ec="#222222", label=T["nat"]),
                       Patch(fc="white", ec="#222222", hatch="///", label=T["mig"])],
              loc="upper right", frameon=False)
fig.savefig(f"video_03_buyume{SUF}.png", dpi=120); plt.close(fig)

# ---------------- 4) Q6: tek gosterge yeter mi? ----------------
q6 = pd.read_csv("q6_tek_gosterge.csv")
items = []
for _, r in q6.iterrows():
    items.append((T["ind"][r["gosterge"]], r["ari_tek_gosterge"], r["boot_alt_2.5"], r["boot_ust_97.5"], False))
e = pd.read_csv("endeks.csv")
ecol = "endeks_esit" if "endeks_esit" in e.columns else [c for c in e.columns if "endeks" in c.lower()][0]
m = kum.merge(e[["ISO3_code", ecol]].rename(columns={ecol: "endeks"}), on="ISO3_code").dropna()
lab1d = KMeans(n_clusters=kum["kume"].nunique(), n_init=50, random_state=42).fit(m[["endeks"]]).labels_
ari_e = ari(m["kume"], lab1d)
items.append((T["endx"], ari_e, np.nan, np.nan, True))
items.sort(key=lambda t: t[1])
fig = new_fig(T["t4"])
ax = fig.add_axes([0.27, 0.20, 0.68, 0.64])
for i, (nm, v, lo, hi, is_idx) in enumerate(items):
    ax.barh(i, v, color="#0072B2" if not is_idx else "white", edgecolor="#0072B2", hatch="///" if is_idx else "",
            height=0.62, lw=2)
    if not np.isnan(lo):
        ax.errorbar(v, i, xerr=[[max(v - lo, 0)], [max(hi - v, 0)]], ecolor="#222222", capsize=6, lw=2)
    ax.text(max(v, hi if not np.isnan(hi) else v) + 0.025, i, num(v, 2), va="center", fontsize=19, fontweight="bold")
ax.set_yticks(range(len(items))); ax.set_yticklabels([t[0] for t in items])
ax.axvline(1, color="#888888", ls="--", lw=1.5)
ax.text(0.995, len(items) - 0.4, T["perfect"], ha="right", color="#666666", fontsize=15)
ax.set_xlim(-0.08, 1.05); ax.set_xlabel(T["x4"])
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: num(v, 1)))
fig.text(0.27, 0.05, T["note4"], fontsize=14, color="#555555")
fig.savefig(f"video_04_tek_gosterge{SUF}.png", dpi=120); plt.close(fig)

# ---------------- 5) Endeks x kume ----------------
tot = ((m["endeks"] - m["endeks"].mean()) ** 2).sum()
btw = sum(len(g) * (g["endeks"].mean() - m["endeks"].mean()) ** 2 for _, g in m.groupby("kume_adi"))
eta2 = btw / tot
fig = new_fig(T["t5"])
ax = fig.add_axes([0.20, 0.17, 0.75, 0.62])
rng = np.random.default_rng(42)
for i, k in enumerate(KEYS[::-1]):
    v = m.loc[m["kume_adi"] == k, "endeks"].to_numpy()
    bp = ax.boxplot(v, positions=[i], vert=False, widths=0.5, patch_artist=True, showfliers=False,
                    medianprops=dict(color="#222222", lw=2.5))
    bp["boxes"][0].set(fc=COL[k], alpha=0.35, ec=COL[k], lw=2)
    for part in ("whiskers", "caps"):
        for ln in bp[part]:
            ln.set(color=COL[k], lw=2)
    ax.scatter(v, i + rng.uniform(-0.18, 0.18, len(v)), s=26, color=COL[k], alpha=0.85, edgecolor="white", lw=0.4, zorder=3)
ax.set_yticks(range(3)); ax.set_yticklabels([T["clusters"][k] for k in KEYS[::-1]], fontsize=19)
for lbl, k in zip(ax.get_yticklabels(), KEYS[::-1]):
    lbl.set_color(COL[k]); lbl.set_fontweight("bold")
ax.set_xlabel(T["x5"]); ax.axvline(0, color="#BBBBBB", lw=1, zorder=0)
fig.text(0.20, 0.85, T["eta"].format(a=num(eta2, 2)) + "     |     " + T["ari"].format(a=num(ari_e, 2)),
         fontsize=19, color="#222222")
fig.savefig(f"video_05_endeks{SUF}.png", dpi=120); plt.close(fig)
print("Bitti:", f"eta2={eta2:.2f}", f"ARI_endeks={ari_e:.2f}")
