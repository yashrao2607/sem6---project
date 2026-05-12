"""
Static chart generation (Matplotlib / Seaborn).
Produces all 10 required visualisations from PRD §10.1.
"""
import logging
import shutil
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import CHARTS_DIR, VENUE_TYPES

logger = logging.getLogger(__name__)

CHARTS_DIR.mkdir(parents=True, exist_ok=True)
ALL_INDIA_CHARTS_DIR = CHARTS_DIR / "all_india"
ALL_INDIA_CHARTS_DIR.mkdir(parents=True, exist_ok=True)

_PALETTE = "deep"
_FIG_DPI  = 150
_FIG_SIZE = (12, 7)
_PER_PLATE_FLOOR = 100
_PACKAGE_MIN_INR = 50_000
_PACKAGE_RATIO_THRESHOLD = 50

sns.set_theme(style="whitegrid", palette=_PALETTE)


def _save(fig: plt.Figure, name: str) -> Path:
    path = CHARTS_DIR / f"{name}.png"
    fig.savefig(str(path), dpi=_FIG_DPI, bbox_inches="tight")
    shutil.copyfile(path, ALL_INDIA_CHARTS_DIR / f"{name}.png")
    plt.close(fig)
    logger.info("Saved chart → %s", path)
    return path


def _as_bool(series: pd.Series) -> pd.Series:
    """Normalize messy truthy flags from CSV/Excel round-trips."""
    lowered = series.astype("string").fillna("").str.strip().str.lower()
    return lowered.isin({"true", "1", "yes"})


def _price_views(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the mixed price schema into two comparable analytical views:
    1. observed per-plate quotes
    2. package / minimum-event quotes
    """
    price_df = df.copy()
    if "_imputed_min_price" in price_df.columns:
        price_df["_is_imputed"] = _as_bool(price_df["_imputed_min_price"])
    else:
        price_df["_is_imputed"] = False

    per_plate = price_df[
        price_df["price_per_plate"].notna()
        & ~price_df["_is_imputed"]
        & price_df["price_per_plate"].between(_PER_PLATE_FLOOR, 50_000)
    ].copy()

    ratio = price_df["min_price"] / price_df["price_per_plate"]
    package_mask = (
        price_df["min_price"].notna()
        & ~price_df["_is_imputed"]
        & (
            (
                price_df["price_per_plate"].notna()
                & price_df["price_per_plate"].gt(0)
                & ratio.gt(_PACKAGE_RATIO_THRESHOLD)
            )
            | (
                price_df["price_per_plate"].isna()
                & price_df["min_price"].gt(_PACKAGE_MIN_INR)
            )
        )
    )
    package = price_df[package_mask].copy()
    return per_plate, package


def _state_labels_with_counts(series: pd.Series, order: pd.Index) -> list[str]:
    counts = series.value_counts()
    return [f"{label} (n={int(counts.get(label, 0))})" for label in order]


def _format_inr(x: float, _: int) -> str:
    if x >= 100_000:
        return f"₹{x/100000:.1f}L"
    if x >= 1_000:
        return f"₹{x/1000:.1f}k"
    return f"₹{x:.0f}"


# ── Chart 1: State Ranking Bar Chart ─────────────────────────────────────────

def chart_state_ranking(df: pd.DataFrame) -> Path:
    """Total venues per state, sorted descending."""
    counts = df.groupby("state").size().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=_FIG_SIZE)
    sns.barplot(x=counts.values, y=counts.index, palette=_PALETTE, ax=ax)
    ax.set_title("Wedding Venue Count by State", fontsize=16, fontweight="bold")
    ax.set_xlabel("Number of Venues")
    ax.set_ylabel("State")
    for bar, val in zip(ax.patches, counts.values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                str(int(val)), va="center", fontsize=10)
    plt.tight_layout()
    return _save(fig, "01_state_ranking")


# ── Chart 2: City Venue Density Heatmap ──────────────────────────────────────

def chart_city_heatmap(df: pd.DataFrame) -> Path:
    """Venue count heatmap: top cities × states."""
    top_cities = df.groupby("city").size().nlargest(20).index
    sub = df[df["city"].isin(top_cities)]
    pivot = sub.groupby(["state", "city"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="YlOrRd", linewidths=0.5, ax=ax)
    ax.set_title("Venue Density Heatmap: State × City (Top 20 Cities)", fontsize=14, fontweight="bold")
    ax.set_xlabel("City")
    ax.set_ylabel("State")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return _save(fig, "02_city_heatmap")


# ── Chart 3: Cost Distribution Box Plots ─────────────────────────────────────

def chart_cost_distribution(df: pd.DataFrame) -> Path:
    """Separate per-plate and package pricing into readable state-level distributions."""
    per_plate_df, package_df = _price_views(df)
    if per_plate_df.empty and package_df.empty:
        logger.warning("No price data — skipping cost distribution chart")
        return None

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    if not per_plate_df.empty:
        upper = per_plate_df["price_per_plate"].quantile(0.99)
        per_plate_plot = per_plate_df[per_plate_df["price_per_plate"] <= upper].copy()
        order_state = (
            per_plate_plot.groupby("state")["price_per_plate"]
            .median()
            .sort_values(ascending=False)
            .index
        )
        sns.boxplot(
            data=per_plate_plot,
            y="state",
            x="price_per_plate",
            order=order_state,
            palette="Blues",
            showfliers=False,
            ax=axes[0],
        )
        axes[0].set_title("Observed Per-Plate Quotes by State", fontsize=12, fontweight="bold")
        axes[0].set_xlabel("Price per Plate (INR)")
        axes[0].set_ylabel("")
        axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(_format_inr))
        axes[0].set_yticks(range(len(order_state)))
        axes[0].set_yticklabels(_state_labels_with_counts(per_plate_plot["state"], order_state))
    else:
        axes[0].axis("off")
        axes[0].set_title("Observed Per-Plate Quotes by State", fontsize=12, fontweight="bold")

    if not package_df.empty:
        order_state = (
            package_df.groupby("state")["min_price"]
            .median()
            .sort_values(ascending=False)
            .index
        )
        sns.boxplot(
            data=package_df,
            y="state",
            x="min_price",
            order=order_state,
            palette="Oranges",
            showfliers=False,
            ax=axes[1],
        )
        axes[1].set_xscale("log")
        axes[1].set_title("Observed Package / Event Quotes by State", fontsize=12, fontweight="bold")
        axes[1].set_xlabel("Minimum Package Quote (INR, log scale)")
        axes[1].set_ylabel("")
        axes[1].set_xticks([50_000, 100_000, 200_000, 500_000, 1_000_000, 5_000_000])
        axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(_format_inr))
        axes[1].set_yticks(range(len(order_state)))
        axes[1].set_yticklabels(_state_labels_with_counts(package_df["state"], order_state))
    else:
        axes[1].axis("off")
        axes[1].set_title("Observed Package / Event Quotes by State", fontsize=12, fontweight="bold")

    plt.tight_layout()
    return _save(fig, "03_cost_distribution")


# ── Chart 4: Venue Type Pie Chart ─────────────────────────────────────────────

def chart_venue_type_pie(df: pd.DataFrame) -> Path:
    """Percentage share of each venue type."""
    type_counts = df["venue_type"].dropna().value_counts()
    if type_counts.empty:
        logger.warning("No venue type data — skipping pie chart")
        return None

    fig, ax = plt.subplots(figsize=(9, 9))
    wedges, texts, autotexts = ax.pie(
        type_counts.values,
        labels=type_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette(_PALETTE, n_colors=len(type_counts))
    )
    for t in autotexts:
        t.set_fontsize(11)
    ax.set_title("Venue Type Distribution", fontsize=16, fontweight="bold")
    plt.tight_layout()
    return _save(fig, "04_venue_type_pie")


# ── Chart 5: Capacity Distribution Histogram ─────────────────────────────────

def chart_capacity_histogram(df: pd.DataFrame) -> Path:
    """Guest capacity distribution across all venues."""
    cap_df = df.dropna(subset=["capacity_max"])
    if cap_df.empty:
        logger.warning("No capacity data — skipping histogram")
        return None

    fig, ax = plt.subplots(figsize=_FIG_SIZE)
    bins = [0, 50, 100, 200, 300, 500, 750, 1000, 2000, 5000]
    ax.hist(cap_df["capacity_max"], bins=bins, edgecolor="white", color=sns.color_palette(_PALETTE)[0])
    ax.set_title("Guest Capacity Distribution", fontsize=16, fontweight="bold")
    ax.set_xlabel("Maximum Guest Capacity")
    ax.set_ylabel("Number of Venues")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
    plt.tight_layout()
    return _save(fig, "05_capacity_histogram")


# ── Chart 6: Price vs. Rating Scatter ────────────────────────────────────────

def chart_price_vs_rating(df: pd.DataFrame) -> Path:
    """Scatter plot of observed per-plate quotes against non-zero ratings."""
    per_plate_df, _ = _price_views(df)
    sub = per_plate_df[per_plate_df["rating"].fillna(0) > 0].copy()
    if sub.empty:
        logger.warning("No price+rating data — skipping scatter")
        return None

    upper = sub["price_per_plate"].quantile(0.99)
    sub = sub[sub["price_per_plate"] <= upper].copy()
    review_scale = np.log1p(sub["review_count"].fillna(0))
    max_review_scale = review_scale.max() if len(review_scale) else 1
    sizes = 25 + (65 * review_scale / max(max_review_scale, 1))

    fig, ax = plt.subplots(figsize=_FIG_SIZE)
    scatter = ax.scatter(
        sub["price_per_plate"], sub["rating"],
        c=sub["state"].astype("category").cat.codes,
        cmap="tab10", alpha=0.55, s=sizes, edgecolors="none"
    )
    ax.set_title("Per-Plate Price vs. Rating", fontsize=16, fontweight="bold")
    ax.set_xlabel("Observed Price per Plate (INR)")
    ax.set_ylabel("Rating (0–5)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_format_inr))
    ax.set_ylim(0.5, 5.2)

    # Trend line
    z = np.polyfit(sub["price_per_plate"], sub["rating"], 1)
    p = np.poly1d(z)
    xs = np.linspace(sub["price_per_plate"].min(), sub["price_per_plate"].max(), 200)
    ax.plot(xs, p(xs), "r--", linewidth=1.5, label="Trend")

    # State legend
    unique_states = sub["state"].unique()
    handles = [
        plt.Line2D([0], [0], marker="o", color="w",
                   markerfacecolor=plt.cm.tab10(i / max(len(unique_states), 1)),
                   label=state, markersize=8)
        for i, state in enumerate(sorted(unique_states))
    ]
    ax.legend(handles=handles, title="State", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    ax.text(
        0.02,
        0.03,
        f"Rated venues only; observed per-plate quotes only (n={len(sub):,})",
        transform=ax.transAxes,
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )
    plt.tight_layout()
    return _save(fig, "06_price_vs_rating")


# ── Chart 7: Luxury vs. Budget Segmentation ──────────────────────────────────

def chart_luxury_segmentation(df: pd.DataFrame) -> Path:
    """Show meaningful price tiers separately for per-plate and package quotes."""
    per_plate_df, package_df = _price_views(df)
    if per_plate_df.empty and package_df.empty:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    per_plate_bins = [0, 600, 1000, 2000, np.inf]
    per_plate_labels = [
        "Value\n(<₹600)",
        "Standard\n(₹600–999)",
        "Premium\n(₹1k–1.9k)",
        "Luxury\n(₹2k+)",
    ]
    if not per_plate_df.empty:
        per_plate_df["tier"] = pd.cut(
            per_plate_df["price_per_plate"],
            bins=per_plate_bins,
            labels=per_plate_labels,
            right=False,
        )
        tier_counts = per_plate_df["tier"].value_counts().reindex(per_plate_labels).fillna(0)
        axes[0].bar(
            tier_counts.index,
            tier_counts.values,
            color=sns.color_palette("Blues", n_colors=len(per_plate_labels)),
        )
        axes[0].set_title("Observed Per-Plate Price Segments", fontsize=13, fontweight="bold")
        axes[0].set_xlabel("Segment")
        axes[0].set_ylabel("Number of Venues")
    else:
        axes[0].axis("off")
        axes[0].set_title("Observed Per-Plate Price Segments", fontsize=13, fontweight="bold")

    package_bins = [0, 100_000, 200_000, 500_000, np.inf]
    package_labels = ["<₹1L", "₹1–2L", "₹2–5L", "₹5L+"]
    if not package_df.empty:
        package_df["tier"] = pd.cut(
            package_df["min_price"],
            bins=package_bins,
            labels=package_labels,
            right=False,
        )
        pivot = package_df.groupby(["state", "tier"]).size().unstack(fill_value=0)
        pivot = pivot.reindex(columns=package_labels).fillna(0)
        pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
        pivot.plot(kind="bar", stacked=True, ax=axes[1], colormap="OrRd")
        axes[1].set_title("Package / Event Quote Segments by State", fontsize=13, fontweight="bold")
        axes[1].set_xlabel("State")
        axes[1].set_ylabel("Number of Venues")
        axes[1].legend(title="Quote band", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
        plt.setp(axes[1].get_xticklabels(), rotation=35, ha="right")
    else:
        axes[1].axis("off")
        axes[1].set_title("Package / Event Quote Segments by State", fontsize=13, fontweight="bold")

    plt.tight_layout()
    return _save(fig, "07_luxury_segmentation")


# ── Chart 8: Micro-Hotspot Map (Bar) ─────────────────────────────────────────

def chart_micro_hotspots(df: pd.DataFrame) -> Path:
    """Top 20 areas by venue concentration."""
    area_df = df.dropna(subset=["area"])
    if area_df.empty:
        logger.warning("No area data — skipping micro-hotspot chart")
        return None

    top_areas = area_df.groupby("area").size().nlargest(20)
    fig, ax = plt.subplots(figsize=_FIG_SIZE)
    sns.barplot(x=top_areas.values, y=top_areas.index, palette="viridis", ax=ax)
    ax.set_title("Top 20 Micro-Hotspot Areas by Venue Count", fontsize=14, fontweight="bold")
    ax.set_xlabel("Number of Venues")
    ax.set_ylabel("Area")
    for bar, val in zip(ax.patches, top_areas.values):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                str(int(val)), va="center", fontsize=9)
    plt.tight_layout()
    return _save(fig, "08_micro_hotspots")


# ── Chart 9: Cost vs. Location Correlation Matrix ────────────────────────────

def chart_cost_location_matrix(df: pd.DataFrame) -> Path:
    """Heatmap of median observed per-plate pricing by state and venue type."""
    per_plate_df, _ = _price_views(df)
    sub = per_plate_df.dropna(subset=["venue_type"])
    if sub.empty:
        return None

    pivot = sub.pivot_table(values="price_per_plate", index="state",
                            columns="venue_type", aggfunc="median")
    pivot = pivot.reindex(columns=[c for c in VENUE_TYPES if c in pivot.columns])
    fig, ax = plt.subplots(figsize=(13, 7))
    sns.heatmap(
        pivot, annot=True, fmt=".0f", cmap="YlOrRd",
        linewidths=0.4, ax=ax,
        cbar_kws={"label": "Median Price per Plate (INR)"}
    )
    ax.set_title("Median Price per Plate (₹): State × Venue Type", fontsize=14, fontweight="bold")
    ax.set_xlabel("Venue Type")
    ax.set_ylabel("State")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return _save(fig, "09_cost_location_matrix")


# ── Chart 10: Source Coverage Comparison ─────────────────────────────────────

def chart_source_coverage(df: pd.DataFrame) -> Path:
    """Stacked bar: data completeness (fill rate) by source."""
    fields = ["area", "venue_type", "min_price", "price_per_plate",
              "capacity_max", "rating", "review_count"]

    rows = []
    for src, grp in df.groupby("source"):
        for f in fields:
            fill = grp[f].notna().mean()
            rows.append({"source": src, "field": f, "fill_rate": fill})

    cov_df = pd.DataFrame(rows)
    pivot = cov_df.pivot(index="source", columns="field", values="fill_rate")

    fig, ax = plt.subplots(figsize=(13, 6))
    pivot.plot(kind="bar", ax=ax, colormap="Set2")
    ax.set_title("Data Field Fill Rate by Source", fontsize=14, fontweight="bold")
    ax.set_xlabel("Source")
    ax.set_ylabel("Fill Rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.legend(title="Field", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    plt.setp(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    return _save(fig, "10_source_coverage")


# ── Generate all charts ───────────────────────────────────────────────────────

def generate_all_charts(df: pd.DataFrame) -> list[Optional[Path]]:
    """Run all 10 chart generators and return list of output paths."""
    generators = [
        chart_state_ranking,
        chart_city_heatmap,
        chart_cost_distribution,
        chart_venue_type_pie,
        chart_capacity_histogram,
        chart_price_vs_rating,
        chart_luxury_segmentation,
        chart_micro_hotspots,
        chart_cost_location_matrix,
        chart_source_coverage,
    ]
    paths = []
    for gen in generators:
        try:
            p = gen(df)
            paths.append(p)
        except Exception as exc:
            logger.error("Chart '%s' failed: %s", gen.__name__, exc)
            paths.append(None)
    return paths
