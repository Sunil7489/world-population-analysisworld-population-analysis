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
# ── Google Drive Fact Table URL ───────────────────────────────────────────────
FACT_URL = "https://drive.google.com/uc?export=download&id=1oBJWEwYGYSYHpJgCWn-xPOuwy24ehac2"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Animated background ── */
.stApp {
    background: linear-gradient(135deg, #020408 0%, #050d1a 30%, #0a0f1e 60%, #050810 100%);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060d1a 0%, #0d1527 100%);
    border-right: 1px solid rgba(79,142,247,0.15);
}
section[data-testid="stSidebar"] * { color: #c8d6f0 !important; }

/* ── Hide default UI ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0.5rem; }

/* ── KPI Cards with glow animation ── */
.kpi-card {
    background: linear-gradient(135deg, #0a1628 0%, #0f2040 50%, #0a1628 100%);
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: 16px;
    padding: 24px 26px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: cardFadeIn 0.8s ease forwards;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(79,142,247,0.25);
}
@keyframes cardFadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-gradient, linear-gradient(90deg, #4f8ef7, #7b61ff));
    border-radius: 16px 16px 0 0;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: -40px; right: -40px;
    width: 120px; height: 120px;
    background: var(--glow-color, rgba(79,142,247,0.06));
    border-radius: 50%;
    animation: pulse 3s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.6; }
    50%       { transform: scale(1.2); opacity: 1; }
}
.kpi-icon   { font-size: 30px; margin-bottom: 10px; display: block; }
.kpi-label  { color: #3a5a7e !important; font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
.kpi-value  { color: #ffffff !important; font-size: 34px; font-weight: 900; line-height: 1; margin-bottom: 6px; }
.kpi-sub    { font-size: 12px; font-weight: 500; color: #4f8ef7 !important; }

/* ── Page title gradient ── */
.page-title {
    font-size: 40px;
    font-weight: 900;
    background: linear-gradient(135deg, #ffffff 0%, #4f8ef7 40%, #7b61ff 70%, #f74f8e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    animation: titleFadeIn 1s ease forwards;
}
@keyframes titleFadeIn {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}
.page-subtitle {
    color: #3a5a7e !important;
    font-size: 14px;
    font-weight: 400;
    margin-top: 6px;
    animation: titleFadeIn 1.2s ease forwards;
}

/* ── Section titles ── */
.section-header { margin: 28px 0 4px 0; }
.section-tag {
    display: inline-block;
    background: rgba(79,142,247,0.12);
    border: 1px solid rgba(79,142,247,0.25);
    color: #4f8ef7 !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 6px;
}
.section-title {
    color: #e8f0ff !important;
    font-size: 20px;
    font-weight: 700;
    margin: 0 0 4px 0;
}
.section-sub {
    color: #2a4060 !important;
    font-size: 13px;
    margin-bottom: 16px;
}

/* ── Glowing divider ── */
.glow-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(79,142,247,0.4) 30%, rgba(123,97,255,0.4) 70%, transparent);
    margin: 24px 0;
    box-shadow: 0 0 8px rgba(79,142,247,0.2);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10,15,30,0.8);
    border-radius: 12px;
    padding: 6px;
    gap: 4px;
    border: 1px solid rgba(79,142,247,0.15);
    backdrop-filter: blur(10px);
}
.stTabs [data-baseweb="tab"] {
    color: #3a5a7e !important;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 18px;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1a3a6e, #2a4a9e) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 16px rgba(79,142,247,0.4);
}

/* ── Sidebar title ── */
.sidebar-brand {
    font-size: 22px;
    font-weight: 900;
    background: linear-gradient(135deg, #4f8ef7, #7b61ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    fact   = pd.read_csv(FACT_URL)
    region = pd.read_csv("data/dim_region.csv")
    age    = pd.read_csv("data/dim_age.csv")
    gdp    = pd.read_csv("data/gdp_table.csv")
    region.loc[region['country'] == 'Sudan', 'Country ID'] = 729
    fact = fact.merge(region[['Country ID', 'country', 'Region']], on='Country ID', how='left')
    fact = fact.merge(age[['Age Group ID', 'Age Group', 'Age Category']], on='Age Group ID', how='left')
    return fact, region, age, gdp

fact, dim_region, dim_age, gdp = load_data()

# ── Build Scoring Table ───────────────────────────────────────────────────────
@st.cache_data
def build_score():
    fact_raw = pd.read_csv(FACT_URL)
    gdp_raw  = pd.read_csv("data/gdp_table.csv")
    reg_raw  = pd.read_csv("data/dim_region.csv")
    reg_raw.loc[reg_raw['country'] == 'Sudan', 'Country ID'] = 729

    pop_2024 = fact_raw[fact_raw['Year'] == 2024].groupby('Country ID')['Population'].sum().reset_index()
    pop_2024 = pop_2024.rename(columns={'Population': 'Population_2024'})
    pop_2050 = fact_raw[fact_raw['Year'] == 2050].groupby('Country ID')['Population'].sum().reset_index()
    pop_2050 = pop_2050.rename(columns={'Population': 'Population_2050'})

    score_df = pop_2024.merge(pop_2050, on='Country ID', how='inner')
    score_df = score_df.merge(gdp_raw[['Country ID', 'GDP_Per_Capita']], on='Country ID', how='inner')
    score_df = score_df.merge(reg_raw[['Country ID', 'country', 'Region']], on='Country ID', how='left')

    score_df['Growth_Rate'] = (score_df['Population_2050'] - score_df['Population_2024']) / score_df['Population_2024']

    def normalize(s):
        return (s - s.min()) / (s.max() - s.min())

    score_df['Score_Population'] = normalize(score_df['Population_2024'])
    score_df['Score_Growth']     = normalize(score_df['Growth_Rate'])
    score_df['Score_GDP']        = normalize(score_df['GDP_Per_Capita'])
    score_df['Final_Score']      = (
        score_df['Score_Population'] * 0.40 +
        score_df['Score_Growth']     * 0.40 +
        score_df['Score_GDP']        * 0.20
    )
    score_df = score_df.sort_values('Final_Score', ascending=False).reset_index(drop=True)
    score_df['Rank'] = score_df.index + 1
    return score_df

score_df = build_score()
top10    = score_df.head(10)

# ── Chart helpers ─────────────────────────────────────────────────────────────
COLORS = ["#4f8ef7","#f7774f","#4ff7a0","#f7d44f","#c44ff7","#f74f8e","#4ff7f0","#ff9f43"]
THEME  = "plotly_dark"

def style(fig, height=380):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,12,28,0.6)",
        height=height,
        font=dict(family="Inter", color="#6a8aaa", size=12),
        margin=dict(l=10, r=20, t=30, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8899aa")),
        xaxis=dict(gridcolor="rgba(79,142,247,0.06)", linecolor="rgba(79,142,247,0.1)", tickfont=dict(color="#4a6a8a")),
        yaxis=dict(gridcolor="rgba(79,142,247,0.06)", linecolor="rgba(79,142,247,0.1)", tickfont=dict(color="#4a6a8a")),
    )
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>🌍 PopulationIQ</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#2a4060;font-size:12px;margin-bottom:20px;'>Market Expansion Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    selected_year    = st.slider("📅 Year", 1950, 2100, 2024)
    all_regions      = sorted(fact['Region'].dropna().unique().tolist())
    selected_regions = st.multiselect("🗺️ Region", all_regions, default=all_regions)
    selected_gender  = st.selectbox("👤 Gender", ["Both", "Male", "Female"])
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#1a3050;font-size:11px;line-height:1.8;'>📊 UN World Population Prospects<br>💰 World Bank GDP per Capita<br>🗓️ Coverage: 1950–2100<br>🌍 Countries: 201</div>", unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
df_y = fact[(fact['Year'] == selected_year) & (fact['Region'].isin(selected_regions))]
df_a = fact[fact['Region'].isin(selected_regions)]
if selected_gender != "Both":
    df_y = df_y[df_y['Gender'] == selected_gender]
    df_a = df_a[df_a['Gender'] == selected_gender]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding:16px 0 8px 0;'>
    <div class='page-title'>🌍 Global Market Expansion Dashboard</div>
    <div class='page-subtitle'>Data-driven country ranking for retail expansion &nbsp;·&nbsp; Population + Growth + GDP scoring model &nbsp;·&nbsp; Showing <b style='color:#4f8ef7'>{selected_year}</b></div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_pop   = df_y['Population'].sum()
top_country = top10.iloc[0]['country']
top_region  = df_y.groupby('Region')['Population'].sum().idxmax()
countries   = df_y['country'].nunique()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class='kpi-card' style='--accent-gradient:linear-gradient(90deg,#4f8ef7,#7b61ff);--glow-color:rgba(79,142,247,0.06);'>
        <span class='kpi-icon'>🌐</span>
        <div class='kpi-label'>World Population</div>
        <div class='kpi-value'>{total_pop/1e9:.2f}B</div>
        <div class='kpi-sub'>▲ in {selected_year}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class='kpi-card' style='--accent-gradient:linear-gradient(90deg,#f7774f,#f7d44f);--glow-color:rgba(247,119,79,0.06);'>
        <span class='kpi-icon'>🏆</span>
        <div class='kpi-label'>Top Expansion Target</div>
        <div class='kpi-value' style='font-size:22px;'>{top_country}</div>
        <div class='kpi-sub'>highest market score</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class='kpi-card' style='--accent-gradient:linear-gradient(90deg,#4ff7a0,#4ff7f0);--glow-color:rgba(79,247,160,0.06);'>
        <span class='kpi-icon'>🗺️</span>
        <div class='kpi-label'>Leading Region</div>
        <div class='kpi-value' style='font-size:22px;'>{top_region}</div>
        <div class='kpi-sub'>highest population</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class='kpi-card' style='--accent-gradient:linear-gradient(90deg,#c44ff7,#f74f8e);--glow-color:rgba(196,79,247,0.06);'>
        <span class='kpi-icon'>🌍</span>
        <div class='kpi-label'>Countries Tracked</div>
        <div class='kpi-value'>{countries}</div>
        <div class='kpi-sub'>across all regions</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

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
    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>MARKET INTELLIGENCE</div>
        <div class='section-title'>Top 10 Countries for Retail Expansion</div>
        <div class='section-sub'>Score = 40% Population Size + 40% Growth (2024→2050) + 20% GDP per Capita · All factors normalized 0–1</div>
    </div>""", unsafe_allow_html=True)

    r1, r2 = st.columns([1.2, 0.8])
    with r1:
        colors = [f"rgba(79,142,247,{0.4 + i*0.06})" for i in range(10)]
        fig = go.Figure(go.Bar(
            x=top10['Final_Score'],
            y=top10['country'],
            orientation='h',
            text=top10['Final_Score'].round(3),
            textposition='outside',
            marker=dict(
                color=top10['Final_Score'],
                colorscale=[[0,'#0d2550'],[0.5,'#2a5aaa'],[1,'#4f8ef7']],
                line=dict(color='rgba(79,142,247,0.3)', width=1)
            )
        ))
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(style(fig, 440), use_container_width=True)

    with r2:
        display_cols  = ['Rank', 'country', 'Region', 'Population_2024', 'Growth_Rate', 'GDP_Per_Capita', 'Final_Score']
        top10_display = top10[display_cols].copy()
        top10_display['Population_2024'] = (top10_display['Population_2024'] / 1e6).round(1).astype(str) + 'M'
        top10_display['Growth_Rate']     = (top10_display['Growth_Rate'] * 100).round(1).astype(str) + '%'
        top10_display['GDP_Per_Capita']  = '$' + top10_display['GDP_Per_Capita'].round(0).astype(int).astype(str)
        top10_display['Final_Score']     = top10_display['Final_Score'].round(3).astype(str)
        top10_display.columns            = ['#', 'Country', 'Region', 'Population', 'Growth', 'GDP/capita', 'Score']
        st.dataframe(top10_display, use_container_width=True, hide_index=True, height=440)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>FULL RANKINGS</div>
        <div class='section-title'>All 185 Countries Ranked</div>
    </div>""", unsafe_allow_html=True)
    full_display = score_df[['Rank', 'country', 'Region', 'Population_2024', 'Growth_Rate', 'GDP_Per_Capita', 'Final_Score']].copy()
    full_display['Population_2024'] = (full_display['Population_2024'] / 1e6).round(1).astype(str) + 'M'
    full_display['Growth_Rate']     = (full_display['Growth_Rate'] * 100).round(1).astype(str) + '%'
    full_display['GDP_Per_Capita']  = '$' + full_display['GDP_Per_Capita'].round(0).astype(int).astype(str)
    full_display['Final_Score']     = full_display['Final_Score'].round(3).astype(str)
    full_display.columns            = ['#', 'Country', 'Region', 'Population', 'Growth', 'GDP/capita', 'Score']
    st.dataframe(full_display, use_container_width=True, hide_index=True, height=400)

# ─── TAB 2 — POPULATION TRENDS ───────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>GLOBAL TREND</div>
        <div class='section-title'>World Population 1950–2100</div>
        <div class='section-sub'>Blue = historical · Orange dashed = UN projections beyond 2024</div>
    </div>""", unsafe_allow_html=True)

    trend = df_a.groupby('Year')['Population'].sum().reset_index()
    fig2  = go.Figure()
    fig2.add_trace(go.Scatter(
        x=trend[trend['Year'] <= 2024]['Year'],
        y=trend[trend['Year'] <= 2024]['Population'],
        name='Historical', line=dict(color='#4f8ef7', width=3),
        fill='tozeroy', fillcolor='rgba(79,142,247,0.07)'
    ))
    fig2.add_trace(go.Scatter(
        x=trend[trend['Year'] >= 2024]['Year'],
        y=trend[trend['Year'] >= 2024]['Population'],
        name='Projected', line=dict(color='#f7774f', width=3, dash='dash'),
        fill='tozeroy', fillcolor='rgba(247,119,79,0.07)'
    ))
    fig2.add_vline(x=2024, line_dash="dot", line_color="rgba(79,142,247,0.4)",
                   annotation_text="  Today", annotation_font_color="#4f8ef7")
    fig2.add_vline(x=selected_year, line_dash="solid", line_color="rgba(247,119,79,0.5)",
                   annotation_text=f"  {selected_year}", annotation_font_color="#f7774f")
    st.plotly_chart(style(fig2, 400), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class='section-header'>
            <div class='section-tag'>RANKINGS</div>
            <div class='section-title'>Top 10 Most Populous Countries</div>
        </div>""", unsafe_allow_html=True)
        top10_pop = df_y.groupby('country')['Population'].sum().reset_index().sort_values('Population', ascending=False).head(10)
        fig3 = px.bar(top10_pop, x='Population', y='country', orientation='h',
                      text='Population', color='Population',
                      color_continuous_scale=[[0,'#0d2550'],[0.5,'#2a5aaa'],[1,'#4f8ef7']],
                      template=THEME)
        fig3.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig3.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
        st.plotly_chart(style(fig3, 420), use_container_width=True)

    with c2:
        st.markdown("""
        <div class='section-header'>
            <div class='section-tag'>COMPARISON</div>
            <div class='section-title'>Country vs Country</div>
        </div>""", unsafe_allow_html=True)
        all_countries = sorted(fact['country'].dropna().unique().tolist())
        col1, col2    = st.columns(2)
        c1i = all_countries.index('India') if 'India' in all_countries else 0
        c2i = all_countries.index('China') if 'China' in all_countries else 1
        country1 = col1.selectbox("🔵 Country 1", all_countries, index=c1i)
        country2 = col2.selectbox("🟠 Country 2", all_countries, index=c2i)
        compare  = df_a[df_a['country'].isin([country1, country2])].groupby(['Year','country'])['Population'].sum().reset_index()
        fig_cmp  = px.line(compare, x='Year', y='Population', color='country',
                           color_discrete_sequence=['#4f8ef7','#f7774f'], template=THEME)
        fig_cmp.add_vline(x=2024, line_dash="dot", line_color="rgba(79,142,247,0.4)")
        st.plotly_chart(style(fig_cmp, 360), use_container_width=True)

# ─── TAB 3 — REGION ANALYSIS ─────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>REGION BREAKDOWN</div>
        <div class='section-title'>Population by Region</div>
    </div>""", unsafe_allow_html=True)

    region_pop = df_y.groupby('Region')['Population'].sum().reset_index().sort_values('Population', ascending=False)
    c1, c2 = st.columns(2)
    with c1:
        fig4 = px.pie(region_pop, names='Region', values='Population',
                      color_discrete_sequence=COLORS, hole=0.55, template=THEME)
        fig4.update_traces(textposition='outside', textinfo='label+percent',
                           marker=dict(line=dict(color='rgba(0,0,0,0.3)', width=2)))
        fig4.update_layout(showlegend=False)
        st.plotly_chart(style(fig4, 420), use_container_width=True)
    with c2:
        fig5 = px.bar(region_pop, x='Region', y='Population', text='Population',
                      color='Region', color_discrete_sequence=COLORS, template=THEME)
        fig5.update_traces(texttemplate='%{text:,.0f}', textposition='outside',
                           marker=dict(line=dict(color='rgba(0,0,0,0.2)', width=1)))
        fig5.update_layout(showlegend=False)
        st.plotly_chart(style(fig5, 420), use_container_width=True)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>OVER TIME</div>
        <div class='section-title'>Region Population Growth 1950–2100</div>
    </div>""", unsafe_allow_html=True)
    region_trend = df_a.groupby(['Year','Region'])['Population'].sum().reset_index()
    fig6 = px.line(region_trend, x='Year', y='Population', color='Region',
                   color_discrete_sequence=COLORS, template=THEME)
    fig6.add_vline(x=2024, line_dash="dot", line_color="rgba(79,142,247,0.4)")
    st.plotly_chart(style(fig6, 420), use_container_width=True)

    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>MILESTONES</div>
        <div class='section-title'>Region Share at Key Years</div>
    </div>""", unsafe_allow_html=True)
    region_milestone = fact[fact['Year'].isin([1950,2000,2024,2050,2100])].groupby(['Year','Region'])['Population'].sum().reset_index()
    fig6b = px.bar(region_milestone, x='Year', y='Population', color='Region',
                   color_discrete_sequence=COLORS, barmode='stack', template=THEME)
    fig6b.update_layout(xaxis=dict(tickmode='array', tickvals=[1950,2000,2024,2050,2100]))
    st.plotly_chart(style(fig6b, 420), use_container_width=True)

# ─── TAB 4 — GENDER ANALYSIS ─────────────────────────────────────────────────
with tab4:
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("""
        <div class='section-header'>
            <div class='section-tag'>GLOBAL SPLIT</div>
            <div class='section-title'>Male vs Female Population</div>
        </div>""", unsafe_allow_html=True)
        gender_pop = df_y.groupby('Gender')['Population'].sum().reset_index()
        fig7 = px.pie(gender_pop, names='Gender', values='Population',
                      color_discrete_sequence=['#4f8ef7','#f74f8e'], hole=0.6, template=THEME)
        fig7.update_traces(textposition='outside', textinfo='label+percent',
                           marker=dict(line=dict(color='rgba(0,0,0,0.3)', width=2)))
        fig7.update_layout(showlegend=False)
        st.plotly_chart(style(fig7, 380), use_container_width=True)
    with g2:
        st.markdown("""
        <div class='section-header'>
            <div class='section-tag'>BY REGION</div>
            <div class='section-title'>Gender by Region</div>
        </div>""", unsafe_allow_html=True)
        gender_region = df_y.groupby(['Region','Gender'])['Population'].sum().reset_index()
        fig8 = px.bar(gender_region, x='Region', y='Population', color='Gender',
                      color_discrete_sequence=['#4f8ef7','#f74f8e'], barmode='group', template=THEME)
        fig8.update_layout(legend=dict(orientation='h', y=1.1))
        st.plotly_chart(style(fig8, 380), use_container_width=True)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>OVER TIME</div>
        <div class='section-title'>Gender Ratio 1950–2100</div>
    </div>""", unsafe_allow_html=True)
    gender_trend = df_a.groupby(['Year','Gender'])['Population'].sum().reset_index()
    fig9 = px.line(gender_trend, x='Year', y='Population', color='Gender',
                   color_discrete_sequence=['#4f8ef7','#f74f8e'], template=THEME)
    fig9.add_vline(x=2024, line_dash="dot", line_color="rgba(79,142,247,0.4)")
    st.plotly_chart(style(fig9, 400), use_container_width=True)

# ─── TAB 5 — AGE ANALYSIS ────────────────────────────────────────────────────
with tab5:
    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>AGE DISTRIBUTION</div>
        <div class='section-title'>Population by Age Group</div>
    </div>""", unsafe_allow_html=True)
    age_pop = df_y.groupby('Age Group')['Population'].sum().reset_index().sort_values('Population', ascending=False)
    fig10 = px.bar(age_pop, x='Age Group', y='Population', text='Population',
                   color='Population',
                   color_continuous_scale=[[0,'#0a1a40'],[0.4,'#1a4a9e'],[0.7,'#4f8ef7'],[1,'#7b61ff']],
                   template=THEME)
    fig10.update_traces(texttemplate='%{text:,.0f}', textposition='outside',
                        marker=dict(line=dict(color='rgba(79,142,247,0.2)', width=1)))
    fig10.update_layout(coloraxis_showscale=False)
    st.plotly_chart(style(fig10, 420), use_container_width=True)

    a1, a2 = st.columns(2)
    with a1:
        st.markdown("""
        <div class='section-header'>
            <div class='section-tag'>CATEGORIES</div>
            <div class='section-title'>Age Category Split</div>
        </div>""", unsafe_allow_html=True)
        age_cat = df_y.groupby('Age Category')['Population'].sum().reset_index()
        fig11 = px.pie(age_cat, names='Age Category', values='Population',
                       color_discrete_sequence=COLORS, hole=0.55, template=THEME)
        fig11.update_traces(textposition='outside', textinfo='label+percent',
                            marker=dict(line=dict(color='rgba(0,0,0,0.3)', width=2)))
        fig11.update_layout(showlegend=False)
        st.plotly_chart(style(fig11, 400), use_container_width=True)
    with a2:
        st.markdown("""
        <div class='section-header'>
            <div class='section-tag'>BY REGION</div>
            <div class='section-title'>Age Category by Region</div>
        </div>""", unsafe_allow_html=True)
        age_region = df_y.groupby(['Region','Age Category'])['Population'].sum().reset_index()
        fig12 = px.bar(age_region, x='Region', y='Population', color='Age Category',
                       color_discrete_sequence=COLORS, barmode='stack', template=THEME)
        fig12.update_layout(legend=dict(orientation='h', y=1.1))
        st.plotly_chart(style(fig12, 400), use_container_width=True)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='section-header'>
        <div class='section-tag'>AGEING TREND</div>
        <div class='section-title'>Is the World Getting Older?</div>
        <div class='section-sub'>Age category trends from 1950 to 2100</div>
    </div>""", unsafe_allow_html=True)
    age_trend = df_a.groupby(['Year','Age Category'])['Population'].sum().reset_index()
    fig13 = px.line(age_trend, x='Year', y='Population', color='Age Category',
                    color_discrete_sequence=COLORS, template=THEME)
    fig13.add_vline(x=2024, line_dash="dot", line_color="rgba(79,142,247,0.4)")
    st.plotly_chart(style(fig13, 420), use_container_width=True)
