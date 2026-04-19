"""
Static chart generation (Matplotlib / Seaborn).
Produces all 10 required visualisations from PRD §10.1.
"""
import logging
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
from config.settings import CHARTS_DIR, LUXURY_THRESHOLD_INR, VENUE_TYPES

logger = logging.getLogger(__name__)

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

_PALETTE = "deep"
_FIG_DPI  = 150
_FIG_SIZE = (12, 7)

sns.set_theme(style="whitegrid", palette=_PALETTE)


def _save(fig: plt.Figure, name: str) -> Path:
    path = CHARTS_DIR / f"{name}.png"
    fig.savefig(str(path), dpi=_FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved chart → %s", path)
    return path


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
    """Box plots of min_price by state."""
    price_df = df.dropna(subset=["min_price"])
    if price_df.empty:
        logger.warning("No price data — skipping cost distribution chart")
        return None

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # By state
    order_state = price_df.groupby("state")["min_price"].median().sort_values(ascending=False).index
    sns.boxplot(data=price_df, y="state", x="min_price", order=order_state,
                palette=_PALETTE, ax=axes[0])
    axes[0].set_title("Price Distribution by State (min_price)", fontsize=12, fontweight="bold")
    axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.1f}L"))
    axes[0].set_xlabel("Price (INR)")

    # Top 10 cities by median price
    top10_cities = price_df.groupby("city")["min_price"].median().nlargest(10).index
    city_df = price_df[price_df["city"].isin(top10_cities)]
    order_city = city_df.groupby("city")["min_price"].median().sort_values(ascending=False).index
    sns.boxplot(data=city_df, y="city", x="min_price", order=order_city,
                palette=_PALETTE, ax=axes[1])
    axes[1].set_title("Price Distribution: Top 10 Cities (min_price)", fontsize=12, fontweight="bold")
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.1f}L"))
    axes[1].set_xlabel("Price (INR)")

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
    """Scatter plot: venue pricing vs. user rating."""
    sub = df.dropna(subset=["min_price", "rating"])
    if sub.empty:
        logger.warning("No price+rating data — skipping scatter")
        return None

    fig, ax = plt.subplots(figsize=_FIG_SIZE)
    scatter = ax.scatter(
        sub["min_price"], sub["rating"],
        c=sub["state"].astype("category").cat.codes,
        cmap="tab10", alpha=0.6, s=50, edgecolors="none"
    )
    ax.set_title("Price vs. Rating", fontsize=16, fontweight="bold")
    ax.set_xlabel("Min Price (INR)")
    ax.set_ylabel("Rating (0–5)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.0f}L"))

    # Trend line
    z = np.polyfit(sub["min_price"], sub["rating"], 1)
    p = np.poly1d(z)
    xs = np.linspace(sub["min_price"].min(), sub["min_price"].max(), 200)
    ax.plot(xs, p(xs), "r--", linewidth=1.5, label="Trend")
    ax.legend()

    # State legend
    unique_states = sub["state"].unique()
    handles = [
        plt.Line2D([0], [0], marker="o", color="w",
                   markerfacecolor=plt.cm.tab10(i / max(len(unique_states), 1)),
                   label=state, markersize=8)
        for i, state in enumerate(sorted(unique_states))
    ]
    ax.legend(handles=handles, title="State", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    plt.tight_layout()
    return _save(fig, "06_price_vs_rating")


# ── Chart 7: Luxury vs. Budget Segmentation ──────────────────────────────────

def chart_luxury_segmentation(df: pd.DataFrame) -> Path:
    """Classify venues into pricing tiers and show geographic breakdown."""
    price_df = df.dropna(subset=["min_price"]).copy()
    if price_df.empty:
        return None

    def _tier(p):
        if p >= LUXURY_THRESHOLD_INR:
            return "Luxury (>₹10L)"
        elif p >= 500_000:
            return "Premium (₹5–10L)"
        elif p >= 200_000:
            return "Mid-range (₹2–5L)"
        else:
            return "Budget (<₹2L)"

    price_df["tier"] = price_df["min_price"].apply(_tier)
    tier_order = ["Luxury (>₹10L)", "Premium (₹5–10L)", "Mid-range (₹2–5L)", "Budget (<₹2L)"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Overall tier distribution
    tier_counts = price_df["tier"].value_counts().reindex(tier_order).fillna(0)
    axes[0].bar(tier_counts.index, tier_counts.values,
                color=sns.color_palette("RdYlGn", n_colors=4))
    axes[0].set_title("Venue Pricing Tier Distribution", fontsize=13, fontweight="bold")
    axes[0].set_xlabel("Tier")
    axes[0].set_ylabel("Number of Venues")
    plt.setp(axes[0].get_xticklabels(), rotation=20, ha="right")

    # Tier breakdown by state
    pivot = price_df.groupby(["state", "tier"]).size().unstack(fill_value=0)
    pivot = pivot.reindex(columns=[c for c in tier_order if c in pivot.columns])
    pivot.plot(kind="bar", ax=axes[1], colormap="RdYlGn")
    axes[1].set_title("Pricing Tiers by State", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("State")
    axes[1].set_ylabel("Number of Venues")
    axes[1].legend(title="Tier", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    plt.setp(axes[1].get_xticklabels(), rotation=40, ha="right")

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
    """Heatmap of median pricing by state and venue type."""
    sub = df.dropna(subset=["min_price", "venue_type"])
    if sub.empty:
        return None

    pivot = sub.pivot_table(values="min_price", index="state",
                             columns="venue_type", aggfunc="median")
    fig, ax = plt.subplots(figsize=(13, 7))
    sns.heatmap(
        pivot / 1e5, annot=True, fmt=".1f", cmap="YlOrRd",
        linewidths=0.4, ax=ax,
        cbar_kws={"label": "Median Min Price (₹ Lakhs)"}
    )
    ax.set_title("Median Min Price (₹L): State × Venue Type", fontsize=14, fontweight="bold")
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
