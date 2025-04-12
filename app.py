import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data with caching
@st.cache_data
def load_data():
    overall = pd.read_csv("mw_overall.csv")
    pw = pd.read_csv("mw_pw.csv")
    pw_profiles = pd.read_csv("mw_pw_profiles.csv")
    style_features = pd.read_csv("style_based_features.csv")
    total = pd.read_csv("total_data.csv")
    return overall, pw, pw_profiles, style_features, total

overall, pw, pw_profiles, style_features, total = load_data()

st.set_page_config(page_title="Batsmen Dashboard", layout="wide")
st.title("🏏 Batsmen Performance Analytics")

# Sidebar
st.sidebar.header("🔍 Filters")

batsmen = sorted(overall['batter'].unique())
selected_batsman = st.sidebar.selectbox("Choose Batsman", batsmen)

years = sorted(overall['year'].dropna().unique())
min_year, max_year = int(min(years)), int(max(years))
selected_years = st.sidebar.slider("Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

styles = sorted(style_features['bowling_type'].dropna().unique())
selected_style = st.sidebar.selectbox("Bowling Style", styles)

# Data filtering
overall_filtered = overall[
    (overall['batter'] == selected_batsman) &
    (overall['year'] >= selected_years[0]) &
    (overall['year'] <= selected_years[1])
]

style_filtered = style_features[
    (style_features['batter'] == selected_batsman) &
    (style_features['year'] >= selected_years[0]) &
    (style_features['year'] <= selected_years[1]) &
    (style_features['bowling_type'] == selected_style)
]

# KPIs
st.markdown("### 📊 Key Performance Indicators")
col1, col2, col3 = st.columns(3)

if not overall_filtered.empty:
    total_runs = int(overall_filtered['runs'].sum())
    avg = overall_filtered['avg'].mean() if 'avg' in overall_filtered else total_runs / max(1, len(overall_filtered))
    sr = overall_filtered['sr'].mean() if 'sr' in overall_filtered else 0

    col1.metric("Total Runs", f"{total_runs}")
    col2.metric("Average", f"{avg:.2f}")
    col3.metric("Strike Rate", f"{sr:.2f}")
else:
    st.warning("No data available for selected filters.")

# Year-wise performance
st.markdown("### 📈 Year-wise Performance")

if not overall_filtered.empty:
    fig_line = px.line(
        overall_filtered,
        x='year',
        y='runs',
        markers=True,
        title=f"{selected_batsman}'s Runs Over the Years",
        labels={'runs': 'Runs', 'year': 'Year'},
        template="plotly_dark"
    )
    fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No year-wise data to show.")

# Bowling Style Performance
st.markdown(f"### 🎯 Performance vs {selected_style} Bowling Style")

if not style_filtered.empty:
    fig_bar = px.bar(
        style_filtered,
        x='year',
        y='runs_scored',
        color='year',
        title=f"{selected_batsman} vs {selected_style} Bowlers",
        labels={'runs_scored': 'Runs Scored', 'year': 'Year'},
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No style-wise data to display.")

# Raw Data Table
with st.expander("📄 View Raw Filtered Data"):
    st.dataframe(overall_filtered.reset_index(drop=True))
