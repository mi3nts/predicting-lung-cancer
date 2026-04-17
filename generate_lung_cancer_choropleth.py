import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / ".cache"
MPL_CACHE_DIR = ROOT / ".matplotlib-cache"
CACHE_DIR.mkdir(exist_ok=True)
MPL_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", str(CACHE_DIR))
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap


SHAPEFILE_ZIP = ROOT / "data" / "raw" / "census_tiger_tl_2019_us_county.zip"
MORTALITY_CSV = ROOT / "data" / "processed" / "preprocessed_fips_lung_cancer" / "preprocessed_lung_cancer_fips_2019.csv"
OUTPUT_PATH = ROOT / "paper" / "Figures" / "fig1_lung_cancer_mortality_map_2019.png"

EXCLUDE_STATEFP = {"02", "15", "60", "66", "69", "72", "78"}
PALETTE = ["#fff7bc", "#fee391", "#fec44f", "#fe9929", "#d95f0e"]


def build_labels(edges: np.ndarray) -> list[str]:
    labels = []
    for lower, upper in zip(edges[:-1], edges[1:]):
        labels.append(f"{lower:.1f}--{upper:.1f}")
    return labels


def main() -> None:
    if not SHAPEFILE_ZIP.exists():
        raise FileNotFoundError(
            f"Missing county geometry: {SHAPEFILE_ZIP}. Download the 2019 Census TIGER county zip first."
        )

    gdf = gpd.read_file(SHAPEFILE_ZIP)
    gdf["GEOID"] = gdf["GEOID"].astype(str).str.zfill(5)

    df = pd.read_csv(MORTALITY_CSV)
    df["Fips"] = df["Fips"].astype(str).str.zfill(5)
    df["lung_cancer_rate_per_100k"] = df["lung_cancer_mortality_rate"] * 100000

    merged = gdf.merge(
        df[["Fips", "lung_cancer_rate_per_100k"]],
        left_on="GEOID",
        right_on="Fips",
        how="left",
    )

    contiguous = merged[~merged["STATEFP"].isin(EXCLUDE_STATEFP)].copy()
    contiguous = contiguous.to_crs(epsg=5070)

    values = contiguous["lung_cancer_rate_per_100k"].dropna()
    quantile_edges = values.quantile([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]).to_numpy()
    quantile_labels = build_labels(quantile_edges)

    contiguous["quintile"] = pd.qcut(
        contiguous["lung_cancer_rate_per_100k"].rank(method="first"),
        q=5,
        labels=quantile_labels,
    )

    fig, ax = plt.subplots(1, 1, figsize=(13.5, 7.6), facecolor="white")
    cmap = ListedColormap(PALETTE)

    contiguous.plot(
        column="quintile",
        ax=ax,
        cmap=cmap,
        categorical=True,
        edgecolor="white",
        linewidth=0.08,
        missing_kwds={"color": "#d9d9d9", "edgecolor": "white", "linewidth": 0.08},
    )

    legend_handles = [
        mpatches.Patch(color=color, label=label)
        for color, label in zip(PALETTE, quantile_labels)
    ]
    legend_handles.append(mpatches.Patch(color="#d9d9d9", label="No data"))

    ax.legend(
        handles=legend_handles,
        title="Deaths per 100,000\n(quintiles)",
        loc="lower right",
        frameon=False,
        fontsize=9,
        title_fontsize=9,
    )
    ax.axis("off")

    plt.tight_layout(pad=0.4)
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

    print(f"Saved: {OUTPUT_PATH}")
    print(f"Range: {values.min():.1f} to {values.max():.1f} deaths per 100,000")
    print(f"Darkest quintile lower bound: {quantile_edges[4]:.1f} deaths per 100,000")
    print(f"Counties with data: {values.shape[0]}")


if __name__ == "__main__":
    main()
