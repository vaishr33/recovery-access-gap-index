from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Recovery Access Gap Index",
    page_icon="🧭",
    layout="wide",
)


# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

FINAL_PRIORITY_CSV = PROCESSED_DIR / "municipality_final_priority_index_with_distance.csv"
FINAL_PRIORITY_GEOJSON = PROCESSED_DIR / "municipality_final_priority_index_with_distance.geojson"


# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    priority_df = pd.read_csv(FINAL_PRIORITY_CSV)
    priority_geo = gpd.read_file(FINAL_PRIORITY_GEOJSON)

    score_cols = [
        "social_vulnerability_pct",
        "final_priority_score",
        "distance_adjusted_priority_score",
        "recovery_access_gap_score",
        "nearest_any_service_distance_miles",
    ]

    for col in score_cols:
        if col in priority_df.columns:
            priority_df[col] = pd.to_numeric(priority_df[col], errors="coerce")
            priority_df.loc[priority_df[col] < 0, col] = np.nan

        if col in priority_geo.columns:
            priority_geo[col] = pd.to_numeric(priority_geo[col], errors="coerce")
            priority_geo.loc[priority_geo[col] < 0, col] = np.nan

    return priority_df, priority_geo


priority_df, priority_geo = load_data()


# -----------------------------
# Header
# -----------------------------
st.title("Recovery Access Gap Index")
st.caption(
    "A municipality-level dashboard identifying Massachusetts communities with high opioid-related burden, "
    "limited source-listed recovery service access, elevated social vulnerability, and distance-based access gaps."
)


overview_tab, map_tab, priority_tab, explorer_tab, methodology_tab = st.tabs(
    [
        "Overview",
        "Priority Map",
        "Top Communities",
        "Access vs Burden",
        "Methodology",
    ]
)


# -----------------------------
# Overview tab
# -----------------------------
with overview_tab:
    st.subheader("Dashboard Overview")

    st.markdown(
        """
        This dashboard combines opioid-related burden, recovery service listings,
        social vulnerability, and distance-based access metrics to identify
        Massachusetts municipalities that may warrant closer attention.
        """
    )

    total_municipalities = len(priority_df)
    very_high_priority = (priority_df["priority_category"] == "Very high priority").sum()
    no_tracked_services = (priority_df["service_diversity_score"] == 0).sum()
    no_services_10mi = (priority_df["services_within_10_miles"] == 0).sum()
    median_priority_score = priority_df["distance_adjusted_priority_score"].median()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Municipalities analyzed", f"{total_municipalities:,}")
    col2.metric("Very high priority", f"{very_high_priority:,}")
    col3.metric("No in-town listings", f"{no_tracked_services:,}")
    col4.metric("No services within 10 mi", f"{no_services_10mi:,}")
    col5.metric("Median adjusted score", f"{median_priority_score:.2f}")

    st.caption(
        "Tracked services are source-listed records from SAMHSA and Mass.gov datasets. "
        "Zero in-town listings does not prove that no recovery support exists locally. "
        "Distance metrics are approximate and use ZIP-code centroids for service locations."
    )

    st.subheader("Highest Distance-Adjusted Priority Scores")

    overview_top = priority_df.sort_values(
        "distance_adjusted_priority_score",
        ascending=False,
    )[[
        "TOWN",
        "COUNTY",
        "distance_adjusted_priority_score",
        "final_priority_score",
        "nearest_any_service_distance_miles",
        "services_within_5_miles",
        "services_within_10_miles",
        "priority_category",
    ]].head(10)

    st.dataframe(overview_top, use_container_width=True)


# -----------------------------
# Map tab
# -----------------------------
with map_tab:
    st.subheader("Massachusetts Distance-Adjusted Priority Map")

    map_df = priority_geo.copy()
    map_df = map_df.to_crs("EPSG:4326")

    map_df["distance_adjusted_priority_score"] = pd.to_numeric(
        map_df["distance_adjusted_priority_score"],
        errors="coerce",
    )
    map_df.loc[
        map_df["distance_adjusted_priority_score"] < 0,
        "distance_adjusted_priority_score",
    ] = np.nan

    fig_map = px.choropleth_mapbox(
        map_df,
        geojson=map_df.__geo_interface__,
        locations=map_df.index,
        color="distance_adjusted_priority_score",
        hover_name="TOWN",
        hover_data={
            "COUNTY": True,
            "priority_category": True,
            "gap_category": True,
            "distance_adjusted_priority_score": ":.3f",
            "final_priority_score": ":.3f",
            "recovery_access_gap_score": ":.3f",
            "social_vulnerability_pct": ":.3f",
            "nearest_any_service_distance_miles": ":.2f",
            "services_within_5_miles": True,
            "services_within_10_miles": True,
            "service_types_within_5_miles": True,
            "service_diversity_score": True,
            "avg_deaths_2021_2023": ":.1f",
            "avg_ems_incidents_2022_2023": ":.1f",
        },
        mapbox_style="carto-positron",
        center={"lat": 42.25, "lon": -71.8},
        zoom=6.7,
        opacity=0.8,
        color_continuous_scale="YlOrRd",
        range_color=(0, map_df["distance_adjusted_priority_score"].quantile(0.95)),
        labels={
            "distance_adjusted_priority_score": "Distance-Adjusted Priority Score",
        },
    )

    fig_map.update_layout(
        height=750,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    fig_map.update_traces(
        marker_line_width=0.35,
        marker_line_color="white",
    )

    st.plotly_chart(fig_map, use_container_width=True)


# -----------------------------
# Top communities tab
# -----------------------------
with priority_tab:
    st.subheader("Top Priority Communities")

    top_priority = priority_df.sort_values(
        "distance_adjusted_priority_score",
        ascending=False,
    )[[
        "TOWN",
        "COUNTY",
        "estimated_population",
        "recovery_access_gap_score",
        "social_vulnerability_pct",
        "final_priority_score",
        "distance_adjusted_priority_score",
        "nearest_any_service_distance_miles",
        "services_within_5_miles",
        "services_within_10_miles",
        "service_types_within_5_miles",
        "priority_category",
    ]].head(25)

    st.dataframe(top_priority, use_container_width=True)

    st.subheader("Highest Distance-Adjusted Priority Scores")

    top_chart = top_priority.sort_values(
        "distance_adjusted_priority_score",
        ascending=True,
    )

    fig_bar = px.bar(
        top_chart,
        x="distance_adjusted_priority_score",
        y="TOWN",
        orientation="h",
        color="priority_category",
        hover_data=[
            "COUNTY",
            "estimated_population",
            "final_priority_score",
            "nearest_any_service_distance_miles",
            "services_within_5_miles",
            "services_within_10_miles",
        ],
        labels={
            "distance_adjusted_priority_score": "Distance-Adjusted Priority Score",
            "TOWN": "Municipality",
            "priority_category": "Priority Category",
        },
        title="Top 25 Municipalities by Distance-Adjusted Priority Score",
    )

    fig_bar.update_layout(
        height=700,
        yaxis_title="",
        xaxis_title="Distance-Adjusted Priority Score",
    )

    st.plotly_chart(fig_bar, use_container_width=True)


# -----------------------------
# Explorer tab
# -----------------------------
with explorer_tab:
    st.subheader("Access vs Burden Explorer")

    scatter_df = priority_df.copy()

    scatter_cols = [
        "recovery_access_gap_score",
        "social_vulnerability_pct",
        "distance_adjusted_priority_score",
    ]

    for col in scatter_cols:
        scatter_df[col] = pd.to_numeric(scatter_df[col], errors="coerce")
        scatter_df.loc[scatter_df[col] < 0, col] = np.nan

    scatter_df = scatter_df.dropna(subset=scatter_cols)

    fig_scatter = px.scatter(
        scatter_df,
        x="recovery_access_gap_score",
        y="social_vulnerability_pct",
        size="distance_adjusted_priority_score",
        size_max=35,
        color="priority_category",
        hover_name="TOWN",
        hover_data={
            "COUNTY": True,
            "avg_deaths_2021_2023": ":.1f",
            "avg_ems_incidents_2022_2023": ":.1f",
            "service_diversity_score": True,
            "nearest_any_service_distance_miles": ":.2f",
            "services_within_5_miles": True,
            "services_within_10_miles": True,
            "recovery_access_gap_score": ":.3f",
            "social_vulnerability_pct": ":.3f",
            "distance_adjusted_priority_score": ":.3f",
        },
        labels={
            "recovery_access_gap_score": "Recovery Access Gap Score",
            "social_vulnerability_pct": "Social Vulnerability Percentile",
            "distance_adjusted_priority_score": "Distance-Adjusted Priority Score",
            "priority_category": "Priority Category",
        },
        title="Municipalities by Recovery Access Gap and Social Vulnerability",
    )

    fig_scatter.update_layout(
        height=650,
        xaxis_title="Recovery Access Gap Score",
        yaxis_title="Social Vulnerability Percentile",
    )

    st.plotly_chart(fig_scatter, use_container_width=True)


# -----------------------------
# Methodology tab
# -----------------------------
with methodology_tab:
    st.subheader("Definitions and Methodology")

    st.markdown(
        """
        ### Key terms

        **Municipality**  
        A city or town in Massachusetts. In the dataset, this is stored as `TOWN`.
        Each row in the dashboard represents one municipality.

        **County**  
        The county that a municipality belongs to. County is used as a grouping field,
        not as the main unit of analysis.

        **Source-listed recovery services**  
        Service access indicators are based on public source-listed records collected
        from SAMHSA and Mass.gov datasets.

        Tracked service categories include:

        - SAMHSA treatment facilities
        - Peer recovery centers
        - Syringe service programs
        - Harm reduction program listings

        **Service diversity score**  
        A score from 0 to 4 showing how many different tracked service categories are
        listed within a municipality.

        **Distance-based access**  
        Distance metrics estimate how close each municipality is to source-listed services.
        Service locations are represented using ZIP-code centroids, so these are approximate
        access measures rather than exact travel distances.

        **Overdose death burden**  
        Average annual opioid-related overdose deaths from 2021 to 2023, based on
        city/town of residence.

        **EMS incident burden**  
        Average annual suspected opioid-related EMS incidents from 2022 to 2023.
        This reflects emergency response burden by incident location, not strictly
        nonfatal overdose counts.

        **Recovery Access Gap Score**  
        A score that increases when a municipality has high overdose/EMS burden and
        low tracked in-municipality recovery service access.

        **Social Vulnerability Percentile**  
        A municipality-level estimate derived from CDC/ATSDR Social Vulnerability Index
        tract-level data. Higher values indicate higher relative social vulnerability.

        **Final Priority Score**  
        Combines Recovery Access Gap Score with social vulnerability.

        **Distance-Adjusted Priority Score**  
        Adjusts the final priority score using nearby service availability within 5 miles.
        This helps avoid overstating gaps in municipalities that have no in-town listing
        but have nearby source-listed services.

        ### Important interpretation note

        This dashboard is a prioritization and exploration tool. It does not prove that a
        municipality has no services, nor does it measure service capacity, quality,
        eligibility, waitlists, transportation barriers, or real travel time.
        """
    )