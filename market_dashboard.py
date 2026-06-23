import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Market Expansion Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #0a0f1e; }
section[data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #1e2d4a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; }
.kpi-card {
    background: linear-gradient(135deg, #0d1b35, #112240);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 8px;
}
.kpi-label { color: #5a7a9e; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
.kpi-value { color: #ffffff; font-size: 28px; font-weight: 800; }
.kpi-sub { color: #4f8ef7; font-size: 12px; margin-top: 4px; }
.section-title { color: #e8f0ff; font-size: 18px; font-weight: 700; margin: 20px 0 4px 0; border-bottom: 1px solid #1e3a5f; padding-bottom: 8px; }
.section-sub { color: #4a6080; font-size: 13px; margin-bottom: 12px; }
.stTabs [data-baseweb="tab-list"] { background: #0d1117; border-radius: 10px; padding: 4px; border: 1px solid #1e2d4a; }
.stTabs [data-baseweb="tab"] { color: #5a7a9e; border-radius: 6px; font-weight: 600; font-size: 13px; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1a3a6e, #2a4a8e) !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    fact   = pd.read_csv("Fact Table.csv")
    region = pd.read_csv("Dim Region.csv")
    age    = pd.read_csv("Dim Age.csv")
    gdp    = pd.read_csv("GDP Table.csv")

    # Fix Sudan Country ID consistency
    region.loc[region['country'] == 'Sudan', 'Country ID'] = 729

    # Merge country name and region into fact using Country ID
    fact = fact.merge(region[['Country ID', 'country', 'Region']], on='Country ID', how='left')

    # Merge age group and age category into fact using Age Group ID
    fact = fact.merge(age[['Age Group ID', 'Age Group', 'Age Category']], on='Age Group ID', how='left')

    return fact, region, age, gdp

fact, dim_region, dim_age, gdp = load_data()

# ── Build Scoring Table ───────────────────────────────────────────────────────
@st.cache_data
def build_score():
    fact_raw = pd.read_csv("Fact Table.csv")
    gdp_raw = pd.read_csv("GDP Table.csv")
    reg_raw = pd.read_csv("Dim Region.csv")
    reg_raw.loc[reg_raw['country'] == 'Sudan', 'Country ID'] = 729

    # Total population 2024 and 2050
    pop_2024 = fact_raw[fact_raw['Year'] == 2024].groupby('Country ID')['Population'].sum().reset_index()
    pop_2024 = pop_2024.rename(columns={'Population': 'Population_2024'})

    pop_2050 = fact_raw[fact_raw['Year'] == 2050].groupby('Country ID')['Population'].sum().reset_index()
    pop_2050 = pop_2050.rename(columns={'Population': 'Population_2050'})

    # Merge together
    score_df = pop_2024.merge(pop_2050, on='Country ID', how='inner')
    score_df = score_df.merge(gdp_raw[['Country ID', 'GDP_Per_Capita']], on='Country ID', how='inner')
    score_df = score_df.merge(reg_raw[['Country ID', 'country', 'Region']], on='Country ID', how='left')

    # Growth rate 2024 to 2050
    score_df['Growth_Rate'] = (score_df['Population_2050'] - score_df['Population_2024']) / score_df['Population_2024']

    # Normalize each factor to 0-1 scale
    def normalize(series):
        return (series - series.min()) / (series.max() - series.min())

    score_df['Score_Population'] = normalize(score_df['Population_2024'])
    score_df['Score_Growth']     = normalize(score_df['Growth_Rate'])
    score_df['Score_GDP']        = normalize(score_df['GDP_Per_Capita'])

    # Final score: 40% population size + 40% growth + 20% GDP
    score_df['Final_Score'] = (
        score_df['Score_Population'] * 0.40 +
        score_df['Score_Growth']     * 0.40 +
        score_df['Score_GDP']        * 0.20
    )

    score_df = score_df.sort_values('Final_Score', ascending=False).reset_index(drop=True)
    score_df['Rank'] = score_df.index + 1

    return score_df

score_df = build_score()
top10    = score_df.head(10)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Market Expansion")
    st.markdown("---")
    selected_year    = st.slider("📅 Year", 1950, 2100, 2024)
    all_regions      = sorted(fact['Region'].dropna().unique().tolist())
    selected_regions = st.multiselect("🗺️ Region", all_regions, default=all_regions)
    selected_gender  = st.selectbox("👤 Gender", ["Both", "Male", "Female"])
    st.markdown("---")
    st.markdown("<span style='color:#4a6080;font-size:11px;'>Data: UN World Population Prospects + World Bank GDP<br>Years: 1950–2100 · Countries: 201</span>", unsafe_allow_html=True)

# ── Filter Data ───────────────────────────────────────────────────────────────
df_y = fact[(fact['Year'] == selected_year) & (fact['Region'].isin(selected_regions))]
df_a = fact[fact['Region'].isin(selected_regions)]
if selected_gender != "Both":
    df_y = df_y[df_y['Gender'] == selected_gender]
    df_a = df_a[df_a['Gender'] == selected_gender]

COLORS = ["#4f8ef7","#f7774f","#4ff7a0","#f7d44f","#c44ff7","#f74f8e","#4ff7f0","#ff6b6b"]
THEME  = "plotly_dark"

def dark_chart(fig, height=380):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,27,53,0.5)",
        height=height,
        font=dict(family="Inter", color="#8899aa"),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor="#0d1b35", linecolor="#1e3a5f"),
        yaxis=dict(gridcolor="#0d1b35", linecolor="#1e3a5f"),
    )
    return fig

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:10px 0 10px 0;'>
    <h1 style='color:white;font-size:32px;font-weight:800;margin:0;background:linear-gradient(135deg,#ffffff,#4f8ef7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        🌍 Global Market Expansion Dashboard
    </h1>
    <p style='color:#4a6080;font-size:14px;margin:6px 0 0 0;'>
        Data-driven country ranking for retail expansion · Population + Growth + GDP scoring model
    </p>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_pop   = df_y['Population'].sum()
top_country = top10.iloc[0]['country']
top_region  = df_y.groupby('Region')['Population'].sum().idxmax()
countries   = df_y['country'].nunique()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>🌐 World Population</div><div class='kpi-value'>{total_pop/1e9:.2f}B</div><div class='kpi-sub'>in {selected_year}</div></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>🏆 Top Expansion Target</div><div class='kpi-value' style='font-size:20px;'>{top_country}</div><div class='kpi-sub'>highest market score</div></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>🗺️ Leading Region</div><div class='kpi-value' style='font-size:20px;'>{top_region}</div><div class='kpi-sub'>highest population</div></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>🌍 Countries Tracked</div><div class='kpi-value'>{countries}</div><div class='kpi-sub'>across all regions</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆  Market Ranking",
    "📈  Population Trends",
    "🗺️  Region Analysis",
    "👨👩  Gender Analysis",
    "👶👴  Age Analysis"
])

# ─── TAB 1 — MARKET RANKING ──────────────────────────────────────────────────
with tab1:
    st.markdown("<div class='section-title'>Top 10 Countries for Retail Expansion</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Score = 40% Population Size + 40% Population Growth (2024→2050) + 20% GDP per Capita · All factors normalized to 0–1 scale</div>", unsafe_allow_html=True)

    r1, r2 = st.columns([1, 1])
    with r1:
        fig = px.bar(
            top10, x='Final_Score', y='country', orientation='h',
            text='Final_Score', color='Final_Score',
            color_continuous_scale=[[0,'#1a3a6e'],[1,'#4f8ef7']],
            template=THEME
        )
        fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
        st.plotly_chart(dark_chart(fig, 420), use_container_width=True)

    with r2:
        display_cols  = ['Rank', 'country', 'Region', 'Population_2024', 'Growth_Rate', 'GDP_Per_Capita', 'Final_Score']
        top10_display = top10[display_cols].copy()
        top10_display['Population_2024'] = (top10_display['Population_2024'] / 1e6).round(1).astype(str) + 'M'
        top10_display['Growth_Rate']     = (top10_display['Growth_Rate'] * 100).round(1).astype(str) + '%'
        top10_display['GDP_Per_Capita']  = '$' + top10_display['GDP_Per_Capita'].round(0).astype(int).astype(str)
        top10_display['Final_Score']     = top10_display['Final_Score'].round(3).astype(str)
        top10_display.columns            = ['Rank', 'Country', 'Region', 'Population', 'Growth', 'GDP/capita', 'Score']
        st.dataframe(top10_display, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-title'>Full Country Rankings</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>All 185 countries ranked by market expansion score</div>", unsafe_allow_html=True)
    full_display = score_df[['Rank', 'country', 'Region', 'Population_2024', 'Growth_Rate', 'GDP_Per_Capita', 'Final_Score']].copy()
    full_display['Population_2024'] = (full_display['Population_2024'] / 1e6).round(1).astype(str) + 'M'
    full_display['Growth_Rate']     = (full_display['Growth_Rate'] * 100).round(1).astype(str) + '%'
    full_display['GDP_Per_Capita']  = '$' + full_display['GDP_Per_Capita'].round(0).astype(int).astype(str)
    full_display['Final_Score']     = full_display['Final_Score'].round(3).astype(str)
    full_display.columns            = ['Rank', 'Country', 'Region', 'Population', 'Growth', 'GDP/capita', 'Score']
    st.dataframe(full_display, use_container_width=True, hide_index=True)

# ─── TAB 2 — POPULATION TRENDS ───────────────────────────────────────────────
with tab2:
    st.markdown("<div class='section-title'>World Population Growth 1950–2100</div>", unsafe_allow_html=True)
    trend = df_a.groupby('Year')['Population'].sum().reset_index()
    fig2  = go.Figure()
    fig2.add_trace(go.Scatter(
        x=trend[trend['Year'] <= 2024]['Year'], y=trend[trend['Year'] <= 2024]['Population'],
        name='Historical', line=dict(color='#4f8ef7', width=3),
        fill='tozeroy', fillcolor='rgba(79,142,247,0.08)'
    ))
    fig2.add_trace(go.Scatter(
        x=trend[trend['Year'] >= 2024]['Year'], y=trend[trend['Year'] >= 2024]['Population'],
        name='Projected', line=dict(color='#f7774f', width=3, dash='dash'),
        fill='tozeroy', fillcolor='rgba(247,119,79,0.08)'
    ))
    fig2.add_vline(x=2024, line_dash="dot", line_color="#4a6080", annotation_text="  Today")
    st.plotly_chart(dark_chart(fig2), use_container_width=True)

    st.markdown("<div class='section-title'>Top 10 Most Populous Countries</div>", unsafe_allow_html=True)
    top10_pop = df_y.groupby('country')['Population'].sum().reset_index().sort_values('Population', ascending=False).head(10)
    fig3 = px.bar(top10_pop, x='Population', y='country', orientation='h',
                  text='Population', color='Population',
                  color_continuous_scale=[[0,'#1a3a6e'],[1,'#4f8ef7']], template=THEME)
    fig3.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig3.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
    st.plotly_chart(dark_chart(fig3), use_container_width=True)

    st.markdown("<div class='section-title'>Country vs Country Comparison</div>", unsafe_allow_html=True)
    all_countries = sorted(fact['country'].dropna().unique().tolist())
    col1, col2    = st.columns(2)
    c1_default    = all_countries.index('India') if 'India' in all_countries else 0
    c2_default    = all_countries.index('China') if 'China' in all_countries else 1
    country1 = col1.selectbox("🔵 Country 1", all_countries, index=c1_default)
    country2 = col2.selectbox("🟠 Country 2", all_countries, index=c2_default)
    compare  = df_a[df_a['country'].isin([country1, country2])].groupby(['Year','country'])['Population'].sum().reset_index()
    fig_cmp  = px.line(compare, x='Year', y='Population', color='country',
                       color_discrete_sequence=['#4f8ef7','#f7774f'], template=THEME)
    fig_cmp.add_vline(x=2024, line_dash="dot", line_color="#4a6080", annotation_text="  Today")
    st.plotly_chart(dark_chart(fig_cmp), use_container_width=True)

# ─── TAB 3 — REGION ANALYSIS ─────────────────────────────────────────────────
with tab3:
    st.markdown("<div class='section-title'>Population by Region</div>", unsafe_allow_html=True)
    region_pop = df_y.groupby('Region')['Population'].sum().reset_index().sort_values('Population', ascending=False)
    c1, c2 = st.columns(2)
    with c1:
        fig4 = px.pie(region_pop, names='Region', values='Population',
                      color_discrete_sequence=COLORS, hole=0.5, template=THEME)
        fig4.update_traces(textposition='outside', textinfo='label+percent')
        fig4.update_layout(showlegend=False)
        st.plotly_chart(dark_chart(fig4, 400), use_container_width=True)
    with c2:
        fig5 = px.bar(region_pop, x='Region', y='Population', text='Population',
                      color='Region', color_discrete_sequence=COLORS, template=THEME)
        fig5.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig5.update_layout(showlegend=False)
        st.plotly_chart(dark_chart(fig5, 400), use_container_width=True)

    st.markdown("<div class='section-title'>Region Population Over Time</div>", unsafe_allow_html=True)
    region_trend = df_a.groupby(['Year','Region'])['Population'].sum().reset_index()
    fig6 = px.line(region_trend, x='Year', y='Population', color='Region',
                   color_discrete_sequence=COLORS, template=THEME)
    fig6.add_vline(x=2024, line_dash="dot", line_color="#4a6080")
    st.plotly_chart(dark_chart(fig6), use_container_width=True)

# ─── TAB 4 — GENDER ANALYSIS ─────────────────────────────────────────────────
with tab4:
    st.markdown("<div class='section-title'>Male vs Female Population</div>", unsafe_allow_html=True)
    g1, g2     = st.columns(2)
    gender_pop = df_y.groupby('Gender')['Population'].sum().reset_index()
    with g1:
        fig7 = px.pie(gender_pop, names='Gender', values='Population',
                      color_discrete_sequence=['#4f8ef7','#f74f8e'], hole=0.55, template=THEME)
        fig7.update_traces(textposition='outside', textinfo='label+percent')
        fig7.update_layout(showlegend=False)
        st.plotly_chart(dark_chart(fig7, 350), use_container_width=True)
    with g2:
        gender_region = df_y.groupby(['Region','Gender'])['Population'].sum().reset_index()
        fig8 = px.bar(gender_region, x='Region', y='Population', color='Gender',
                      color_discrete_sequence=['#4f8ef7','#f74f8e'], barmode='group', template=THEME)
        st.plotly_chart(dark_chart(fig8, 350), use_container_width=True)

    st.markdown("<div class='section-title'>Gender Ratio Over Time</div>", unsafe_allow_html=True)
    gender_trend = df_a.groupby(['Year','Gender'])['Population'].sum().reset_index()
    fig9 = px.line(gender_trend, x='Year', y='Population', color='Gender',
                   color_discrete_sequence=['#4f8ef7','#f74f8e'], template=THEME)
    fig9.add_vline(x=2024, line_dash="dot", line_color="#4a6080")
    st.plotly_chart(dark_chart(fig9), use_container_width=True)

# ─── TAB 5 — AGE ANALYSIS ────────────────────────────────────────────────────
with tab5:
    st.markdown("<div class='section-title'>Age Group Distribution</div>", unsafe_allow_html=True)
    age_pop = df_y.groupby('Age Group')['Population'].sum().reset_index().sort_values('Population', ascending=False)
    fig10 = px.bar(age_pop, x='Age Group', y='Population', text='Population',
                   color='Population',
                   color_continuous_scale=[[0,'#0d1b35'],[0.5,'#4f8ef7'],[1,'#7b61ff']],
                   template=THEME)
    fig10.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig10.update_layout(coloraxis_showscale=False)
    st.plotly_chart(dark_chart(fig10, 400), use_container_width=True)

    a1, a2 = st.columns(2)
    with a1:
        st.markdown("<div class='section-title'>Age Category Split</div>", unsafe_allow_html=True)
        age_cat = df_y.groupby('Age Category')['Population'].sum().reset_index()
        fig11 = px.pie(age_cat, names='Age Category', values='Population',
                       color_discrete_sequence=COLORS, hole=0.5, template=THEME)
        fig11.update_traces(textposition='outside', textinfo='label+percent')
        fig11.update_layout(showlegend=False)
        st.plotly_chart(dark_chart(fig11, 380), use_container_width=True)
    with a2:
        st.markdown("<div class='section-title'>Age Category by Region</div>", unsafe_allow_html=True)
        age_region = df_y.groupby(['Region','Age Category'])['Population'].sum().reset_index()
        fig12 = px.bar(age_region, x='Region', y='Population', color='Age Category',
                       color_discrete_sequence=COLORS, barmode='stack', template=THEME)
        st.plotly_chart(dark_chart(fig12, 380), use_container_width=True)
