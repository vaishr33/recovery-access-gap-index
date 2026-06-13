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
    page_title="ANCHOR",
    layout="wide",
)
st.title("ANCHOR")

st.caption(
    "A Massachusetts dashboard mapping overdose burden, social vulnerability, and access to harm reduction and recovery supports."
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
# Global filters
# -----------------------------
st.sidebar.header("Filters")

county_options = ["All"] + sorted(priority_df["COUNTY"].dropna().unique().tolist())
priority_options = ["All"] + sorted(priority_df["priority_category"].dropna().unique().tolist())
gap_options = ["All"] + sorted(priority_df["gap_category"].dropna().unique().tolist())

selected_county = st.sidebar.selectbox("County", county_options)
selected_priority = st.sidebar.selectbox("Priority level", priority_options)
selected_gap = st.sidebar.selectbox("Access gap level", gap_options)

max_priority_score = float(
    pd.to_numeric(priority_df["distance_adjusted_priority_score"], errors="coerce").max()
)

min_priority_score = st.sidebar.slider(
    "Minimum priority score",
    min_value=0.0,
    max_value=max_priority_score,
    value=0.0,
    step=0.05,
)

filtered_df = priority_df.copy()

if selected_county != "All":
    filtered_df = filtered_df[filtered_df["COUNTY"] == selected_county]

if selected_priority != "All":
    filtered_df = filtered_df[filtered_df["priority_category"] == selected_priority]

if selected_gap != "All":
    filtered_df = filtered_df[filtered_df["gap_category"] == selected_gap]

priority_score_filter = pd.to_numeric(
    filtered_df["distance_adjusted_priority_score"],
    errors="coerce",
)

if min_priority_score > 0:
    filtered_df = filtered_df[priority_score_filter >= min_priority_score].copy()
else:
    filtered_df = filtered_df.copy()

filtered_geo = priority_geo[
    priority_geo["town_join"].isin(filtered_df["town_join"])
].copy()

st.sidebar.caption(
    f"Showing {len(filtered_df):,} of {len(priority_df):,} municipalities."
)

map_overview_tab, profile_tab, priority_tab, explorer_tab, methodology_tab = st.tabs(
    [
        "Map Overview",
        "Community Profile",
        "Top Communities",
        "Access Explorer",
        "Methodology",
    ]
)


# -----------------------------
# Overview tab
# -----------------------------
# -----------------------------
# Map overview tab
# -----------------------------
# -----------------------------
# Map overview tab
# -----------------------------
with map_overview_tab:
    st.subheader("Massachusetts Recovery Access Priority Map")

    st.markdown(
        """
        This map highlights Massachusetts municipalities where opioid-related burden,
        social vulnerability, and recovery access gaps may warrant closer attention.
        """
    )

    map_df = filtered_geo.copy()
    if map_df.empty:
        st.warning("No municipalities match the selected filters. Reset filters in the sidebar to show the map.")
        st.stop()
    map_df = map_df.to_crs("EPSG:4326")

    map_df["distance_adjusted_priority_score"] = pd.to_numeric(
        map_df["distance_adjusted_priority_score"],
        errors="coerce",
    )
    map_df.loc[
        map_df["distance_adjusted_priority_score"] < 0,
        "distance_adjusted_priority_score",
    ] = np.nan

    map_df = map_df.rename(
        columns={
            "distance_adjusted_priority_score": "Priority Score",
            "final_priority_score": "Original Priority Score",
            "recovery_access_gap_score": "Access Gap Score",
            "social_vulnerability_pct": "Social Vulnerability",
            "nearest_any_service_distance_miles": "Nearest Listed Service (miles)",
            "services_within_5_miles": "Listed Services Within 5 Miles",
            "services_within_10_miles": "Listed Services Within 10 Miles",
            "service_types_within_5_miles": "Service Types Within 5 Miles",
            "service_diversity_score": "Service Types Inside Municipality",
            "avg_deaths_2021_2023": "Avg Annual Overdose Deaths",
            "avg_ems_incidents_2022_2023": "Avg Annual EMS Incidents",
            "priority_category": "Priority Level",
            "gap_category": "Access Gap Level",
            "COUNTY": "County",
            "TOWN": "Municipality",
        }
    )

    fig_map = px.choropleth_mapbox(
        map_df,
        geojson=map_df.__geo_interface__,
        locations=map_df.index,
        color="Priority Score",
        hover_name="Municipality",
        hover_data={
            "County": True,
            "Priority Level": True,
            "Access Gap Level": True,
            "Priority Score": ":.2f",
            "Access Gap Score": ":.2f",
            "Social Vulnerability": ":.2f",
            "Nearest Listed Service (miles)": ":.1f",
            "Listed Services Within 5 Miles": True,
            "Listed Services Within 10 Miles": True,
            "Service Types Within 5 Miles": True,
            "Service Types Inside Municipality": True,
            "Avg Annual Overdose Deaths": ":.1f",
            "Avg Annual EMS Incidents": ":.1f",
        },
        mapbox_style="carto-positron",
        center={"lat": 42.25, "lon": -71.8},
        zoom=6.7,
        opacity=0.8,
        color_continuous_scale="YlOrRd",
        max_priority_score = float(map_df["Priority Score"].max())
        labels={
            "Priority Score": "Priority Score",
            "County": "County",
            "Priority Level": "Priority Level",
            "Access Gap Level": "Access Gap Level",
            "Access Gap Score": "Access Gap Score",
            "Social Vulnerability": "Social Vulnerability",
            "Nearest Listed Service (miles)": "Nearest Listed Service (miles)",
            "Listed Services Within 5 Miles": "Listed Services Within 5 Miles",
            "Listed Services Within 10 Miles": "Listed Services Within 10 Miles",
            "Service Types Within 5 Miles": "Service Types Within 5 Miles",
            "Service Types Inside Municipality": "Service Types Inside Municipality",
            "Avg Annual Overdose Deaths": "Avg Annual Overdose Deaths",
            "Avg Annual EMS Incidents": "Avg Annual EMS Incidents",
        },
        range_color=(0, map_df["Priority Score"].max()),
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

    st.divider()
    st.subheader("Dashboard summary")

    total_municipalities = len(filtered_df)
    very_high_priority = (filtered_df["priority_category"] == "Very high priority").sum()
    no_tracked_services = (filtered_df["service_diversity_score"] == 0).sum()
    no_services_10mi = (filtered_df["services_within_10_miles"] == 0).sum()
    median_priority_score = filtered_df["distance_adjusted_priority_score"].median()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Municipalities shown", f"{total_municipalities:,}")
        with st.popover("What does this mean?"):
            st.write(
                "The dashboard shows Massachusetts municipalities included in the current filters. "
                "Each row represents one city or town."
            )

    with col2:
        st.metric("Very high priority", f"{very_high_priority:,}")
        with st.popover("What does this mean?"):
            st.write(
                "Municipalities with the highest combined priority based on overdose burden, "
                "social vulnerability, and access to source-listed supports."
            )

    with col3:
        st.metric("No in-town listings", f"{no_tracked_services:,}")
        with st.popover("What does this mean?"):
            st.write(
                "Municipalities with zero tracked source-listed service categories located inside the municipality. "
                "This does not mean no support exists locally."
            )

    with col4:
        st.metric("No services within 10 mi", f"{no_services_10mi:,}")
        with st.popover("What does this mean?"):
            st.write(
                "Municipalities with no source-listed service records within approximately 10 miles, "
                "using ZIP-code centroid distance estimates."
            )

    with col5:
        st.metric("Median priority score", f"{median_priority_score:.2f}")
        with st.popover("What does this mean?"):
            st.write(
                "The middle priority score among municipalities currently shown after filters are applied."
            )

st.caption(
    "Tracked services are source-listed records from SAMHSA and Mass.gov datasets. "
    "Distance metrics are approximate and use ZIP-code centroids for service locations."
)

# -----------------------------
# Community profile tab
# -----------------------------
with profile_tab:
    # -----------------------------
# Community profile tab
# -----------------------------
 with profile_tab:
    st.subheader("Community Profile")

    st.markdown(
        "Search for a municipality to understand its overdose burden, vulnerability, and access to source-listed harm reduction and recovery supports."
    )

    municipality_options = sorted(priority_df["TOWN"].dropna().unique().tolist())

    selected_municipality = st.selectbox(
        "Search or select a municipality",
        options=municipality_options,
        index=municipality_options.index("REVERE") if "REVERE" in municipality_options else 0,
    )

    profile = priority_df[priority_df["TOWN"] == selected_municipality].iloc[0]

    st.markdown(f"## {profile['TOWN'].title()}, {profile['COUNTY'].title()} County")

    # -----------------------------
    # Summary card
    # -----------------------------
    left, right = st.columns([1.4, 1])

    with left:
        st.markdown("### Priority summary")

        st.markdown(
            f"""
            **Priority level:** `{profile['priority_category']}`  
            **Access gap level:** `{profile['gap_category']}`  
            **Nearest listed service:** `{profile['nearest_any_service_distance_miles']:.1f} miles`  
            **In-town service types:** `{int(profile['service_diversity_score'])}/4`
            """
        )

    with right:
        st.metric("Priority score", f"{profile['distance_adjusted_priority_score']:.2f}")
        st.caption(
            "Higher scores suggest greater need for closer review based on burden, vulnerability, and access."
        )

    st.divider()

    # -----------------------------
    # Main profile metrics
    # -----------------------------
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Avg overdose deaths", f"{profile['avg_deaths_2021_2023']:.1f}")
    m2.metric("Avg EMS incidents", f"{profile['avg_ems_incidents_2022_2023']:.1f}")
    m3.metric("Social vulnerability", f"{profile['social_vulnerability_pct']:.2f}")
    m4.metric("Services within 5 mi", f"{int(profile['services_within_5_miles']):,}")

    m5, m6, m7, m8 = st.columns(4)

    m5.metric("Services within 10 mi", f"{int(profile['services_within_10_miles']):,}")
    m6.metric("Service types within 5 mi", f"{int(profile['service_types_within_5_miles'])}/4")
    m7.metric("Service types within 10 mi", f"{int(profile['service_types_within_10_miles'])}/4")
    m8.metric("In-town service types", f"{int(profile['service_diversity_score'])}/4")

    st.markdown("### Plain-language interpretation")

    if profile["service_diversity_score"] == 0 and profile["services_within_5_miles"] > 0:
        st.info(
            f"{profile['TOWN'].title()} has no tracked source-listed harm reduction or recovery service categories inside the municipality "
            f"in this dataset, but it has {int(profile['services_within_5_miles'])} source-listed service records within approximately 5 miles. "
            f"This suggests that nearby access may be stronger than an in-town count alone implies."
        )
    elif profile["services_within_10_miles"] == 0:
        st.warning(
            f"{profile['TOWN'].title()} has no source-listed service records within approximately 10 miles based on ZIP-code centroid estimates. "
            f"This may indicate a stronger geographic access gap."
        )
    else:
        st.success(
            f"{profile['TOWN'].title()} has source-listed services nearby, with "
            f"{int(profile['services_within_10_miles'])} records within approximately 10 miles."
        )

    # -----------------------------
    # Expandable detail table
    # -----------------------------
    with st.expander("View detailed community metrics"):
        profile_table = pd.DataFrame(
            {
                "Metric": [
                    "Priority score",
                    "Priority level",
                    "Access gap level",
                    "Recovery access gap score",
                    "Social vulnerability",
                    "Average annual overdose deaths",
                    "Average annual EMS incidents",
                    "In-town service types",
                    "Nearest listed service",
                    "Services within 5 miles",
                    "Services within 10 miles",
                    "Service types within 5 miles",
                    "Service types within 10 miles",
                    "Nearest treatment listing",
                    "Nearest peer recovery listing",
                    "Nearest syringe service listing",
                    "Nearest harm reduction listing",
                ],
                "Value": [
                    f"{profile['distance_adjusted_priority_score']:.2f}",
                    profile["priority_category"],
                    profile["gap_category"],
                    f"{profile['recovery_access_gap_score']:.2f}",
                    f"{profile['social_vulnerability_pct']:.2f}",
                    f"{profile['avg_deaths_2021_2023']:.1f}",
                    f"{profile['avg_ems_incidents_2022_2023']:.1f}",
                    f"{int(profile['service_diversity_score'])}/4",
                    f"{profile['nearest_any_service_distance_miles']:.1f} miles",
                    f"{int(profile['services_within_5_miles'])}",
                    f"{int(profile['services_within_10_miles'])}",
                    f"{int(profile['service_types_within_5_miles'])}/4",
                    f"{int(profile['service_types_within_10_miles'])}/4",
                    f"{profile['nearest_treatment_distance_miles']:.1f} miles",
                    f"{profile['nearest_peer_recovery_distance_miles']:.1f} miles",
                    f"{profile['nearest_ssp_distance_miles']:.1f} miles",
                    f"{profile['nearest_harm_reduction_distance_miles']:.1f} miles",
                ],
            }
        )

        st.dataframe(profile_table, use_container_width=True, hide_index=True)
# -----------------------------
# -----------------------------
# Top communities tab
# -----------------------------
with priority_tab:
    st.subheader("Top Communities")

    st.markdown(
        "Ranked municipalities based on the ANCHOR Priority Score. Higher scores suggest greater need for closer review."
    )

    search_term = st.text_input("Search municipality", "")

    top_df = filtered_df.copy()

    if search_term:
        top_df = top_df[
            top_df["TOWN"].str.contains(search_term, case=False, na=False)
        ]

    top_df = top_df.sort_values(
        "distance_adjusted_priority_score",
        ascending=False,
    ).copy()

    display_top = top_df[[
        "TOWN",
        "COUNTY",
        "priority_category",
        "distance_adjusted_priority_score",
        "nearest_any_service_distance_miles",
        "services_within_5_miles",
        "services_within_10_miles",
        "service_diversity_score",
        "social_vulnerability_pct",
        "avg_deaths_2021_2023",
        "avg_ems_incidents_2022_2023",
    ]].rename(
        columns={
            "TOWN": "Municipality",
            "COUNTY": "County",
            "priority_category": "Priority Level",
            "distance_adjusted_priority_score": "Priority Score",
            "nearest_any_service_distance_miles": "Nearest Listed Service (mi)",
            "services_within_5_miles": "Services Within 5 mi",
            "services_within_10_miles": "Services Within 10 mi",
            "service_diversity_score": "In-Town Service Types",
            "social_vulnerability_pct": "Social Vulnerability",
            "avg_deaths_2021_2023": "Avg Annual Overdose Deaths",
            "avg_ems_incidents_2022_2023": "Avg Annual EMS Incidents",
        }
    )

    if display_top.empty:
        st.warning("No municipalities match the current filters or search.")
    else:
        chart_df = display_top.head(20).sort_values("Priority Score", ascending=True)

        fig_bar = px.bar(
            chart_df,
            x="Priority Score",
            y="Municipality",
            orientation="h",
            color="Priority Level",
            hover_data=[
                "County",
                "Nearest Listed Service (mi)",
                "Services Within 5 mi",
                "Services Within 10 mi",
                "Social Vulnerability",
            ],
            title="Top 20 Municipalities by Priority Score",
        )

        fig_bar.update_layout(
            height=650,
            yaxis_title="",
            xaxis_title="Priority Score",
            margin={"r": 20, "t": 50, "l": 20, "b": 20},
        )

        st.plotly_chart(fig_bar, use_container_width=True)

        with st.expander("View ranked data table"):
            st.dataframe(
                display_top,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "Download filtered table as CSV",
                data=display_top.to_csv(index=False),
                file_name="filtered_priority_communities.csv",
                mime="text/csv",
            )
# -----------------------------
# Access explorer tab
# -----------------------------
with explorer_tab:
    st.subheader("Access Explorer")

    st.markdown(
        "Explore how access gaps, social vulnerability, and distance-based service access relate to each other."
    )

    scatter_df = filtered_df.copy()

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
            "nearest_any_service_distance_miles": ":.2f",
            "services_within_5_miles": True,
            "services_within_10_miles": True,
            "distance_adjusted_priority_score": ":.3f",
        },
        labels={
            "recovery_access_gap_score": "Recovery Access Gap Score",
            "social_vulnerability_pct": "Social Vulnerability",
            "distance_adjusted_priority_score": "Priority Score",
            "priority_category": "Priority Level",
            "COUNTY": "County",
            "avg_deaths_2021_2023": "Avg Annual Overdose Deaths",
            "avg_ems_incidents_2022_2023": "Avg Annual EMS Incidents",
            "nearest_any_service_distance_miles": "Nearest Listed Service (mi)",
            "services_within_5_miles": "Services Within 5 mi",
            "services_within_10_miles": "Services Within 10 mi",
        },
        title="Access Gap vs Social Vulnerability",
    )

    fig_scatter.update_layout(
        height=650,
        xaxis_title="Recovery Access Gap Score",
        yaxis_title="Social Vulnerability",
        margin={"r": 20, "t": 50, "l": 20, "b": 20},
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("#### Municipalities with no in-town listings but nearby services")

    no_intown_nearby = filtered_df[
        (filtered_df["service_diversity_score"] == 0)
        & (filtered_df["services_within_5_miles"] > 0)
    ].copy()

    st.metric(
        "No in-town listings but at least one service within 5 miles",
        f"{len(no_intown_nearby):,}",
    )

    access_table = no_intown_nearby[[
        "TOWN",
        "COUNTY",
        "nearest_any_service_distance_miles",
        "services_within_5_miles",
        "services_within_10_miles",
        "service_types_within_5_miles",
        "distance_adjusted_priority_score",
    ]].rename(
        columns={
            "TOWN": "Municipality",
            "COUNTY": "County",
            "nearest_any_service_distance_miles": "Nearest Listed Service (mi)",
            "services_within_5_miles": "Services Within 5 mi",
            "services_within_10_miles": "Services Within 10 mi",
            "service_types_within_5_miles": "Service Types Within 5 mi",
            "distance_adjusted_priority_score": "Priority Score",
        }
    ).sort_values("Nearest Listed Service (mi)")

    st.dataframe(access_table, use_container_width=True, hide_index=True)


# -----------------------------
# Methodology tab
# -----------------------------
with methodology_tab:
    st.subheader("Definitions and Methodology")

    st.markdown(
        """
        ### Key terms

        **Municipality**  
        A city or town in Massachusetts. Each row in the dashboard represents one municipality.

        **Source-listed recovery services**  
        Service access indicators are based on public source-listed records collected from SAMHSA and Mass.gov datasets.

        Tracked service categories include:

        - SAMHSA treatment facilities
        - Peer recovery centers
        - Syringe service programs
        - Harm reduction program listings

        **In-town service types**  
        The number of tracked service categories listed inside a municipality, from 0 to 4.

        **Distance-based access**  
        Distance metrics estimate how close each municipality is to source-listed services. Service locations are represented using ZIP-code centroids, so these are approximate access measures.

        **Priority Score**  
        The main dashboard score. It combines opioid-related burden, social vulnerability, source-listed service access, and nearby distance-based access.

        ### Important interpretation note

        This dashboard is a prioritization and exploration tool. It does not prove that a municipality has no services, nor does it measure service capacity, quality, eligibility, waitlists, transportation barriers, or real travel time.
        """
    )