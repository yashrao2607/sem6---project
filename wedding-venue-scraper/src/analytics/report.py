"""
Summary insights report generator.
Produces a 2–3 page text/markdown report with key findings, advanced insights,
and actionable recommendations.
"""
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import LUXURY_THRESHOLD_INR, LUXURY_CLUSTER_MIN_VENUES, REPORT_DIR

logger = logging.getLogger(__name__)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _inr(val: float) -> str:
    if val >= 1e7:
        return f"₹{val/1e7:.1f} Cr"
    if val >= 1e5:
        return f"₹{val/1e5:.1f}L"
    return f"₹{val:,.0f}"


# ── Advanced insights ─────────────────────────────────────────────────────────

def detect_luxury_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify geographic clusters where avg venue price > ₹10L
    and venue count >= LUXURY_CLUSTER_MIN_VENUES (PRD §10.2).
    """
    price_df = df.dropna(subset=["min_price", "area"])
    if price_df.empty:
        return pd.DataFrame()

    cluster = price_df.groupby(["state", "city", "area"]).agg(
        venue_count=("venue_id", "count"),
        avg_price=("min_price", "mean"),
        avg_rating=("rating", "mean"),
    ).reset_index()

    return cluster[
        (cluster["avg_price"] >= LUXURY_THRESHOLD_INR) &
        (cluster["venue_count"] >= LUXURY_CLUSTER_MIN_VENUES)
    ].sort_values("avg_price", ascending=False)


def cost_vs_popularity_curve(df: pd.DataFrame) -> pd.DataFrame:
    """
    City-level: avg pricing vs. avg review count.
    Flags overpriced (high cost, low reviews) and undervalued destinations.
    """
    sub = df.dropna(subset=["min_price", "review_count"])
    if sub.empty:
        return pd.DataFrame()

    city_stats = sub.groupby("city").agg(
        avg_price=("min_price", "mean"),
        avg_reviews=("review_count", "mean"),
        venue_count=("venue_id", "count"),
        state=("state", "first"),
    ).reset_index()

    # Z-scores for classification
    city_stats["price_z"]   = (city_stats["avg_price"]   - city_stats["avg_price"].mean())   / city_stats["avg_price"].std()
    city_stats["reviews_z"] = (city_stats["avg_reviews"] - city_stats["avg_reviews"].mean()) / city_stats["avg_reviews"].std()

    def _classify(row):
        if row["price_z"] > 0.5 and row["reviews_z"] < -0.5:
            return "Overpriced"
        if row["price_z"] < -0.5 and row["reviews_z"] > 0.5:
            return "Undervalued"
        return "Balanced"

    city_stats["classification"] = city_stats.apply(_classify, axis=1)
    return city_stats.sort_values("avg_price", ascending=False)


def top_micro_locations(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Composite score = 0.4×(venue_density) + 0.3×(avg_rating) + 0.3×(price_diversity).
    Higher score → more versatile wedding micro-destination (PRD §10.2).
    """
    area_df = df.dropna(subset=["area"])
    if area_df.empty:
        return pd.DataFrame()

    stats = area_df.groupby(["area", "city", "state"]).agg(
        venue_count=("venue_id", "count"),
        avg_rating=("rating", "mean"),
        price_std=("min_price", "std"),
    ).reset_index().fillna(0)

    # Normalize 0–1
    for col in ["venue_count", "avg_rating", "price_std"]:
        rng = stats[col].max() - stats[col].min()
        stats[f"{col}_n"] = (stats[col] - stats[col].min()) / rng if rng else 0

    stats["composite_score"] = (
        0.4 * stats["venue_count_n"] +
        0.3 * stats["avg_rating_n"] +
        0.3 * stats["price_std_n"]
    )
    return stats.nlargest(n, "composite_score")[
        ["area", "city", "state", "venue_count", "avg_rating", "price_std", "composite_score"]
    ]


# ── Report generation ─────────────────────────────────────────────────────────

def generate_report(df: pd.DataFrame, output_path: Path = None) -> Path:
    """Generate the full markdown summary report and return its path."""
    output_path = output_path or REPORT_DIR / "wedding_venues_summary.md"

    lines = []
    a = lines.append  # shorthand

    a("# Indian Wedding Destination Intelligence — Summary Report")
    a("")
    a(f"**Dataset size:** {len(df):,} venues  |  "
      f"**States:** {df['state'].nunique()}  |  "
      f"**Cities:** {df['city'].nunique()}")
    a("")

    # ── 1. Geography ──────────────────────────────────────────────────────────
    a("## 1. Geography Intelligence")
    a("")
    a("### Top States by Venue Count")
    state_counts = df.groupby("state").size().sort_values(ascending=False)
    for rank, (state, count) in enumerate(state_counts.items(), 1):
        a(f"{rank}. **{state}** — {count} venues")
    a("")

    a("### Top 10 Cities by Venue Concentration")
    city_counts = df.groupby("city").size().sort_values(ascending=False).head(10)
    for rank, (city, count) in enumerate(city_counts.items(), 1):
        state = df[df["city"] == city]["state"].mode().iloc[0] if not df[df["city"] == city].empty else ""
        a(f"{rank}. **{city}** ({state}) — {count} venues")
    a("")

    # ── 2. Economic ───────────────────────────────────────────────────────────
    a("## 2. Economic Intelligence")
    a("")
    price_df = df.dropna(subset=["min_price"])
    if not price_df.empty:
        a(f"- **Minimum price recorded:** {_inr(price_df['min_price'].min())}")
        a(f"- **Maximum price recorded:** {_inr(price_df['min_price'].max())}")
        a(f"- **Average price:** {_inr(price_df['min_price'].mean())}")
        a(f"- **Median price:** {_inr(price_df['min_price'].median())}")
        a(f"- **Price data coverage:** {price_df.shape[0]/len(df):.1%} of venues")
        a("")
        a("### Median Price by State")
        state_medians = price_df.groupby("state")["min_price"].median().sort_values(ascending=False)
        for state, med in state_medians.items():
            a(f"- **{state}:** {_inr(med)}")
    else:
        a("_No pricing data available in this dataset._")
    a("")

    # ── 3. Venue Type ─────────────────────────────────────────────────────────
    a("## 3. Venue Type Intelligence")
    a("")
    type_df = df.dropna(subset=["venue_type"])
    if not type_df.empty:
        type_counts = type_df["venue_type"].value_counts()
        a(f"Venue type data available for {len(type_df):,} venues ({len(type_df)/len(df):.1%}).")
        a("")
        for vtype, count in type_counts.items():
            pct = count / len(type_df)
            a(f"- **{vtype.replace('_', ' ').title()}:** {count} venues ({pct:.1%})")
        a("")
        a("### Type Concentration by State")
        for state in df["state"].dropna().unique():
            state_types = type_df[type_df["state"] == state]["venue_type"].value_counts().head(2)
            if not state_types.empty:
                dominant = state_types.index[0].replace("_", " ").title()
                a(f"- **{state}:** {dominant} dominates")
    a("")

    # ── 4. Capacity ───────────────────────────────────────────────────────────
    a("## 4. Capacity Intelligence")
    a("")
    cap_df = df.dropna(subset=["capacity_max"])
    if not cap_df.empty:
        a(f"Capacity data available for {len(cap_df):,} venues ({len(cap_df)/len(df):.1%}).")
        boutique = (cap_df["capacity_max"] < 100).sum()
        large    = (cap_df["capacity_max"] >= 500).sum()
        a(f"- **Boutique venues (<100 guests):** {boutique} ({boutique/len(cap_df):.1%})")
        a(f"- **Large venues (500+ guests):**    {large} ({large/len(cap_df):.1%})")
        a(f"- **Average max capacity:**          {cap_df['capacity_max'].mean():.0f} guests")
    a("")

    # ── 5. Advanced Insights ──────────────────────────────────────────────────
    a("## 5. Advanced Insights")
    a("")

    # Luxury clusters
    a("### Luxury Wedding Corridors")
    clusters = detect_luxury_clusters(df)
    if not clusters.empty:
        a(f"Identified **{len(clusters)} luxury micro-clusters** (avg price > ₹10L, ≥{LUXURY_CLUSTER_MIN_VENUES} venues):")
        a("")
        for _, row in clusters.head(10).iterrows():
            a(f"- **{row['area']}, {row['city']}** ({row['state']}) — "
              f"{int(row['venue_count'])} venues, avg {_inr(row['avg_price'])}")
    else:
        a("_Insufficient area-level data to detect luxury clusters. "
          "Increase area extraction coverage._")
    a("")

    # Cost vs popularity
    a("### Cost vs. Popularity Classification")
    curve = cost_vs_popularity_curve(df)
    if not curve.empty:
        overpriced   = curve[curve["classification"] == "Overpriced"]
        undervalued  = curve[curve["classification"] == "Undervalued"]
        a(f"**Overpriced destinations** (high cost, low reviews): "
          f"{', '.join(overpriced['city'].head(5).tolist()) or 'None detected'}")
        a("")
        a(f"**Undervalued destinations** (low cost, high reviews): "
          f"{', '.join(undervalued['city'].head(5).tolist()) or 'None detected'}")
    a("")

    # Top micro-locations
    a("### Top 10 Most Versatile Wedding Micro-Locations")
    top_ml = top_micro_locations(df, n=10)
    if not top_ml.empty:
        a("Ranked by composite score (venue density + rating + price diversity):")
        a("")
        for rank, (_, row) in enumerate(top_ml.iterrows(), 1):
            a(f"{rank}. **{row['area']}, {row['city']}** ({row['state']}) — "
              f"Score: {row['composite_score']:.2f}, "
              f"{int(row['venue_count'])} venues, "
              f"Avg rating: {row['avg_rating']:.1f}")
    a("")

    # ── 6. Recommendations ────────────────────────────────────────────────────
    a("## 6. Key Findings & Recommendations")
    a("")

    # Determine top state
    if not state_counts.empty:
        top_state = state_counts.index[0]
        a(f"- **{top_state} dominates India's destination wedding market** with "
          f"{state_counts.iloc[0]} venues — driven by iconic heritage properties, "
          f"diverse landscapes, and strong tourism infrastructure.")

    # Top city
    if not city_counts.empty:
        top_city = city_counts.index[0]
        top_city_state = df[df["city"] == top_city]["state"].mode()
        state_str = top_city_state.iloc[0] if not top_city_state.empty else ""
        a(f"- **{top_city} ({state_str}) leads in venue concentration** — "
          f"{city_counts.iloc[0]} venues across diverse micro-locations.")

    a("- **Price gap between luxury and budget segments is wide** — "
      "targeted marketing by tier will improve conversion.")
    a("- **Micro-hotspot data is incomplete** — invest in area-level extraction "
      "for deeper clustering analysis.")
    a("- **Expand capacity data coverage** — currently under-represented; "
      "critical for guest capacity planning tools.")
    a("")
    a("---")
    a(f"*Report auto-generated by the Indian Wedding Venue Intelligence Pipeline.*")

    text = "\n".join(lines)
    output_path.write_text(text, encoding="utf-8")
    logger.info("Summary report saved → %s", output_path)
    return output_path
