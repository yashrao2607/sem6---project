"""
Interactive HTML dashboard using Plotly.
Generates a single self-contained HTML file with all charts.
"""
import logging
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import DASHBOARD_DIR, LUXURY_THRESHOLD_INR

logger = logging.getLogger(__name__)
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)


def _fmt_inr(val: float) -> str:
    if val >= 1e7:
        return f"₹{val/1e7:.1f}Cr"
    if val >= 1e5:
        return f"₹{val/1e5:.1f}L"
    return f"₹{val:,.0f}"


def build_dashboard(df: pd.DataFrame, output_path: Path = None) -> Path:
    """
    Build a Plotly-based interactive HTML dashboard.
    Returns the path to the generated HTML file.
    """
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        import plotly.io as pio
    except ImportError:
        logger.error("Plotly not installed — skipping interactive dashboard. "
                     "Install with: pip install plotly")
        return None

    output_path = output_path or DASHBOARD_DIR / "wedding_venues_dashboard.html"
    figs = []

    # ── 1. State ranking ─────────────────────────────────────────────────────
    state_counts = df.groupby("state").size().sort_values(ascending=False).reset_index()
    state_counts.columns = ["state", "count"]
    fig1 = px.bar(state_counts, x="count", y="state", orientation="h",
                  title="Venue Count by State",
                  labels={"count": "Venues", "state": "State"},
                  color="count", color_continuous_scale="Blues")
    fig1.update_layout(showlegend=False)
    figs.append(("State Ranking", fig1))

    # ── 2. Top cities ─────────────────────────────────────────────────────────
    city_counts = df.groupby(["city", "state"]).size().reset_index(name="count")
    city_counts = city_counts.nlargest(25, "count")
    fig2 = px.bar(city_counts, x="city", y="count", color="state",
                  title="Top 25 Cities by Venue Count",
                  labels={"count": "Venues", "city": "City"})
    fig2.update_layout(xaxis_tickangle=-40)
    figs.append(("City Rankings", fig2))

    # ── 3. Venue type distribution ────────────────────────────────────────────
    type_counts = df["venue_type"].dropna().value_counts().reset_index()
    type_counts.columns = ["venue_type", "count"]
    fig3 = px.pie(type_counts, names="venue_type", values="count",
                  title="Venue Type Distribution", hole=0.3)
    figs.append(("Venue Types", fig3))

    # ── 4. Price distribution by state ────────────────────────────────────────
    price_df = df.dropna(subset=["min_price"])
    if not price_df.empty:
        fig4 = px.box(price_df, x="state", y="min_price",
                      title="Price Distribution by State",
                      labels={"min_price": "Min Price (INR)", "state": "State"},
                      color="state")
        fig4.update_layout(xaxis_tickangle=-40, showlegend=False)
        fig4.update_yaxes(tickformat="₹,.0f")
        figs.append(("Price by State", fig4))

    # ── 5. Price vs Rating scatter ────────────────────────────────────────────
    pr_df = df.dropna(subset=["min_price", "rating"])
    if not pr_df.empty:
        fig5 = px.scatter(pr_df, x="min_price", y="rating",
                          color="state", hover_name="venue_name",
                          hover_data=["city", "venue_type"],
                          title="Price vs. Rating",
                          labels={"min_price": "Min Price (INR)", "rating": "Rating (0-5)"},
                          opacity=0.7)
        figs.append(("Price vs Rating", fig5))

    # ── 6. Luxury segmentation ────────────────────────────────────────────────
    if not price_df.empty:
        def tier(p):
            if p >= LUXURY_THRESHOLD_INR:
                return "Luxury (>₹10L)"
            elif p >= 500_000:
                return "Premium (₹5-10L)"
            elif p >= 200_000:
                return "Mid-range (₹2-5L)"
            return "Budget (<₹2L)"

        tier_df = price_df.copy()
        tier_df["tier"] = tier_df["min_price"].apply(tier)
        tier_state = tier_df.groupby(["state", "tier"]).size().reset_index(name="count")
        fig6 = px.bar(tier_state, x="state", y="count", color="tier",
                      title="Pricing Tier Distribution by State",
                      labels={"count": "Venues"},
                      color_discrete_sequence=px.colors.sequential.YlGn_r)
        fig6.update_layout(xaxis_tickangle=-40)
        figs.append(("Luxury Segmentation", fig6))

    # ── 7. Top micro-hotspots ─────────────────────────────────────────────────
    area_df = df.dropna(subset=["area"])
    if not area_df.empty:
        top_areas = area_df.groupby(["area", "state"]).size().reset_index(name="count")
        top_areas = top_areas.nlargest(20, "count")
        fig7 = px.bar(top_areas, x="count", y="area", orientation="h",
                      color="state",
                      title="Top 20 Micro-Hotspot Areas by Venue Count",
                      labels={"count": "Venues", "area": "Area"})
        figs.append(("Micro-Hotspots", fig7))

    # ── 8. Capacity distribution ──────────────────────────────────────────────
    cap_df = df.dropna(subset=["capacity_max"])
    if not cap_df.empty:
        fig8 = px.histogram(cap_df, x="capacity_max", nbins=30,
                             title="Guest Capacity Distribution",
                             labels={"capacity_max": "Max Guest Capacity"},
                             color_discrete_sequence=["#2196F3"])
        figs.append(("Capacity", fig8))

    # ── 9. Source coverage ────────────────────────────────────────────────────
    src_counts = df.groupby("source").size().reset_index(name="count")
    fig9 = px.pie(src_counts, names="source", values="count",
                  title="Venue Records by Source", hole=0.3)
    figs.append(("Source Coverage", fig9))

    # ── Assemble HTML ─────────────────────────────────────────────────────────
    html_parts = [
        "<!DOCTYPE html><html lang='en'><head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<title>Indian Wedding Destination Intelligence Dashboard</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:0;padding:20px;background:#f5f5f5;}",
        "h1{text-align:center;color:#333;padding:20px 0;}",
        ".tab-container{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px;}",
        ".tab-btn{padding:10px 20px;border:none;border-radius:4px;cursor:pointer;",
        "background:#ddd;font-size:14px;transition:background 0.2s;}",
        ".tab-btn.active{background:#2196F3;color:white;}",
        ".chart-panel{display:none;background:white;border-radius:8px;",
        "padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.1);}",
        ".chart-panel.active{display:block;}",
        ".summary{background:white;border-radius:8px;padding:20px;",
        "margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,0.1);}",
        ".kpi{display:inline-block;margin:10px;text-align:center;}",
        ".kpi .number{font-size:2em;font-weight:bold;color:#2196F3;}",
        ".kpi .label{font-size:0.9em;color:#666;}",
        "</style></head><body>",
        "<h1>🇮🇳 Indian Wedding Destination Intelligence Dashboard</h1>",
    ]

    # KPI summary bar
    html_parts.append("<div class='summary'><h2>Dataset Overview</h2>")
    kpis = [
        (len(df), "Total Venues"),
        (df["state"].nunique(), "States Covered"),
        (df["city"].nunique(), "Cities Covered"),
        (df["area"].nunique() if "area" in df else 0, "Micro-Areas"),
        (f"{df['min_price'].notna().mean():.0%}" if "min_price" in df else "N/A", "Price Coverage"),
        (f"{df['capacity_max'].notna().mean():.0%}" if "capacity_max" in df else "N/A", "Capacity Coverage"),
    ]
    for num, lbl in kpis:
        html_parts.append(
            f"<div class='kpi'><div class='number'>{num}</div><div class='label'>{lbl}</div></div>"
        )
    html_parts.append("</div>")

    # Tab buttons
    html_parts.append("<div class='tab-container'>")
    for i, (tab_name, _) in enumerate(figs):
        active = "active" if i == 0 else ""
        html_parts.append(
            f"<button class='tab-btn {active}' onclick=\"showTab({i})\">{tab_name}</button>"
        )
    html_parts.append("</div>")

    # Chart panels
    for i, (tab_name, fig) in enumerate(figs):
        active = "active" if i == 0 else ""
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=("cdn" if i == 0 else False))
        html_parts.append(f"<div id='panel-{i}' class='chart-panel {active}'>")
        html_parts.append(chart_html)
        html_parts.append("</div>")

    # Tab switching script
    html_parts.append("""
    <script>
    function showTab(idx) {
        document.querySelectorAll('.chart-panel').forEach((p,i)=>p.classList.toggle('active',i===idx));
        document.querySelectorAll('.tab-btn').forEach((b,i)=>b.classList.toggle('active',i===idx));
    }
    </script>
    """)
    html_parts.append("</body></html>")

    output_path.write_text("\n".join(html_parts), encoding="utf-8")
    logger.info("Dashboard saved → %s", output_path)
    return output_path
