import base64
import os
import sys
import subprocess
from datetime import datetime
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    import plotly.express as px
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.graph_objects as go
    import plotly.express as px


RISK_COLOR_MAP = {
    "Crítico": "#E9494A",
    "Alto": "#F28C28",
    "Médio": "#F2C94C",
    "Baixo": "#37C978"
}

RISK_ORDER = ["Crítico", "Alto", "Médio", "Baixo"]

RISK_LABELS = {
    "Crítico": "Crítico",
    "Alto": "Alto",
    "Médio": "Médio",
    "Baixo": "Baixo"
}

STATUS_COLOR_MAP = {
    "Em Andamento": "#3AA7FF",
    "Planejamento": "#74D94A",
    "Contratado": "#FFB020",
    "Concluído": "#8D55FF",
    "Concluido": "#8D55FF"
}

st.set_page_config(
    page_title="CapexVision V23.3.1",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
html, body, [class*="css"] {font-family: Inter, Segoe UI, Arial, sans-serif;}
.stApp {
    background:
      radial-gradient(circle at top left, rgba(33,82,130,.32), transparent 27%),
      linear-gradient(135deg, #06111F 0%, #040B15 55%, #02060C 100%);
    color:#EAF2FF;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06101D 0%, #020811 100%);
    border-right: 1px solid rgba(99,153,210,.25);
    min-width: 250px;
}
[data-testid="stSidebar"] * {color: #DCEBFF;}
.block-container {padding: 0.75rem 1rem 1rem 1rem; max-width: 1920px;}
div[data-testid="stVerticalBlock"] {gap: 0.58rem;}
div[data-testid="column"] {padding-left: 0.25rem !important; padding-right: 0.25rem !important;}
.stSelectbox label, .stTextInput label, .stMultiSelect label {
    color: #D8E7FA !important; font-size: 0.73rem !important; font-weight: 850 !important;
}
.stSelectbox > div > div, .stTextInput > div > div > input, .stMultiSelect > div {
    background: linear-gradient(135deg, rgba(13,31,53,.95), rgba(8,20,35,.95)) !important;
    border: 1px solid rgba(110,170,255,.20) !important;
    border-radius: 12px !important;
    color: #F5FAFF !important;
}
button[kind="secondary"] {
    background: linear-gradient(135deg, rgba(13,31,53,.95), rgba(8,20,35,.95)) !important;
    border: 1px solid rgba(0,198,255,.25) !important;
    color: #40BFFF !important;
    border-radius: 12px !important;
    font-weight: 850 !important;
}
.brand-wrap {padding: 12px 4px 16px 4px; border-bottom: 1px solid rgba(255,255,255,.10); margin-bottom: 10px;}
.brand {display:flex; gap:12px; align-items:center;}
.logo {
    width:46px;height:46px;border-radius:12px;background:linear-gradient(135deg,#00C6FF,#7B61FF);
    display:flex;align-items:center;justify-content:center;font-size:25px;box-shadow:0 0 25px rgba(0,198,255,.40);
}
.brand-title {font-size:1.54rem;font-weight:950;color:#fff;line-height:1;letter-spacing:.2px;}
.brand-sub {font-size:.70rem;color:#B2C7DE;letter-spacing:1px;margin-top:4px;font-weight:750;}
.user-box {
    background: linear-gradient(135deg, rgba(17,47,83,.95), rgba(10,26,47,.96));
    border: 1px solid rgba(110,170,255,.18); border-radius: 14px; padding: 12px; margin: 12px 0;
    display: flex; gap: 10px; align-items: center;
}
.avatar {width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#1667E8,#46A6FF);display:flex;align-items:center;justify-content:center;font-size:22px;}
.user-title {font-weight:850;font-size:.88rem;}
.user-sub {font-size:.72rem;color:#9EB4CD;}
.footer-brand {position: fixed; bottom: 16px; left: 16px; color: #8FA7C4; font-size: .76rem;}
.header {
    background: linear-gradient(135deg, rgba(13,31,53,.98), rgba(9,22,39,.98));
    border: 1px solid rgba(90,160,255,.20); border-radius: 18px; padding: 13px 18px;
    box-shadow: 0 18px 45px rgba(0,0,0,.34);
}
.header-title {font-size:1.53rem;font-weight:950;color:white;line-height:1.1;}
.header-sub {font-size:.84rem;color:#9DB5CF;margin-top:2px;}
.update {color:#AFC3DC;font-size:.82rem;text-align:right;border-left:1px solid rgba(255,255,255,.16);padding-left:18px;}
.kpi {
    position:relative;overflow:hidden;border-radius:18px;padding:17px 18px;
    border:1px solid rgba(255,255,255,.10);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.06), 0 18px 38px rgba(0,0,0,.32);
    height:126px;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.kpi:hover {
    transform: translateY(-3px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 24px 50px rgba(0,0,0,.42), 0 0 24px rgba(0,198,255,.12);
    border-color: rgba(0,198,255,.35);
}
.kpi-title {font-size:.735rem;color:rgba(255,255,255,.80);font-weight:850;text-transform:uppercase;}
.kpi-value {font-size:1.70rem;font-weight:950;color:white;margin-top:13px;}
.kpi-sub {font-size:.79rem;color:rgba(255,255,255,.76);margin-top:6px;}
.kpi-icon {position:absolute;right:18px;bottom:16px;font-size:3.1rem;opacity:.22;}
.blue{background:linear-gradient(135deg,#0C3A68,#0A2342)}
.green{background:linear-gradient(135deg,#0F653A,#0A3021)}
.orange{background:linear-gradient(135deg,#A35418,#3B1E0E)}
.purple{background:linear-gradient(135deg,#5625A6,#21103F)}
.cyan{background:linear-gradient(135deg,#055D7C,#092337)}
.panel {
    background: linear-gradient(135deg, rgba(13,31,53,.95), rgba(8,20,35,.96));
    border: 1px solid rgba(110,170,255,.18);
    border-radius: 18px; padding: 13px;
    box-shadow: 0 18px 40px rgba(0,0,0,.34);
    transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
.panel:hover {
    border-color: rgba(0,198,255,.28);
    box-shadow: 0 22px 52px rgba(0,0,0,.42), 0 0 18px rgba(0,198,255,.09);
}
.panel.h-250 {height:250px; overflow:hidden;}
.panel.h-332 {height:332px; overflow:hidden;}
.panel.h-520 {height:520px; overflow:hidden;}
.ptitle {font-weight:950;font-size:.89rem;text-transform:uppercase;color:#F1F7FF;margin-bottom:3px;}
.psub {font-size:.72rem;color:#8FA7C4;margin-bottom:7px;}
.alert-row {
    display:flex; justify-content:space-between; align-items:center;
    padding: 8.8px 0; border-bottom: 1px solid rgba(255,255,255,.08);
    color:#DCEBFF; font-size:.80rem;
}
.badge {padding:5px 12px;border-radius:10px;color:white;font-weight:950;min-width:36px;text-align:center;}
.red{background:#E9494A}.amber{background:#F28C28}.yellow{background:#F2C94C;color:#17202A}.ok{background:#37C978}
.story {background:rgba(255,255,255,.045);border-left:4px solid #00C6FF;border-radius:12px;padding:13px 15px;color:#DCEBFF;line-height:1.45;}
.note-grid {display:grid;grid-template-columns: repeat(8, minmax(110px, 1fr));gap:9px;}
.note {
    border-radius:13px;padding:10px 11px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.10);
    min-height:112px;transition: transform .18s ease, background .18s ease;
}
.note:hover {transform: translateY(-2px); background:rgba(255,255,255,.065);}
.note:nth-child(1){border-color:#635BFF}.note:nth-child(2){border-color:#3AA7FF}.note:nth-child(3){border-color:#65D64F}.note:nth-child(4){border-color:#65D64F}.note:nth-child(5){border-color:#FF7A00}.note:nth-child(6){border-color:#8D55FF}.note:nth-child(7){border-color:#00C6FF}.note:nth-child(8){border-color:#FF7A00}
.ntitle {font-size:.80rem;font-weight:950;color:white;}
.ntext {font-size:.68rem;color:#B7C7DC;margin-top:7px;line-height:1.34;}
.tip {background:linear-gradient(135deg,#123C62,#0B2036);border:1px solid rgba(0,198,255,.25);border-radius:18px;padding:17px;height:154px;box-shadow:0 0 24px rgba(0,198,255,.08);}
.neg{color:#FF5F57;font-weight:950}.pos{color:#66E38A;font-weight:950}
.top-table {width:100%;border-collapse:collapse;color:#DCEBFF;font-size:.77rem;}
.top-table th {color:#9FB4D0;text-align:left;padding:7px 6px;border-bottom:1px solid rgba(255,255,255,.14);font-weight:850;}
.top-table td {padding:8px 6px;border-bottom:1px solid rgba(255,255,255,.07);}
.top-table tr:hover td {background:rgba(255,255,255,.035);}
.floor {
    position:relative;height:270px;background:
      radial-gradient(circle at 30% 45%, rgba(0,198,255,.13), transparent 24%),
      linear-gradient(135deg,#132A45,#0A1729);
    border:1px solid rgba(255,255,255,.12);border-radius:16px;overflow:hidden;
}
.zone{position:absolute;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.05);border-radius:10px}
.hot{position:absolute;width:16px;height:16px;border-radius:50%;background:#47E46E;box-shadow:0 0 0 6px rgba(71,228,110,.18),0 0 22px rgba(71,228,110,.95);animation:pulseGreen 2s infinite;}
.hot.o{background:#FFB020;box-shadow:0 0 0 6px rgba(255,176,32,.18),0 0 22px rgba(255,176,32,.95);animation:pulseOrange 2s infinite;}
@keyframes pulseGreen {0%{box-shadow:0 0 0 0 rgba(71,228,110,.45),0 0 22px rgba(71,228,110,.95)}70%{box-shadow:0 0 0 12px rgba(71,228,110,0),0 0 22px rgba(71,228,110,.75)}100%{box-shadow:0 0 0 0 rgba(71,228,110,0),0 0 22px rgba(71,228,110,.95)}}
@keyframes pulseOrange {0%{box-shadow:0 0 0 0 rgba(255,176,32,.45),0 0 22px rgba(255,176,32,.95)}70%{box-shadow:0 0 0 12px rgba(255,176,32,0),0 0 22px rgba(255,176,32,.75)}100%{box-shadow:0 0 0 0 rgba(255,176,32,0),0 0 22px rgba(255,176,32,.95)}}
.call{position:absolute;background:rgba(10,24,42,.96);border:1px solid rgba(71,228,110,.55);border-radius:10px;padding:7px 9px;color:#DCEBFF;font-size:.67rem;line-height:1.26;box-shadow:0 10px 26px rgba(0,0,0,.45)}
.call.o{border-color:rgba(255,176,32,.65)}
div[role="radiogroup"] label {padding: 9px 6px !important;border-radius: 10px !important;}
div[role="radiogroup"] label:hover {background: rgba(25,110,255,.16) !important;}

/* V19 correction: Plotly charts live inside native Streamlit bordered containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(135deg, rgba(13,31,53,.95), rgba(8,20,35,.96)) !important;
    border: 1px solid rgba(110,170,255,.18) !important;
    border-radius: 18px !important;
    box-shadow: 0 18px 40px rgba(0,0,0,.34) !important;
    padding: 12px !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(0,198,255,.28) !important;
    box-shadow: 0 22px 52px rgba(0,0,0,.42), 0 0 18px rgba(0,198,255,.09) !important;
}



.top5-panel{
    width:100%;
    padding-top:4px;
}
.top5-table{
    width:100%;
    border-collapse:collapse;
    table-layout:fixed;
}
.top5-table thead th{
    color:#A8BED8;
    font-size:.70rem;
    font-weight:800;
    text-align:left;
    padding:8px 8px 10px 8px;
    border-bottom:1px solid rgba(255,255,255,.10);
}
.top5-table tbody td{
    color:#E7F0FA;
    font-size:.77rem;
    padding:11px 8px;
    border-bottom:1px solid rgba(255,255,255,.06);
    vertical-align:middle;
}
.top5-table tbody tr:hover td{
    background:rgba(255,255,255,.03);
}
.top5-project{
    width:42%;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}
.top5-money{
    width:18%;
    text-align:left;
    white-space:nowrap;
}
.top5-var{
    width:14%;
    text-align:left;
    white-space:nowrap;
    color:#FF5F57 !important;
    font-weight:900;
}
.top5-pct{
    width:10%;
    text-align:right;
    white-space:nowrap;
    color:#FF5F57 !important;
    font-weight:900;
}
.top5-cta{
    width:100%;
    text-align:center;
    color:#3AA7FF;
    font-size:.76rem;
    font-weight:900;
    letter-spacing:.3px;
    padding-top:14px;
}



.floor-img {
    position:relative;
    height:270px;
    border:1px solid rgba(255,255,255,.12);
    border-radius:16px;
    overflow:hidden;
    background-size: cover;
    background-position: center;
    background-repeat:no-repeat;
}
.floor-img::before{
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(135deg, rgba(3,10,20,.28), rgba(3,10,20,.52));
    z-index:0;
}
.floor-empty-label{
    position:absolute;
    z-index:2;
    left:50%;
    top:50%;
    transform:translate(-50%,-50%);
    color:#B7C7DC;
    text-align:center;
    font-size:.78rem;
    background:rgba(4,12,24,.65);
    border:1px solid rgba(255,255,255,.12);
    border-radius:12px;
    padding:12px 16px;
}


.project-card{
    background:linear-gradient(135deg, rgba(13,31,53,.96), rgba(8,20,35,.98));
    border:1px solid rgba(110,170,255,.18);
    border-radius:18px;
    padding:16px;
    box-shadow:0 18px 40px rgba(0,0,0,.34);
}
.project-title{font-size:1.25rem;font-weight:950;color:#F3F8FF;}
.project-sub{color:#9DB5CF;font-size:.82rem;margin-top:4px;}
.risk-pill{display:inline-block;border-radius:999px;padding:6px 12px;color:white;font-weight:900;font-size:.76rem;}
.risk-Crítico{background:#E9494A;}
.risk-Alto{background:#F28C28;}
.risk-Médio{background:#F2C94C;color:#17202A;}
.risk-Baixo{background:#37C978;color:#06111F;}
.insight-box{
    background:rgba(255,255,255,.045);
    border-left:4px solid #00C6FF;
    border-radius:12px;
    padding:14px 16px;
    color:#DCEBFF;
    line-height:1.48;
    font-size:.88rem;
}
.metric-mini{
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.10);
    border-radius:14px;
    padding:12px;
    min-height:88px;
}
.metric-mini-title{font-size:.70rem;color:#9DB5CF;font-weight:800;text-transform:uppercase;}
.metric-mini-value{font-size:1.15rem;color:#F3F8FF;font-weight:950;margin-top:8px;}


.exec-card{
    background:linear-gradient(135deg, rgba(13,31,53,.96), rgba(8,20,35,.98));
    border:1px solid rgba(110,170,255,.18);
    border-radius:18px;
    padding:16px;
    box-shadow:0 18px 40px rgba(0,0,0,.34);
    min-height:132px;
}
.exec-title{color:#F3F8FF;font-size:.82rem;font-weight:950;text-transform:uppercase;}
.exec-value{color:#FFFFFF;font-size:1.58rem;font-weight:950;margin-top:10px;}
.exec-sub{color:#9DB5CF;font-size:.74rem;margin-top:6px;line-height:1.35;}
.insight-item{background:rgba(255,255,255,.045);border-radius:12px;padding:12px 14px;margin-bottom:10px;color:#DCEBFF;font-size:.84rem;line-height:1.42;}
.insight-critical{border-left:4px solid #E9494A;}
.insight-high{border-left:4px solid #F28C28;}
.insight-medium{border-left:4px solid #F2C94C;}
.insight-low{border-left:4px solid #37C978;}
.rule-box{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.10);border-radius:14px;padding:13px;margin-bottom:10px;color:#DCEBFF;font-size:.82rem;}
.company-tag{display:inline-block;border-radius:999px;padding:5px 10px;background:rgba(58,167,255,.14);color:#7CC7FF;border:1px solid rgba(58,167,255,.25);font-size:.72rem;font-weight:900;margin:3px;}


.floor-img-company {
    position:relative;
    height:270px;
    border:1px solid rgba(255,255,255,.12);
    border-radius:16px;
    overflow:hidden;
    background-size: contain;
    background-position: center;
    background-repeat:no-repeat;
    background-color:#071321;
}
.floor-img-company::before{
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(135deg, rgba(3,10,20,.08), rgba(3,10,20,.28));
    z-index:0;
    pointer-events:none;
}
.config-help{
    font-size:.72rem;
    color:#9DB5CF;
    line-height:1.35;
    margin-top:2px;
    margin-bottom:12px;
}
.param-section-title{
    color:#F3F8FF;
    font-weight:900;
    font-size:.86rem;
    margin:10px 0 8px 0;
}


/* V23.3 - contraste reforçado para legendas, tabs, sliders e textos */
.js-plotly-plot .legend text,
.js-plotly-plot .gtitle,
.js-plotly-plot .xtick text,
.js-plotly-plot .ytick text,
.js-plotly-plot .cbaxis text,
.js-plotly-plot text {
    fill: #EAF2FF !important;
    color: #EAF2FF !important;
    opacity: 1 !important;
}
button[data-baseweb="tab"] {
    color: #DCEBFF !important;
    opacity: 1 !important;
    font-weight: 850 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom-color: #FF4D5A !important;
}
.stSlider label,
.stSlider [data-testid="stMarkdownContainer"],
.stSlider div,
.stSlider span,
label,
.stSelectbox label,
.stTextInput label,
.stNumberInput label,
.stTextArea label {
    color: #DCEBFF !important;
    opacity: 1 !important;
    font-weight: 800 !important;
}
.config-help {
    color: #BFD1E8 !important;
    opacity: 1 !important;
}
.legend-chip-row{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    margin:6px 0 12px 0;
}
.legend-chip{
    display:inline-flex;
    align-items:center;
    gap:7px;
    padding:5px 9px;
    border-radius:999px;
    background:rgba(255,255,255,.075);
    border:1px solid rgba(255,255,255,.16);
    color:#EAF2FF;
    font-size:.74rem;
    font-weight:850;
}
.legend-dot{
    width:10px;
    height:10px;
    border-radius:50%;
    display:inline-block;
}

</style>
""", unsafe_allow_html=True)






def render_risk_legend_custom(title="Legenda de risco"):
    html = f"""
    <div style="color:#EAF2FF;font-weight:900;font-size:.76rem;margin-top:4px;">{title}</div>
    <div class="legend-chip-row">
        <span class="legend-chip"><span class="legend-dot" style="background:#E9494A;"></span>Crítico</span>
        <span class="legend-chip"><span class="legend-dot" style="background:#F28C28;"></span>Alto</span>
        <span class="legend-chip"><span class="legend-dot" style="background:#F2C94C;"></span>Médio</span>
        <span class="legend-chip"><span class="legend-dot" style="background:#37C978;"></span>Baixo</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_indicator_legend_custom():
    html = """
    <div style="color:#EAF2FF;font-weight:900;font-size:.76rem;margin-top:4px;">Legenda dos indicadores</div>
    <div class="legend-chip-row">
        <span class="legend-chip"><span class="legend-dot" style="background:#2F80ED;"></span>Orçado</span>
        <span class="legend-chip"><span class="legend-dot" style="background:#7CC7FF;"></span>Realizado</span>
        <span class="legend-chip"><span class="legend-dot" style="background:#FF4D5A;"></span>Comprometido</span>
        <span class="legend-chip"><span class="legend-dot" style="background:#F5A3AD;"></span>Saldo</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def default_engine_params():
    return {
        "risk_cpi_yellow": 0.90,
        "risk_cpi_red": 0.80,
        "risk_spi_yellow": 0.90,
        "risk_spi_red": 0.80,
        "risk_vac_yellow_pct": -0.05,
        "risk_vac_red_pct": -0.10,
        "health_weight_cpi": 25,
        "health_weight_spi": 25,
        "health_weight_vac": 20,
        "health_weight_forecast": 15,
        "health_weight_data_quality": 15,
        "maturity_weight_budget": 20,
        "maturity_weight_schedule": 20,
        "maturity_weight_physical_progress": 20,
        "maturity_weight_cost_performance": 20,
        "maturity_weight_forecast": 20,
        "capex_min_value": 1000000,
        "capex_opex_keywords": "manutenção,reparo,adequação,correção,conserto",
        "capex_payback_limit_months": 12,
        "whatif_default_budget_cut_pct": 10,
        "whatif_default_delay_months": 3,
        "whatif_default_fx_cost_pct": 8,
        "forecast_model": "Híbrido",
        "roi_weight_health": 45,
        "roi_weight_maturity": 25,
        "roi_weight_risk": 30,
        "esg_keyword_bonus": 30,
        "data_quality_required_fields": "empresa,definicao_projeto,elemento_pep,orcamento_aprovado_total,realizado,responsavel,avanco_planejado_pct,avanco_real_pct"
    }

if "engine_params" not in st.session_state:
    st.session_state.engine_params = default_engine_params()

if "company_floorplan_images" not in st.session_state:
    st.session_state.company_floorplan_images = {}

if "company_floorplan_names" not in st.session_state:
    st.session_state.company_floorplan_names = {}

if "analytics_audit_log" not in st.session_state:
    st.session_state.analytics_audit_log = []

if "floorplan_images" not in st.session_state:
    st.session_state.floorplan_images = {}
if "floorplan_names" not in st.session_state:
    st.session_state.floorplan_names = {}

if "raw_data" not in st.session_state:
    st.session_state.raw_data = None
if "load_log" not in st.session_state:
    st.session_state.load_log = []

def fmt(v):
    v=float(v) if pd.notna(v) else 0
    if abs(v)>=1e9: return f"R$ {v/1e9:,.2f} BI".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(v)>=1e6: return f"R$ {v/1e6:,.0f} MI".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(v)>=1e3: return f"R$ {v/1e3:,.0f} MIL".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def num(x): return pd.to_numeric(x, errors="coerce").fillna(0)

def normalize(df):
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ","_").replace("-","_") for c in df.columns]
    return df

def demo_data():
    np.random.seed(17)
    n=48
    real=pd.DataFrame({
        "empresa":["4000"]*n,
        "definicao_projeto":[f"PRJ-{100+i:03d}" for i in range(n)],
        "elemento_pep":[f"PRJ-{100+i:03d}-WBS-{i%4+1:02d}" for i in range(n)],
        "valor_moeda_objeto":np.random.randint(900000,18000000,n),
        "data_lancamento":pd.date_range("2024-01-01", periods=n, freq="7D")
    })
    bud=pd.DataFrame({
        "empresa":["4000"]*n,
        "definicao_projeto":real.definicao_projeto,
        "elemento_pep":real.elemento_pep,
        "orcamento_aprovado_total":real.valor_moeda_objeto*np.random.uniform(1.05,2.6,n),
        "orcamento_original":real.valor_moeda_objeto*np.random.uniform(1.0,2.2,n),
        "suplementacao":np.random.randint(0,1500000,n),
        "reducao":np.random.randint(0,700000,n)
    })
    comp=pd.DataFrame({
        "empresa":["4000"]*n,
        "definicao_projeto":real.definicao_projeto,
        "elemento_pep":real.elemento_pep,
        "valor_comprometido":real.valor_moeda_objeto*np.random.uniform(.1,.8,n)
    })
    cad=pd.DataFrame({
        "empresa":["4000"]*n,
        "definicao_projeto":real.definicao_projeto,
        "elemento_pep":real.elemento_pep,
        "nome_projeto":[f"Projeto Estratégico {i+1}" for i in range(n)],
        "area_responsavel":np.random.choice(["Área 01","Área 02","Área 03","Área 04"],n),
        "responsavel":np.random.choice(["Engenharia","Operações","Manutenção","Facilities"],n),
        "status_usuario":np.random.choice(["Em Andamento","Planejamento","Contratado","Concluído"],n),
        "data_inicio_planejada":pd.date_range("2024-01-01", periods=n, freq="5D"),
        "data_fim_planejada":pd.date_range("2024-08-01", periods=n, freq="6D")
    })
    av=pd.DataFrame({
        "empresa":["4000"]*n,
        "definicao_projeto":real.definicao_projeto,
        "elemento_pep":real.elemento_pep,
        "data_referencia":pd.date_range("2024-05-01", periods=n, freq="4D"),
        "avanco_planejado_pct":np.random.randint(35,95,n),
        "avanco_real_pct":np.random.randint(20,92,n)
    })
    return {"CJI3_REALIZADO":real,"ORCAMENTO":bud,"COMPROMETIDO":comp,"CADASTRO_PROJETOS_PEPS":cad,"AVANCO_FISICO":av}

def read_excel(uploaded):
    xls = pd.ExcelFile(uploaded)
    return {s: normalize(pd.read_excel(uploaded, sheet_name=s)) for s in xls.sheet_names}

def apply_load(new_data, mode):
    if st.session_state.raw_data is None or mode == "Substituir base":
        st.session_state.raw_data = new_data
    else:
        merged = dict(st.session_state.raw_data)
        for k,v in new_data.items():
            if k in merged:
                merged[k] = pd.concat([merged[k], v], ignore_index=True).drop_duplicates()
            else:
                merged[k] = v
        st.session_state.raw_data = merged
    st.session_state.load_log.append({"data_hora":datetime.now().strftime("%d/%m/%Y %H:%M"),"modo":mode,"abas":len(new_data)})

def build_summary(data):
    real = normalize(data.get("CJI3_REALIZADO", pd.DataFrame()))
    bud = normalize(data.get("ORCAMENTO", pd.DataFrame()))
    comp = normalize(data.get("COMPROMETIDO", pd.DataFrame()))
    cad = normalize(data.get("CADASTRO_PROJETOS_PEPS", pd.DataFrame()))
    av = normalize(data.get("AVANCO_FISICO", pd.DataFrame()))
    key=["empresa","definicao_projeto","elemento_pep"]
    if real.empty or bud.empty or not all(c in real.columns for c in key) or not all(c in bud.columns for c in key):
        return pd.DataFrame()
    real["valor_moeda_objeto"]=num(real.get("valor_moeda_objeto"))
    bud["orcamento_aprovado_total"]=num(bud.get("orcamento_aprovado_total"))
    if "orcamento_original" not in bud: bud["orcamento_original"]=bud["orcamento_aprovado_total"]
    if "suplementacao" not in bud: bud["suplementacao"]=0
    if "reducao" not in bud: bud["reducao"]=0
    bud["orcamento_original"]=num(bud["orcamento_original"]); bud["suplementacao"]=num(bud["suplementacao"]); bud["reducao"]=num(bud["reducao"])
    s=real.groupby(key)["valor_moeda_objeto"].sum().reset_index().rename(columns={"valor_moeda_objeto":"realizado"})
    b=bud.groupby(key)[["orcamento_aprovado_total","orcamento_original","suplementacao","reducao"]].sum().reset_index()
    s=s.merge(b,on=key,how="left")
    if not comp.empty and all(c in comp for c in key):
        comp["valor_comprometido"]=num(comp.get("valor_comprometido"))
        s=s.merge(comp.groupby(key)["valor_comprometido"].sum().reset_index(),on=key,how="left")
    else:
        s["valor_comprometido"]=0
    if not cad.empty and all(c in cad for c in key):
        keep=[c for c in key+["nome_projeto","area_responsavel","responsavel","status_usuario","data_inicio_planejada","data_fim_planejada"] if c in cad]
        s=s.merge(cad[keep].drop_duplicates(key),on=key,how="left")
    if not av.empty and all(c in av for c in key):
        av["avanco_planejado_pct"]=num(av.get("avanco_planejado_pct"))
        av["avanco_real_pct"]=num(av.get("avanco_real_pct"))
        s=s.merge(av.groupby(key)[["avanco_planejado_pct","avanco_real_pct"]].mean().reset_index(),on=key,how="left")
    for c in ["orcamento_aprovado_total","orcamento_original","suplementacao","reducao","valor_comprometido","avanco_planejado_pct","avanco_real_pct"]:
        if c not in s: s[c]=0
        s[c]=num(s[c])
    s["variacao_budget"]=s["orcamento_aprovado_total"]-s["orcamento_original"]
    s["saldo"]=s["orcamento_aprovado_total"]-s["realizado"]-s["valor_comprometido"]
    s["exposicao_pct"]=np.where(s["orcamento_aprovado_total"]>0,(s["realizado"]+s["valor_comprometido"])/s["orcamento_aprovado_total"],0)
    s["consumo_pct"]=np.where(s["orcamento_aprovado_total"]>0,s["realizado"]/s["orcamento_aprovado_total"],0)
    s["PV"]=s["orcamento_aprovado_total"]*s["avanco_planejado_pct"]/100
    s["EV"]=s["orcamento_aprovado_total"]*s["avanco_real_pct"]/100
    s["AC"]=s["realizado"]; s["BAC"]=s["orcamento_aprovado_total"]
    s["CPI"]=np.where(s["AC"]>0,s["EV"]/s["AC"],np.nan)
    s["SPI"]=np.where(s["PV"]>0,s["EV"]/s["PV"],np.nan)
    s["EAC"]=np.where((s["CPI"]>0)&pd.notna(s["CPI"]),s["BAC"]/s["CPI"],s["realizado"]+s["valor_comprometido"])
    s["ETC"]=s["EAC"]-s["AC"]
    s["VAC"]=s["BAC"]-s["EAC"]
    s["risk"]=np.select([s.exposicao_pct>=1,s.exposicao_pct>=.85,s.exposicao_pct>=.65],["Crítico","Alto","Médio"],"Baixo")
    score=100-np.where(s.exposicao_pct>=1,30,np.where(s.exposicao_pct>=.85,18,0))-np.where(s.VAC<0,20,0)-np.where(s.SPI<.9,12,0)-np.where(s.CPI<.9,12,0)
    s["health_score"]=np.clip(score,0,100).round()
    s["prob_estouro"]=(s["exposicao_pct"]*.55 + np.where(s["VAC"]<0,.25,0) + np.where(s["CPI"].fillna(1)<.9,.15,0)).clip(0,1)
    s["prob_atraso"]=(np.where(s["SPI"].fillna(1)<.9,.45,0)+np.where(s["avanco_real_pct"]<s["avanco_planejado_pct"],.35,0)).clip(0,1)
    coords=[(-23.55,-46.63),(-22.90,-43.20),(-12.97,-38.50),(-3.11,-60.02),(-1.45,-48.50),(-8.05,-34.90)]
    s["latitude"]=[coords[i%len(coords)][0] for i in range(len(s))]
    s["longitude"]=[coords[i%len(coords)][1] for i in range(len(s))]
    return s



def get_available_units(df_source):
    if "area_responsavel" in df_source.columns:
        units = sorted(
            [str(x) for x in df_source["area_responsavel"].dropna().unique().tolist()]
        )
        return units
    return []

def get_selected_floorplan_image(selected_unit, df_filtered):
    images = st.session_state.get("floorplan_images", {})

    if selected_unit and selected_unit != "Todas":
        return selected_unit, images.get(selected_unit)

    if "area_responsavel" in df_filtered.columns:
        for unit in df_filtered["area_responsavel"].dropna().astype(str).unique().tolist():
            if unit in images:
                return unit, images.get(unit)

    if images:
        first_unit = list(images.keys())[0]
        return first_unit, images[first_unit]

    return None, None

def add_risk_legend():
    st.markdown(
        """
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin:4px 0 10px 0;">
            <div style="font-size:.76rem;color:#DCEBFF;"><span style="color:#E9494A;font-size:1rem;">●</span> Crítico</div>
            <div style="font-size:.76rem;color:#DCEBFF;"><span style="color:#F28C28;font-size:1rem;">●</span> Alto</div>
            <div style="font-size:.76rem;color:#DCEBFF;"><span style="color:#F2C94C;font-size:1rem;">●</span> Médio</div>
            <div style="font-size:.76rem;color:#DCEBFF;"><span style="color:#37C978;font-size:1rem;">●</span> Baixo</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def prepare_gantt_data(df):
    gantt = df.copy()
    if "data_inicio_planejada" in gantt.columns:
        gantt["Inicio"] = pd.to_datetime(gantt["data_inicio_planejada"], errors="coerce")
    else:
        gantt["Inicio"] = pd.NaT
    if "data_fim_planejada" in gantt.columns:
        gantt["Fim"] = pd.to_datetime(gantt["data_fim_planejada"], errors="coerce")
    else:
        gantt["Fim"] = pd.NaT

    base_date = pd.Timestamp("2024-01-01")
    fallback_start = pd.Series([base_date + pd.Timedelta(days=int(i * 7)) for i in range(len(gantt))], index=gantt.index)
    gantt["Inicio"] = gantt["Inicio"].fillna(fallback_start)
    gantt["Fim"] = gantt["Fim"].fillna(gantt["Inicio"] + pd.to_timedelta(45 + (gantt.index % 90), unit="D"))

    gantt["Projeto"] = gantt["elemento_pep"].astype(str)
    gantt["Risco"] = gantt["risk"].astype(str)
    gantt["Avanço Planejado"] = gantt["avanco_planejado_pct"].fillna(0).round(1)
    gantt["Avanço Real"] = gantt["avanco_real_pct"].fillna(0).round(1)
    return gantt.sort_values(["Risco", "Inicio"]).head(40)

def kpi(title,value,sub,icon,cls):
    st.markdown(f'<div class="kpi {cls}"><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div><div class="kpi-icon">{icon}</div></div>',unsafe_allow_html=True)

def gauge(value,title,minv=0,maxv=1.5, height=126):
    fig=go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(value) if pd.notna(value) else 0,
        title={"text":title,"font":{"size":11,"color":"#B9CAE1"}},
        number={"font":{"size":18,"color":"#EAF2FF"}},
        gauge={
            "axis":{"range":[minv,maxv],"visible":False},
            "bar":{"color":"#F39C12"},
            "bgcolor":"rgba(255,255,255,.02)",
            "borderwidth":0,
            "steps":[
                {"range":[minv,.75],"color":"rgba(231,76,60,.80)"},
                {"range":[.75,1],"color":"rgba(243,156,18,.85)"},
                {"range":[1,maxv],"color":"rgba(46,204,113,.80)"}
            ],
            "threshold":{"line":{"color":"#FFFFFF","width":2},"thickness":0.75,"value":1}
        }
    ))
    fig.update_layout(height=height, margin=dict(l=0,r=0,t=24,b=0), paper_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
    return fig

def donut(s):
    vals=[s.realizado.sum(),s.valor_comprometido.sum(),max(s.saldo.sum(),0)]
    fig=go.Figure(go.Pie(
        labels=["Realizado (AC)","Comprometido","Saldo"],
        values=vals,
        hole=.70,
        marker=dict(colors=["#2F80ED","#65D64F","#8F98A3"]),
        textinfo="none"
    ))
    fig.update_layout(
        height=206,
        margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#EAF2FF",
        showlegend=True,
        legend=dict(orientation="v", y=0.55, x=0.78, font=dict(size=10, color="#DCEBFF"))
    )
    fig.add_annotation(text=f"{fmt(sum(vals))}<br>Total",x=.40,y=.50,showarrow=False,font=dict(size=14,color="#EAF2FF"))
    return fig


def floor(s, selected_unit="Todas", selected_company="Todas"):
    if isinstance(s, pd.DataFrame) and not s.empty:
        top = s.sort_values("orcamento_aprovado_total", ascending=False).head(8).reset_index(drop=True)
    else:
        top = pd.DataFrame()

    spots = [(18,68),(32,42),(48,30),(64,58),(78,36),(24,22),(54,72),(84,66)]
    company_name, bg = get_company_floorplan(selected_company, s)

    if bg:
        html = f"""
        <div class="floor-img-company" style="background-image: url('{bg}');">
            <div class="floor-unit-tag">Empresa: {company_name}</div>
        """
    else:
        selected_txt = selected_company if selected_company and selected_company != "Todas" else "empresa selecionada"
        html = f"""
        <div class="floor">
            <div class="zone" style="left:8%;top:13%;width:30%;height:26%;"></div>
            <div class="zone" style="left:43%;top:13%;width:24%;height:26%;"></div>
            <div class="zone" style="left:70%;top:13%;width:20%;height:26%;"></div>
            <div class="zone" style="left:8%;top:46%;width:36%;height:32%;"></div>
            <div class="zone" style="left:49%;top:46%;width:41%;height:32%;"></div>
            <div class="floor-empty-label">
                Nenhuma imagem vinculada para {selected_txt}<br>
                Cadastre em Empresas & Plantas.
            </div>
        """

    for i, r in top.iterrows():
        x, y = spots[i % len(spots)]
        o = "o" if str(r.get("risk", "")) in ["Crítico", "Alto"] else ""
        pep = str(r.get("elemento_pep", "Projeto"))
        html += f"""
        <div class="hot {o}" style="left:{x}%;top:{y}%;z-index:3;"></div>
        <div class="call {o}" style="left:{min(x+4,74)}%;top:{max(y-12,6)}%;z-index:4;">
            <b>{pep}</b><br>
            Orçado: {fmt(r.get("orcamento_aprovado_total", 0))}<br>
            Realizado: {fmt(r.get("realizado", 0))}<br>
            Consumo: {float(r.get("consumo_pct", 0)):.1%}
        </div>
        """
    html += "</div>"
    return html


def top_table_html(df):
    top = df.copy()

    if top.empty:
        return """
        <div class="top5-panel">
            <div style="color:#8FA7C4;padding:20px 0;font-size:.80rem;">
                Nenhum projeto encontrado.
            </div>
        </div>
        """

    top["desvio_pct"] = np.where(
        top.orcamento_aprovado_total > 0,
        top.VAC / top.orcamento_aprovado_total,
        0
    )

    top = top.sort_values("VAC").head(5)

    rows = ""

    for _, r in top.iterrows():

        nome = str(r.get("nome_projeto", "")).strip()

        if nome and nome.lower() != "nan":
            projeto = f"{r.elemento_pep} - {nome}"
        else:
            projeto = str(r.elemento_pep)

        rows += f"""
        <tr>
            <td class="top5-project" title="{projeto}">
                {projeto}
            </td>

            <td class="top5-money">
                {fmt(r.orcamento_aprovado_total)}
            </td>

            <td class="top5-money">
                {fmt(r.realizado)}
            </td>

            <td class="top5-var">
                {fmt(r.VAC)}
            </td>

            <td class="top5-pct">
                {r.desvio_pct:.1%}
            </td>
        </tr>
        """

    return f"""
    <div class="top5-panel">

        <table class="top5-table">

            <thead>
                <tr>
                    <th class="top5-project">Projeto</th>
                    <th class="top5-money">Orçado (BAC)</th>
                    <th class="top5-money">Realizado (AC)</th>
                    <th class="top5-var">Desvio (R$)</th>
                    <th class="top5-pct">Desvio (%)</th>
                </tr>
            </thead>

            <tbody>
                {rows}
            </tbody>

        </table>

        <div class="top5-cta">
            VER TODOS PROJETOS → 
        </div>

    </div>
    """



def build_top5_dataframe(df):
    top = df.copy()

    if top.empty:
        return pd.DataFrame(columns=[
            "Projeto",
            "Orçado (BAC)",
            "Realizado (AC)",
            "Desvio (R$)",
            "Desvio (%)"
        ])

    top["desvio_pct"] = np.where(
        top.orcamento_aprovado_total > 0,
        top.VAC / top.orcamento_aprovado_total,
        0
    )

    cols = [
        "elemento_pep",
        "orcamento_aprovado_total",
        "realizado",
        "VAC",
        "desvio_pct"
    ]

    top = top.sort_values("VAC").head(5)[cols].copy()

    top.columns = [
        "Projeto",
        "Orçado (BAC)",
        "Realizado (AC)",
        "Desvio (R$)",
        "Desvio (%)"
    ]

    top["Orçado (BAC)"] = top["Orçado (BAC)"].apply(fmt)
    top["Realizado (AC)"] = top["Realizado (AC)"].apply(fmt)
    top["Desvio (R$)"] = top["Desvio (R$)"].apply(fmt)
    top["Desvio (%)"] = top["Desvio (%)"].apply(lambda x: f"{x:.1%}")

    return top



def project_health_interpretation(row):
    risk = str(row.get("risk", "Baixo"))
    cpi = row.get("CPI", np.nan)
    spi = row.get("SPI", np.nan)
    vac = row.get("VAC", 0)
    consumo = row.get("consumo_pct", 0)
    av_real = row.get("avanco_real_pct", 0)
    av_plan = row.get("avanco_planejado_pct", 0)

    messages = []

    if pd.notna(cpi) and cpi < 1:
        messages.append("CPI abaixo de 1,0 indica perda de eficiência de custo.")
    else:
        messages.append("CPI em patamar aceitável indica controle relativo de custo.")

    if pd.notna(spi) and spi < 1:
        messages.append("SPI abaixo de 1,0 indica atraso no avanço físico frente ao planejado.")
    else:
        messages.append("SPI em patamar aceitável indica avanço físico compatível com o plano.")

    if vac < 0:
        messages.append("VAC negativo projeta estouro no custo final estimado.")
    else:
        messages.append("VAC positivo indica tendência de economia ou folga orçamentária.")

    if av_real < av_plan:
        messages.append("O avanço real está abaixo do avanço planejado, exigindo acompanhamento operacional.")

    return f"O projeto está classificado como **{risk}**. Consumo atual: **{consumo:.1%}**. " + " ".join(messages)

def build_project_curve(row):
    months = pd.date_range("2024-01-01", periods=12, freq="MS")
    bac = float(row.get("BAC", row.get("orcamento_aprovado_total", 0)) or 0)
    ac = float(row.get("AC", row.get("realizado", 0)) or 0)
    comp = float(row.get("valor_comprometido", 0) or 0)
    eac = float(row.get("EAC", bac) or 0)

    x = np.linspace(-2, 2, 12)
    weights = 1/(1+np.exp(-x))
    weights = (weights - weights.min())/(weights.max()-weights.min())
    planned = weights/weights[-1] * bac if weights[-1] != 0 else np.zeros(12)
    actual = np.linspace(0, ac, 12)
    committed = np.linspace(0, ac + comp, 12)
    forecast = np.linspace(0, eac, 12)

    return pd.DataFrame({
        "Mês": months.strftime("%Y-%m"),
        "Planejado (PV)": planned,
        "Realizado (AC)": actual,
        "Realizado + Comprometido": committed,
        "Forecast (EAC)": forecast
    })

def render_mini_metric(title, value, subtitle=""):
    st.markdown(f"""
    <div class="metric-mini">
        <div class="metric-mini-title">{title}</div>
        <div class="metric-mini-value">{value}</div>
        <div style="font-size:.72rem;color:#9DB5CF;margin-top:4px;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def build_project_gantt(row):
    start = pd.to_datetime(row.get("data_inicio_planejada", pd.NaT), errors="coerce")
    end = pd.to_datetime(row.get("data_fim_planejada", pd.NaT), errors="coerce")

    if pd.isna(start):
        start = pd.Timestamp("2024-01-01")
    if pd.isna(end):
        end = start + pd.Timedelta(days=120)

    av_plan = float(row.get("avanco_planejado_pct", 0) or 0)
    av_real = float(row.get("avanco_real_pct", 0) or 0)

    planned_end = start + (end - start) * min(max(av_plan/100, 0), 1)
    real_end = start + (end - start) * min(max(av_real/100, 0), 1)

    return pd.DataFrame({
        "Etapa": ["Janela planejada", "Avanço planejado", "Avanço real"],
        "Inicio": [start, start, start],
        "Fim": [end, planned_end, real_end],
        "Tipo": ["Prazo total", "Planejado", "Real"]
    })


def get_param(name, default=None):
    return st.session_state.get("engine_params", {}).get(name, default)

def audit_param_change(param_name, old_value, new_value):
    if old_value != new_value:
        st.session_state.analytics_audit_log.append({
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "parâmetro": param_name,
            "valor_anterior": old_value,
            "valor_novo": new_value
        })

def safe_div(a, b):
    try:
        return float(a) / float(b) if float(b) != 0 else 0
    except Exception:
        return 0

def exec_metric_card(title, value, sub=""):
    st.markdown(
        f"""
        <div class="exec-card">
            <div class="exec-title">{title}</div>
            <div class="exec-value">{value}</div>
            <div class="exec-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def normalize_company_key(value):
    if value is None:
        return ""
    return str(value).strip()

def get_companies_from_data(df_source):
    if isinstance(df_source, pd.DataFrame) and "empresa" in df_source.columns:
        companies = (
            df_source["empresa"]
            .dropna()
            .astype(str)
            .map(lambda x: x.strip())
            .unique()
            .tolist()
        )
        return sorted([c for c in companies if c])
    return []

def image_to_data_url(uploaded_file):
    img_bytes = uploaded_file.getvalue()
    mime = uploaded_file.type or "image/png"
    encoded = base64.b64encode(img_bytes).decode()
    return f"data:{mime};base64,{encoded}"

def get_company_floorplan(selected_company, df_filtered):
    images = st.session_state.get("company_floorplan_images", {})
    selected_key = normalize_company_key(selected_company)

    if selected_key and selected_key != "Todas" and selected_key in images:
        return selected_key, images[selected_key]

    if isinstance(df_filtered, pd.DataFrame) and "empresa" in df_filtered.columns:
        visible_companies = (
            df_filtered["empresa"]
            .dropna()
            .astype(str)
            .map(lambda x: x.strip())
            .unique()
            .tolist()
        )
        for company in visible_companies:
            if company in images:
                return company, images[company]

    return None, None

def calculate_parametric_scores(df):
    out = df.copy()
    p = st.session_state.engine_params

    cpi_red = float(p.get("risk_cpi_red", 0.80))
    spi_red = float(p.get("risk_spi_red", 0.80))
    vac_red_pct = float(p.get("risk_vac_red_pct", -0.10))

    out["param_vac_pct"] = np.where(out["orcamento_aprovado_total"] > 0, out["VAC"] / out["orcamento_aprovado_total"], 0)

    out["param_risk"] = np.select(
        [
            (out["CPI"].fillna(1) < cpi_red) | (out["SPI"].fillna(1) < spi_red) | (out["param_vac_pct"] < vac_red_pct),
            (out["CPI"].fillna(1) < float(p.get("risk_cpi_yellow", 0.90))) | (out["SPI"].fillna(1) < float(p.get("risk_spi_yellow", 0.90))) | (out["param_vac_pct"] < float(p.get("risk_vac_yellow_pct", -0.05))),
            out["exposicao_pct"].fillna(0) >= .65
        ],
        ["Crítico", "Alto", "Médio"],
        default="Baixo"
    )

    weights = {
        "cpi": float(p.get("health_weight_cpi", 25)),
        "spi": float(p.get("health_weight_spi", 25)),
        "vac": float(p.get("health_weight_vac", 20)),
        "forecast": float(p.get("health_weight_forecast", 15)),
        "data_quality": float(p.get("health_weight_data_quality", 15))
    }
    total_w = max(sum(weights.values()), 1)

    cpi_score = np.clip(out["CPI"].fillna(1), 0, 1) * 100
    spi_score = np.clip(out["SPI"].fillna(1), 0, 1) * 100
    vac_score = np.where(out["VAC"] >= 0, 100, np.clip(100 + out["param_vac_pct"]*100, 0, 100))
    forecast_score = np.where(out["EAC"] <= out["BAC"], 100, np.clip(100 - ((out["EAC"]-out["BAC"]) / out["BAC"].replace(0, np.nan)).fillna(0)*100, 0, 100))
    dq_score = data_quality_score(out)

    out["param_health_score"] = (
        cpi_score * weights["cpi"] +
        spi_score * weights["spi"] +
        vac_score * weights["vac"] +
        forecast_score * weights["forecast"] +
        dq_score * weights["data_quality"]
    ) / total_w

    return out

def data_quality_score(df):
    required = str(get_param("data_quality_required_fields", "")).split(",")
    required = [c.strip() for c in required if c.strip()]
    if not required:
        return pd.Series([100]*len(df), index=df.index)

    score = pd.Series([100.0]*len(df), index=df.index)
    penalty = 100 / max(len(required), 1)

    for col in required:
        if col not in df.columns:
            score -= penalty
        else:
            missing = df[col].isna() | df[col].astype(str).str.strip().eq("")
            score -= np.where(missing, penalty, 0)
    return score.clip(0,100)

def classify_capex_opex(row):
    p = st.session_state.engine_params
    min_value = float(p.get("capex_min_value", 1000000))
    keywords = [k.strip().lower() for k in str(p.get("capex_opex_keywords", "")).split(",") if k.strip()]
    nome = str(row.get("nome_projeto", "")).lower()
    valor = float(row.get("orcamento_aprovado_total", 0) or 0)

    reasons = []
    if valor < min_value:
        reasons.append(f"valor abaixo do mínimo CAPEX configurado ({fmt(min_value)})")
    if any(k in nome for k in keywords):
        reasons.append("descrição contém palavra-chave típica de OPEX")
    if not reasons:
        return "CAPEX provável", "Projeto acima dos critérios mínimos de capitalização configurados."
    if len(reasons) >= 2:
        return "Possível OPEX", "Classificado assim porque " + "; ".join(reasons) + "."
    return "Revisar classificação", "Revisar porque " + "; ".join(reasons) + "."

def build_enterprise_engine(df):
    out = calculate_parametric_scores(df)
    out["data_quality_score_param"] = data_quality_score(out)

    capex_results = out.apply(classify_capex_opex, axis=1)
    out["capex_opex_sugestao"] = [x[0] for x in capex_results]
    out["capex_opex_explicacao"] = [x[1] for x in capex_results]

    out["maturity_score_param"] = (
        100
        - np.where(out["orcamento_aprovado_total"].fillna(0) <= 0, float(get_param("maturity_weight_budget",20)), 0)
        - np.where(out["avanco_planejado_pct"].fillna(0) <= 0, float(get_param("maturity_weight_schedule",20)), 0)
        - np.where(out["avanco_real_pct"].fillna(0) <= 0, float(get_param("maturity_weight_physical_progress",20)), 0)
        - np.where(out["CPI"].fillna(1) < 0.9, float(get_param("maturity_weight_cost_performance",20)), 0)
        - np.where(out["VAC"].fillna(0) < 0, float(get_param("maturity_weight_forecast",20)), 0)
    ).clip(0,100)

    out["investment_efficiency_param"] = (
        out["param_health_score"] * float(get_param("roi_weight_health",45)) +
        out["maturity_score_param"] * float(get_param("roi_weight_maturity",25)) +
        ((1-out["prob_estouro"].fillna(0))*100) * float(get_param("roi_weight_risk",30))
    ) / max(float(get_param("roi_weight_health",45))+float(get_param("roi_weight_maturity",25))+float(get_param("roi_weight_risk",30)),1)

    out["forecast_model_used"] = get_param("forecast_model","Híbrido")
    out["forecast_param"] = np.where(
        out["forecast_model_used"].eq("Linear") if hasattr(out["forecast_model_used"], "eq") else False,
        out["realizado"] + out["valor_comprometido"],
        out["EAC"]
    )

    return out

def scenario_impact_param(df, reduction_pct=None, delay_months=None, fx_pct=None):
    if reduction_pct is None:
        reduction_pct = float(get_param("whatif_default_budget_cut_pct",10))
    if delay_months is None:
        delay_months = float(get_param("whatif_default_delay_months",3))
    if fx_pct is None:
        fx_pct = float(get_param("whatif_default_fx_cost_pct",8))

    sim = df.copy()
    sim["budget_scenario"] = sim["orcamento_aprovado_total"] * (1 - reduction_pct/100)
    sim["eac_scenario"] = sim["EAC"] * (1 + fx_pct/100)
    sim["vac_scenario"] = sim["budget_scenario"] - sim["eac_scenario"]
    sim["delay_impact_days"] = delay_months * 30 * np.where(sim["SPI"].fillna(1)<1, 1.25, 1)
    sim["new_risk"] = np.select(
        [sim["vac_scenario"] < 0, sim["delay_impact_days"] > 60, sim["vac_scenario"] < sim["budget_scenario"]*.1],
        ["Crítico","Alto","Médio"],
        default="Baixo"
    )
    return sim

def executive_insights_param(df):
    eng = build_enterprise_engine(df)
    insights = []
    if eng.empty:
        return ["Nenhum dado disponível para gerar insights."]

    crit = int((eng["param_risk"]=="Crítico").sum())
    low_dq = int((eng["data_quality_score_param"]<70).sum())
    possible_opex = int((eng["capex_opex_sugestao"]=="Possível OPEX").sum())
    low_maturity = int((eng["maturity_score_param"]<60).sum())
    forecast_over = eng.loc[eng["forecast_param"]>eng["BAC"], "forecast_param"].sum() - eng.loc[eng["forecast_param"]>eng["BAC"], "BAC"].sum()

    if crit:
        insights.append(f"{crit} projetos classificados como críticos pelo motor parametrizado.")
    if possible_opex:
        insights.append(f"{possible_opex} projetos podem exigir revisão CAPEX/OPEX conforme critérios configurados.")
    if low_dq:
        insights.append(f"{low_dq} projetos possuem baixa qualidade de dados conforme campos obrigatórios.")
    if low_maturity:
        insights.append(f"{low_maturity} projetos apresentam baixa maturidade de planejamento.")
    if forecast_over > 0:
        insights.append(f"O forecast parametrizado indica potencial necessidade adicional de {fmt(forecast_over)}.")
    if not insights:
        insights.append("Nenhum alerta executivo relevante no recorte atual.")
    return insights

def render_insight_list(items):
    classes = ["insight-critical","insight-high","insight-medium","insight-low"]
    for i, item in enumerate(items):
        st.markdown(f'<div class="insight-item {classes[min(i,3)]}">{item}</div>', unsafe_allow_html=True)

def export_excel(df):
    out=BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="ANALISE")
        pd.DataFrame(st.session_state.load_log).to_excel(w, index=False, sheet_name="LOG_CARGAS")
    out.seek(0)
    return out

st.sidebar.markdown("""
<div class="brand-wrap">
  <div class="brand">
    <div class="logo">💠</div>
    <div>
      <div class="brand-title">CAPEXVISION</div>
      <div class="brand-sub">COCKPIT EXECUTIVO</div>
    </div>
  </div>
</div>
<div class="user-box">
  <div class="avatar">👤</div>
  <div>
    <div class="user-title">Olá, Gestor!</div>
    <div class="user-sub">Bem-vindo ao cockpit executivo</div>
  </div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navegação",
    ["▦ Visão Geral","▤ Projetos","🔎 Detalhe do Projeto","🧠 Inteligência Executiva","🧪 Simulador What-if","🏛️ Pipeline & Contratos","📊 Eficiência & ROI","🧾 CAPEX x OPEX","🌱 ESG & Sustentabilidade","⚙️ Governança & Parâmetros","🏢 Empresas & Plantas","◈ Análise Financeira","◷ Atrasos e Prazos","⌖ Mapa de Localizações","▥ Planta da Unidade","⚠ Alertas","◎ Previsão (EVM)","∿ Curva S","ⓘ Notas Explicativas","⚙ Configurações"],
    label_visibility="collapsed"
)






st.sidebar.markdown("### Carga de dados")
load_mode = st.sidebar.radio("Modo", ["Substituir base", "Acrescentar evitando duplicados"])
uploaded=st.sidebar.file_uploader("Enviar Excel",type=["xlsx"])
if st.sidebar.button("Processar carga", use_container_width=True):
    if uploaded:
        apply_load(read_excel(uploaded), load_mode)
        st.sidebar.success("Carga processada.")
    else:
        st.sidebar.warning("Envie um arquivo primeiro.")
if st.sidebar.button("Usar dados demonstrativos", use_container_width=True):
    st.session_state.raw_data = demo_data()
    st.session_state.load_log.append({"data_hora":datetime.now().strftime("%d/%m/%Y %H:%M"),"modo":"Demo","abas":5})
if st.sidebar.button("Limpar base", use_container_width=True):
    st.session_state.raw_data = None
    st.session_state.load_log = []

st.sidebar.markdown("""
<div class="footer-brand">
💠 <b>CAPEXVISION</b><br>
Inteligência para seus investimentos<br><br>
🟢 Versão 23.3.0
</div>
""", unsafe_allow_html=True)

data = st.session_state.raw_data if st.session_state.raw_data is not None else demo_data()
s=build_summary(data)

st.markdown(f"""
<div class="header">
  <div style="display:flex;justify-content:space-between;gap:16px;align-items:start;">
    <div>
      <div class="header-title">{menu.replace('▦ ','').replace('▤ ','').replace('🔎 ','').replace('🧠 ','').replace('🧪 ','').replace('🏛️ ','').replace('📊 ','').replace('🧾 ','').replace('🌱 ','').replace('⚙️ ','').replace('🏢 ','').replace('◈ ','').replace('◷ ','').replace('⌖ ','').replace('▥ ','').replace('⚠ ','').replace('◎ ','').replace('∿ ','').replace('ⓘ ','').replace('⚙ ','')}</div>
      <div class="header-sub">Panorama executivo dos investimentos</div>
    </div>
    <div class="update">Última atualização<br><b>{datetime.now().strftime("%d/%m/%Y %H:%M")}</b> &nbsp; ⟳</div>
  </div>
</div>
""", unsafe_allow_html=True)

f1,f2,f3,f4,f5=st.columns([1.3,1.5,1.25,1.35,1.1])
empresa=f1.selectbox("EMPRESA",["Todas"]+sorted(s.empresa.astype(str).unique().tolist()))
unidade=f2.selectbox("UNIDADE / LOCALIZAÇÃO",["Todas"]+sorted(s.get("area_responsavel",pd.Series()).dropna().astype(str).unique().tolist()))
status=f3.selectbox("STATUS",["Todos"]+sorted(s.get("status_usuario",pd.Series()).dropna().astype(str).unique().tolist()))
periodo=f4.text_input("PERÍODO","01/01/2024 - 31/12/2024")
limpar=f5.button("⟳ LIMPAR FILTROS", use_container_width=True)
search = st.text_input("PESQUISAR PROJETO / PEP / RESPONSÁVEL", "", placeholder="Digite parte do projeto, PEP, área ou responsável...")

df=s.copy()
if empresa!="Todas": df=df[df.empresa.astype(str).str.strip()==str(empresa).strip()]
if unidade!="Todas" and "area_responsavel" in df: df=df[df.area_responsavel.astype(str)==unidade]
if status!="Todos" and "status_usuario" in df: df=df[df.status_usuario.astype(str)==status]
if search:
    mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
    df=df[mask]

orc=df.orcamento_aprovado_total.sum()
real=df.realizado.sum()
comp=df.valor_comprometido.sum()
sal=df.saldo.sum()
health=df.health_score.mean() if len(df) else 0


def render_kpis():
    cols=st.columns([1,1,1,1,.88,.95])
    with cols[0]: kpi("ORÇADO TOTAL (BAC)",fmt(orc),"100% do orçamento total","💰","blue")
    with cols[1]: kpi("COMPROMETIDO",fmt(comp),f"{(comp/orc if orc else 0):.1%} do orçamento","✅","green")
    with cols[2]: kpi("REALIZADO (AC)",fmt(real),f"{(real/orc if orc else 0):.1%} do orçamento","▦","orange")
    with cols[3]: kpi("SALDO (BAC - AC)",fmt(sal),f"{(sal/orc if orc else 0):.1%} do orçamento","⛓","purple")
    with cols[4]: kpi("PROJETOS ATIVOS",str(len(df)),"Em andamento","👤","cyan")
    with cols[5]:
        with st.container(border=True):
            st.markdown('<div class="ptitle" style="text-align:center;font-size:.76rem;">HEALTH SCORE MÉDIO</div>',unsafe_allow_html=True)
            st.plotly_chart(gauge(health,"",0,100, height=108),use_container_width=True,config={"displayModeBar":False})


def render_visual_overview():
    render_kpis()

    r1c1,r1c2,r1c3,r1c4=st.columns([1.35,1.55,.82,1.25])
    with r1c1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">RESUMO FINANCEIRO</div>',unsafe_allow_html=True)
            render_indicator_legend_custom()
            st.plotly_chart(donut(df),use_container_width=True,config={"displayModeBar":False})
    with r1c2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">DESEMPENHO EVM (GERAL)</div><div class="psub">CPI e SPI abaixo de 1,0 exigem atenção executiva.</div>',unsafe_allow_html=True)
            g=st.columns(4)
            values=[(np.nanmean(df.CPI),"CPI",0,1.5),(np.nanmean(df.SPI),"SPI",0,1.5),(df.EAC.sum()/1e6,"EAC",0,max(df.EAC.sum()/1e6*1.2,1)),(abs(df.VAC.sum())/1e6,"VAC",0,max(abs(df.VAC.sum())/1e6*1.2,1))]
            for col,(val,title,minv,maxv) in zip(g,values):
                with col:
                    st.plotly_chart(gauge(val,title,minv,maxv, height=122),use_container_width=True,config={"displayModeBar":False})
            st.markdown('<div style="color:#B7C7DC;font-size:.74rem;">CPI = EV / AC · SPI = EV / PV · EAC = estimativa ao término · VAC = BAC - EAC</div>',unsafe_allow_html=True)
    with r1c3:
        with st.container(border=True):
            crit=int((df.risk=="Crítico").sum()); high=int((df.risk=="Alto").sum()); med=int((df.risk=="Médio").sum()); miss=int((df.orcamento_aprovado_total<=0).sum())
            st.markdown(f'''
            <div class="ptitle">ALERTAS CRÍTICOS</div>
            <div class="alert-row"><span>🔴 Estouro iminente (&gt; 90%)</span><span class="badge red">{crit}</span></div>
            <div class="alert-row"><span>🔴 Projetos com atraso</span><span class="badge red">{high}</span></div>
            <div class="alert-row"><span>🟠 Estouro previsto (EAC &gt; BAC)</span><span class="badge amber">{med}</span></div>
            <div class="alert-row"><span>🟡 Dados incompletos</span><span class="badge yellow">{miss}</span></div>
            <div style="text-align:right;margin-top:10px;color:#3AA7FF;font-weight:950;font-size:.76rem;">VER TODOS ALERTAS →</div>
            ''',unsafe_allow_html=True)
    with r1c4:
        with st.container(border=True):
            st.markdown('<div class="ptitle">DISTRIBUIÇÃO POR STATUS</div>',unsafe_allow_html=True)
            vc=df.get("status_usuario",pd.Series(["Em Andamento"]*len(df))).fillna("Em Andamento").value_counts()
            fig=go.Figure(go.Funnelarea(values=vc.values,text=vc.index,marker={"colors":["#3AA7FF","#74D94A","#FFB020","#8D55FF"]}))
            fig.update_layout(height=205,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)",font_color="#EAF2FF")
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    r2c1,r2c2,r2c3=st.columns([1.25,1.25,1.45])
    with r2c1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">MAPA DE LOCALIZAÇÕES</div><div class="psub">Orçado vs realizado por localização geográfica</div>',unsafe_allow_html=True)
            add_risk_legend()
            fig=px.scatter_mapbox(df,lat="latitude",lon="longitude",size="orcamento_aprovado_total",color="risk",hover_name="elemento_pep",zoom=3,height=270,color_discrete_map=RISK_COLOR_MAP)
            fig.update_layout(mapbox_style="carto-darkmatter",margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with r2c2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">PLANTA DA UNIDADE</div><div class="psub">Visão dos investimentos na planta industrial</div>',unsafe_allow_html=True)
            st.markdown(floor(df, unidade, empresa), unsafe_allow_html=True)
    with r2c3:
        with st.container(border=True):
            st.markdown('<div class="ptitle">TOP 5 PROJETOS (MAIOR DESVIO)</div>',unsafe_allow_html=True)
            top5 = build_top5_dataframe(df)
            st.dataframe(
                top5,
                use_container_width=True,
                hide_index=True,
                height=255
            )
            st.markdown(
                '''
                <div style="text-align:center;margin-top:10px;color:#3AA7FF;font-weight:900;font-size:.76rem;letter-spacing:.2px;">
                    VER TODOS PROJETOS →
                </div>
                ''',
                unsafe_allow_html=True
            )

    n1,n2=st.columns([5.4,.95])
    with n1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">NOTAS EXPLICATIVAS - PRINCIPAIS SIGLAS E TERMINOLOGIAS</div><div class="note-grid">' + ''.join([
                f'<div class="note"><div class="ntitle">{a}</div><div class="ntext">{b}</div></div>' for a,b in [
                    ("BAC","Orçamento total aprovado para conclusão do projeto."),
                    ("AC","Custo real incorrido até a data de referência."),
                    ("PV","Valor planejado do trabalho a ser realizado."),
                    ("EV","Valor agregado do trabalho efetivamente realizado."),
                    ("CPI","Índice de desempenho de custo. CPI = EV / AC."),
                    ("SPI","Índice de desempenho de prazo. SPI = EV / PV."),
                    ("EAC","Estimativa de custo total ao término do projeto."),
                    ("VAC","Variação estimada no custo ao término. VAC = BAC - EAC.")
                ]]) + '</div>', unsafe_allow_html=True)
    with n2:
        st.markdown('''
        <div class="tip">
          <div style="color:#FF6B6B;font-weight:950;">💡 DICA DE GESTÃO</div>
          <div style="color:#D8E7FA;margin-top:8px;font-size:.80rem;line-height:1.42;">
            Projetos com CPI abaixo de 1,0 estão custando mais do que o planejado. Acompanhe alertas e tome ações corretivas.
          </div>
        </div>
        ''',unsafe_allow_html=True)

if menu == "▦ Visão Geral":
    render_visual_overview()
elif menu == "▤ Projetos":
    render_kpis()
    with st.container(border=True):
        st.markdown('<div class="ptitle">CARTEIRA DE PROJETOS / PEPs</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "🔎 Detalhe do Projeto":
    st.markdown(
        '<div class="story"><b>Drill-down individual:</b> selecione um projeto/PEP para analisar desempenho financeiro, prazo, EVM, risco e histórico de lançamentos.</div>',
        unsafe_allow_html=True
    )

    projeto_options = sorted(df["elemento_pep"].dropna().astype(str).unique().tolist()) if "elemento_pep" in df.columns else []

    if not projeto_options:
        st.warning("Nenhum projeto disponível para análise com os filtros atuais.")
    else:
        selected_project = st.selectbox("Selecionar projeto / PEP", projeto_options, key="selected_project_detail")
        project_df = df[df["elemento_pep"].astype(str) == selected_project].copy()
        row = project_df.iloc[0]

        risk = str(row.get("risk", "Baixo"))
        risk_class = "risk-" + risk

        st.markdown(f"""
        <div class="project-card">
            <div style="display:flex;justify-content:space-between;gap:16px;align-items:start;">
                <div>
                    <div class="project-title">{row.get("elemento_pep", "")}</div>
                    <div class="project-sub">
                        Projeto: {row.get("definicao_projeto", "-")} ·
                        Empresa: {row.get("empresa", "-")} ·
                        Unidade: {row.get("area_responsavel", "-")} ·
                        Responsável: {row.get("responsavel", "-")}
                    </div>
                </div>
                <div><span class="risk-pill {risk_class}">{risk}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        k1,k2,k3,k4,k5,k6 = st.columns(6)
        with k1:
            render_mini_metric("BAC / Orçado", fmt(row.get("BAC", row.get("orcamento_aprovado_total", 0))), "Budget at Completion")
        with k2:
            render_mini_metric("AC / Realizado", fmt(row.get("AC", row.get("realizado", 0))), "Actual Cost")
        with k3:
            render_mini_metric("Comprometido", fmt(row.get("valor_comprometido", 0)), "Pedidos/contratos")
        with k4:
            render_mini_metric("Saldo", fmt(row.get("saldo", 0)), f"{row.get('consumo_pct',0):.1%} consumido")
        with k5:
            render_mini_metric("EAC", fmt(row.get("EAC", 0)), "Estimativa ao término")
        with k6:
            render_mini_metric("VAC", fmt(row.get("VAC", 0)), "Variação ao término")

        st.markdown(f"""
        <div class="insight-box">
            <b>Diagnóstico executivo automático:</b><br>
            {project_health_interpretation(row)}
        </div>
        """, unsafe_allow_html=True)

        g1,g2,g3,g4 = st.columns(4)
        with g1:
            st.plotly_chart(gauge(row.get("CPI", 0), "CPI", 0, 1.5, height=190), use_container_width=True, config={"displayModeBar": False})
        with g2:
            st.plotly_chart(gauge(row.get("SPI", 0), "SPI", 0, 1.5, height=190), use_container_width=True, config={"displayModeBar": False})
        with g3:
            st.plotly_chart(gauge(row.get("health_score", 0), "Health Score", 0, 100, height=190), use_container_width=True, config={"displayModeBar": False})
        with g4:
            st.plotly_chart(gauge(row.get("prob_estouro", 0)*100, "Prob. Estouro (%)", 0, 100, height=190), use_container_width=True, config={"displayModeBar": False})

        c1,c2 = st.columns([1.25,1])
        with c1:
            with st.container(border=True):
                st.markdown('<div class="ptitle">CURVA S INDIVIDUAL — PLANEJADO, REALIZADO E FORECAST</div>', unsafe_allow_html=True)
                curve = build_project_curve(row)
                fig = px.line(curve, x="Mês", y=["Planejado (PV)", "Realizado (AC)", "Realizado + Comprometido", "Forecast (EAC)"], markers=True, height=410)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF", legend_title_text="Métrica", margin=dict(l=10,r=10,t=30,b=10))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with c2:
            with st.container(border=True):
                st.markdown('<div class="ptitle">GANTT INDIVIDUAL DO PROJETO</div>', unsafe_allow_html=True)
                gantt_project = build_project_gantt(row)
                fig = px.timeline(gantt_project, x_start="Inicio", x_end="Fim", y="Etapa", color="Tipo",
                    color_discrete_map={"Prazo total": "#3AA7FF", "Planejado": "#F2C94C", "Real": "#37C978"}, height=410)
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF", legend_title_text="Tipo", margin=dict(l=10,r=10,t=30,b=10))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        d1,d2 = st.columns([1,1])
        with d1:
            with st.container(border=True):
                st.markdown('<div class="ptitle">MATRIZ DE RISCO INDIVIDUAL</div>', unsafe_allow_html=True)
                risk_data = pd.DataFrame({
                    "Risco": ["Financeiro", "Prazo", "Execução", "Dados", "Forecast"],
                    "Score": [
                        float(row.get("prob_estouro", 0))*100,
                        float(row.get("prob_atraso", 0))*100,
                        max(0, 100 - float(row.get("health_score", 0))),
                        0 if row.get("orcamento_aprovado_total", 0) > 0 else 80,
                        80 if row.get("VAC", 0) < 0 else 25
                    ]
                })
                fig = px.bar(risk_data, x="Risco", y="Score", color="Score",
                    color_continuous_scale=["#37C978", "#F2C94C", "#F28C28", "#E9494A"],
                    range_color=[0,100], height=350)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF", showlegend=False, coloraxis_showscale=False, margin=dict(l=10,r=10,t=20,b=10))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with d2:
            with st.container(border=True):
                st.markdown('<div class="ptitle">VARIAÇÕES ORÇAMENTÁRIAS</div>', unsafe_allow_html=True)
                budget_variation = pd.DataFrame({
                    "Indicador": ["Orçamento Original", "Suplementação", "Redução", "Orçamento Atual", "Variação Líquida"],
                    "Valor": [row.get("orcamento_original", 0), row.get("suplementacao", 0), row.get("reducao", 0), row.get("orcamento_aprovado_total", 0), row.get("variacao_budget", 0)]
                })
                budget_variation["Valor Formatado"] = budget_variation["Valor"].apply(fmt)
                st.dataframe(budget_variation[["Indicador", "Valor Formatado"]], use_container_width=True, hide_index=True, height=350)

        with st.container(border=True):
            st.markdown('<div class="ptitle">HISTÓRICO / LANÇAMENTOS DO PROJETO</div>', unsafe_allow_html=True)
            project_cols = ["empresa","definicao_projeto","elemento_pep","nome_projeto","area_responsavel","responsavel","status_usuario","orcamento_aprovado_total","realizado","valor_comprometido","saldo","CPI","SPI","EAC","VAC","risk","health_score"]
            available = [c for c in project_cols if c in project_df.columns]
            st.dataframe(project_df[available], use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.markdown('<div class="ptitle">EXPORTAÇÃO DO RELATÓRIO DO PROJETO</div>', unsafe_allow_html=True)
            export_project = BytesIO()
            with pd.ExcelWriter(export_project, engine="openpyxl") as writer:
                project_df.to_excel(writer, index=False, sheet_name="PROJETO")
                build_project_curve(row).to_excel(writer, index=False, sheet_name="CURVA_S")
                build_project_gantt(row).to_excel(writer, index=False, sheet_name="GANTT")
            export_project.seek(0)
            st.download_button("Baixar relatório individual do projeto", export_project, file_name=f"relatorio_projeto_{selected_project}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



elif menu == "🧠 Inteligência Executiva":
    eng = build_enterprise_engine(df)
    st.markdown('<div class="story"><b>Inteligência Executiva Parametrizada:</b> resultados calculados com base nos critérios definidos em Governança & Parâmetros.</div>', unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        exec_metric_card("Health Param.", f"{eng['param_health_score'].mean():.0f}", "Score com pesos configuráveis")
    with c2:
        exec_metric_card("Maturidade", f"{eng['maturity_score_param'].mean():.0f}", "Project Maturity Score")
    with c3:
        exec_metric_card("Data Quality", f"{eng['data_quality_score_param'].mean():.0f}", "Campos obrigatórios")
    with c4:
        exec_metric_card("Possíveis OPEX", str(int((eng['capex_opex_sugestao']=='Possível OPEX').sum())), "Critério configurável")
    with c5:
        exec_metric_card("Críticos", str(int((eng['param_risk']=='Crítico').sum())), "Motor de risco")

    a,b = st.columns([1.15,1])
    with a:
        with st.container(border=True):
            st.markdown('<div class="ptitle">CENTRO DE INSIGHTS AUTOMÁTICOS</div>', unsafe_allow_html=True)
            render_insight_list(executive_insights_param(df))
    with b:
        with st.container(border=True):
            st.markdown('<div class="ptitle">RISCO PELO MOTOR PARAMETRIZADO</div>', unsafe_allow_html=True)
            render_risk_legend_custom()
            risk_df = eng["param_risk"].value_counts().reset_index()
            risk_df.columns = ["Risco","Projetos"]
            fig = px.pie(risk_df, names="Risco", values="Projetos", hole=.58, color="Risco", color_discrete_map=RISK_COLOR_MAP, height=340)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    h1,h2 = st.columns([1,1])
    with h1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">HEATMAP DE DESVIOS — EMPRESA x RISCO</div>', unsafe_allow_html=True)
            heat = eng.pivot_table(index="empresa", columns="param_risk", values="VAC", aggfunc="sum", fill_value=0)
            fig = px.imshow(heat, text_auto=".2s", color_continuous_scale=["#E9494A","#F2C94C","#37C978"], aspect="auto", height=380)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with h2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">BENCHMARK — CUSTO POR AVANÇO</div>', unsafe_allow_html=True)
            bench = eng.copy()
            bench["custo_por_avanco"] = np.where(bench["avanco_real_pct"]>0, bench["realizado"]/bench["avanco_real_pct"], np.nan)
            bench = bench.sort_values("custo_por_avanco").head(12)
            fig = px.bar(bench, x="custo_por_avanco", y="elemento_pep", orientation="h", color="param_risk", color_discrete_map=RISK_COLOR_MAP, height=380)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.container(border=True):
        st.markdown('<div class="ptitle">EXPLAINABLE ANALYTICS — CLASSIFICAÇÃO CAPEX/OPEX</div>', unsafe_allow_html=True)
        st.dataframe(eng[["empresa","elemento_pep","nome_projeto","orcamento_aprovado_total","capex_opex_sugestao","capex_opex_explicacao","param_risk","param_health_score","data_quality_score_param"]], use_container_width=True, hide_index=True)

elif menu == "🧪 Simulador What-if":
    st.markdown('<div class="story"><b>Simulador What-if Parametrizado:</b> valores padrão vêm da tela Governança & Parâmetros, mas podem ser ajustados para cenários específicos.</div>', unsafe_allow_html=True)

    s1,s2,s3 = st.columns(3)
    with s1:
        reduction_pct = st.slider("Redução de orçamento (%)", 0, 60, int(get_param("whatif_default_budget_cut_pct",10)))
    with s2:
        delay_months = st.slider("Postergar projetos (meses)", 0, 18, int(get_param("whatif_default_delay_months",3)))
    with s3:
        fx_pct = st.slider("Aumento de custos/câmbio (%)", -30, 80, int(get_param("whatif_default_fx_cost_pct",8)))

    sim = scenario_impact_param(df, reduction_pct, delay_months, fx_pct)

    k1,k2,k3,k4 = st.columns(4)
    with k1:
        exec_metric_card("Novo orçamento", fmt(sim["budget_scenario"].sum()), f"Corte: {reduction_pct}%")
    with k2:
        exec_metric_card("Novo EAC", fmt(sim["eac_scenario"].sum()), f"Custo/câmbio: {fx_pct}%")
    with k3:
        exec_metric_card("Novo VAC", fmt(sim["vac_scenario"].sum()), "Cenário")
    with k4:
        exec_metric_card("Projetos críticos", str(int((sim["new_risk"]=="Crítico").sum())), "Pós-simulação")

    c1,c2 = st.columns([1,1])
    with c1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">IMPACTO POR PROJETO</div>', unsafe_allow_html=True)
            render_risk_legend_custom()
            top = sim.sort_values("vac_scenario").head(15)
            fig = px.bar(top, x="vac_scenario", y="elemento_pep", orientation="h", color="new_risk", color_discrete_map=RISK_COLOR_MAP, height=460)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with c2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">DISTRIBUIÇÃO DE RISCO SIMULADO</div>', unsafe_allow_html=True)
            render_risk_legend_custom()
            pie = sim["new_risk"].value_counts().reset_index()
            pie.columns = ["Risco","Projetos"]
            fig = px.pie(pie, names="Risco", values="Projetos", hole=.55, color="Risco", color_discrete_map=RISK_COLOR_MAP, height=460)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.container(border=True):
        st.markdown('<div class="ptitle">TABELA DO CENÁRIO</div>', unsafe_allow_html=True)
        st.dataframe(sim[["empresa","elemento_pep","orcamento_aprovado_total","budget_scenario","EAC","eac_scenario","VAC","vac_scenario","risk","new_risk","delay_impact_days"]], use_container_width=True, hide_index=True)

elif menu == "🏛️ Pipeline & Contratos":
    eng = build_enterprise_engine(df).copy()
    suppliers = ["Fornecedor Alfa","Fornecedor Beta","Fornecedor Gama","Fornecedor Delta","Fornecedor Ômega"]
    stages = ["Ideia","Estudo","Aprovação","Contratação","Execução","Encerramento"]
    eng["fornecedor"] = [suppliers[i % len(suppliers)] for i in range(len(eng))]
    eng["pipeline_stage"] = [stages[i % len(stages)] for i in range(len(eng))]
    eng["contract_balance"] = eng["valor_comprometido"].fillna(0) * 0.35
    eng["contract_consumption_pct"] = np.where(eng["valor_comprometido"]>0, 1 - eng["contract_balance"]/eng["valor_comprometido"], 0)
    eng["approval_sla_days"] = 12 + (eng.index % 28)

    st.markdown('<div class="story"><b>Pipeline & Contratos:</b> controle de aprovação, gargalos, saldo contratual, consumo e concentração por fornecedor.</div>', unsafe_allow_html=True)
    p1,p2,p3,p4 = st.columns(4)
    with p1:
        exec_metric_card("SLA médio", f"{eng['approval_sla_days'].mean():.0f} dias", "Aprovação")
    with p2:
        exec_metric_card("Saldo contratual", fmt(eng["contract_balance"].sum()), "Contratos")
    with p3:
        exec_metric_card("Fornecedores", str(eng["fornecedor"].nunique()), "Base")
    with p4:
        exec_metric_card("Concentração TOP 3", f"{safe_div(eng.groupby('fornecedor')['valor_comprometido'].sum().sort_values(ascending=False).head(3).sum(), eng['valor_comprometido'].sum()):.1%}", "Comprometido")

    a,b = st.columns([1,1])
    with a:
        with st.container(border=True):
            pipe = eng.groupby("pipeline_stage")["elemento_pep"].count().reset_index()
            pipe.columns = ["Etapa","Projetos"]
            fig = px.funnel(pipe, x="Projetos", y="Etapa", height=420)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with b:
        with st.container(border=True):
            forn = eng.groupby("fornecedor")["valor_comprometido"].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(forn, x="valor_comprometido", y="fornecedor", orientation="h", height=420)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.container(border=True):
        st.dataframe(eng[["empresa","elemento_pep","fornecedor","valor_comprometido","contract_balance","contract_consumption_pct","pipeline_stage","approval_sla_days","param_risk"]], use_container_width=True, hide_index=True)

elif menu == "📊 Eficiência & ROI":
    eng = build_enterprise_engine(df)
    eng["roi_estimado_pct"] = ((eng["BAC"] - eng["forecast_param"]) / eng["BAC"].replace(0,np.nan)).fillna(0) + 0.12
    eng["payback_meses"] = np.clip(24 + (100-eng["investment_efficiency_param"])/3, 6, 60)

    st.markdown('<div class="story"><b>Eficiência & ROI:</b> análise de retorno, payback e eficiência dos investimentos corporativos.</div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    with a:
        exec_metric_card("ROI médio", f"{eng['roi_estimado_pct'].mean():.1%}", "Estimado")
    with b:
        exec_metric_card("Payback médio", f"{eng['payback_meses'].mean():.1f} meses", "Estimado")
    with c:
        exec_metric_card("Eficiência média", f"{eng['investment_efficiency_param'].mean():.0f}", "0 a 100")
    with d:
        exec_metric_card("Elite", str(int((eng["investment_efficiency_param"]>=80).sum())), "Alta eficiência")

    c1,c2 = st.columns([1.15,1])
    with c1:
        with st.container(border=True):
            top = eng.sort_values("investment_efficiency_param", ascending=False).head(15)
            fig = px.bar(top, x="investment_efficiency_param", y="elemento_pep", orientation="h", color="investment_efficiency_param", color_continuous_scale=["#E9494A","#F2C94C","#37C978"], height=460)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with c2:
        with st.container(border=True):
            fig = px.scatter(eng, x="payback_meses", y="roi_estimado_pct", size="orcamento_aprovado_total", color="param_risk", color_discrete_map=RISK_COLOR_MAP, hover_name="elemento_pep", height=460)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

elif menu == "🧾 CAPEX x OPEX":
    eng = build_enterprise_engine(df)
    st.markdown('<div class="story"><b>CAPEX x OPEX Intelligence:</b> classificação explicável baseada nos parâmetros definidos em Governança & Parâmetros.</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        exec_metric_card("Possível OPEX", str(int((eng["capex_opex_sugestao"]=="Possível OPEX").sum())), "Revisar")
    with c2:
        exec_metric_card("Revisar classificação", str(int((eng["capex_opex_sugestao"]=="Revisar classificação").sum())), "Atenção")
    with c3:
        exec_metric_card("Depreciação futura", fmt(eng["orcamento_aprovado_total"].sum()/120), "Vida útil 10 anos")

    a,b = st.columns([1,1])
    with a:
        with st.container(border=True):
            pie = eng["capex_opex_sugestao"].value_counts().reset_index()
            pie.columns = ["Sugestão","Projetos"]
            fig = px.pie(pie, names="Sugestão", values="Projetos", hole=.55, height=420)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with b:
        with st.container(border=True):
            dep = eng.groupby("empresa")["orcamento_aprovado_total"].sum().reset_index()
            dep["depreciacao_mensal"] = dep["orcamento_aprovado_total"]/120
            fig = px.bar(dep, x="empresa", y="depreciacao_mensal", height=420)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.container(border=True):
        st.dataframe(eng[["empresa","elemento_pep","nome_projeto","orcamento_aprovado_total","capex_opex_sugestao","capex_opex_explicacao"]], use_container_width=True, hide_index=True)

elif menu == "🌱 ESG & Sustentabilidade":
    eng = build_enterprise_engine(df)
    keywords = ["ambiental","energia","eficiência","sustent","carbono","solar"]
    bonus = float(get_param("esg_keyword_bonus",30))
    name_series = eng.get("nome_projeto", pd.Series([""]*len(eng))).fillna("").astype(str).str.lower()
    eng["esg_score"] = np.clip(50 + np.where(name_series.apply(lambda x: any(k in x for k in keywords)), bonus, 0) + (eng.index % 20), 0, 100)
    eng["carbon_avoid_ton"] = (eng["esg_score"] * eng["orcamento_aprovado_total"] / 100000000).round(1)

    st.markdown('<div class="story"><b>ESG CAPEX:</b> indicadores ambientais e sustentabilidade vinculados ao portfólio.</div>', unsafe_allow_html=True)
    e1,e2,e3,e4 = st.columns(4)
    with e1:
        exec_metric_card("ESG médio", f"{eng['esg_score'].mean():.0f}", "0 a 100")
    with e2:
        exec_metric_card("CO₂ evitado", f"{eng['carbon_avoid_ton'].sum():.1f} t", "Estimado")
    with e3:
        exec_metric_card("Projetos ESG fortes", str(int((eng["esg_score"]>=75).sum())), "Score >= 75")
    with e4:
        exec_metric_card("CAPEX ESG", fmt(eng.loc[eng["esg_score"]>=75,"orcamento_aprovado_total"].sum()), "Potencial")

    a,b = st.columns([1.15,1])
    with a:
        with st.container(border=True):
            top = eng.sort_values("esg_score", ascending=False).head(20)
            fig = px.bar(top, x="esg_score", y="elemento_pep", orientation="h", color="esg_score", color_continuous_scale=["#E9494A","#F2C94C","#37C978"], height=460)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with b:
        with st.container(border=True):
            carbon = eng.groupby("empresa")["carbon_avoid_ton"].sum().reset_index()
            fig = px.treemap(carbon, path=["empresa"], values="carbon_avoid_ton", height=460)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#EAF2FF")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


elif menu == "⚙️ Governança & Parâmetros":
    st.markdown(
        '<div class="story"><b>Central de Governança & Parâmetros:</b> ajuste os coeficientes que influenciam risco, health score, maturidade, CAPEX/OPEX, What-if, ROI, ESG e qualidade de dados.</div>',
        unsafe_allow_html=True
    )

    tabs = st.tabs([
        "Risco & Alertas",
        "Health & Maturidade",
        "CAPEX x OPEX",
        "What-if & Forecast",
        "ROI / ESG / Dados",
        "Upload Tabela",
        "Auditoria"
    ])

    with tabs[0]:
        st.markdown('<div class="param-section-title">Limites de risco por CPI, SPI e VAC</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            v = st.number_input("CPI amarelo", 0.0, 2.0, float(get_param("risk_cpi_yellow", .90)), .01)
            audit_param_change("risk_cpi_yellow", get_param("risk_cpi_yellow"), v)
            st.session_state.engine_params["risk_cpi_yellow"] = v
            st.markdown('<div class="config-help">Limite preventivo de custo. Se o CPI cair abaixo desse valor, o projeto entra em atenção.</div>', unsafe_allow_html=True)

            v = st.number_input("CPI vermelho", 0.0, 2.0, float(get_param("risk_cpi_red", .80)), .01)
            audit_param_change("risk_cpi_red", get_param("risk_cpi_red"), v)
            st.session_state.engine_params["risk_cpi_red"] = v
            st.markdown('<div class="config-help">Limite crítico de custo. Abaixo desse valor, o motor pode classificar o projeto como crítico.</div>', unsafe_allow_html=True)

        with c2:
            v = st.number_input("SPI amarelo", 0.0, 2.0, float(get_param("risk_spi_yellow", .90)), .01)
            audit_param_change("risk_spi_yellow", get_param("risk_spi_yellow"), v)
            st.session_state.engine_params["risk_spi_yellow"] = v
            st.markdown('<div class="config-help">Limite preventivo de prazo. SPI abaixo do limite indica perda de ritmo frente ao planejado.</div>', unsafe_allow_html=True)

            v = st.number_input("SPI vermelho", 0.0, 2.0, float(get_param("risk_spi_red", .80)), .01)
            audit_param_change("risk_spi_red", get_param("risk_spi_red"), v)
            st.session_state.engine_params["risk_spi_red"] = v
            st.markdown('<div class="config-help">Limite crítico de prazo. Abaixo desse valor o projeto sinaliza atraso relevante.</div>', unsafe_allow_html=True)

        with c3:
            v = st.number_input("VAC amarelo (%)", -1.0, 1.0, float(get_param("risk_vac_yellow_pct", -.05)), .01)
            audit_param_change("risk_vac_yellow_pct", get_param("risk_vac_yellow_pct"), v)
            st.session_state.engine_params["risk_vac_yellow_pct"] = v
            st.markdown('<div class="config-help">Percentual de desvio negativo tolerado antes de gerar alerta financeiro.</div>', unsafe_allow_html=True)

            v = st.number_input("VAC vermelho (%)", -1.0, 1.0, float(get_param("risk_vac_red_pct", -.10)), .01)
            audit_param_change("risk_vac_red_pct", get_param("risk_vac_red_pct"), v)
            st.session_state.engine_params["risk_vac_red_pct"] = v
            st.markdown('<div class="config-help">Percentual de desvio negativo crítico contra o orçamento aprovado.</div>', unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<div class="param-section-title">Pesos do Health Score</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-help">Controlam a composição do Health Score parametrizado. Quanto maior o peso, maior a influência do indicador.</div>', unsafe_allow_html=True)

        cols = st.columns(5)
        items = [
            ("health_weight_cpi", "CPI"),
            ("health_weight_spi", "SPI"),
            ("health_weight_vac", "VAC"),
            ("health_weight_forecast", "Forecast"),
            ("health_weight_data_quality", "Data Quality"),
        ]
        for col, (key, label) in zip(cols, items):
            with col:
                v = st.number_input(label, 0, 100, int(get_param(key, 20)), 1, key=f"v231_{key}")
                audit_param_change(key, get_param(key), v)
                st.session_state.engine_params[key] = v

        st.markdown('<div class="param-section-title">Pesos do Maturity Score</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-help">Controlam o índice de maturidade do projeto, considerando orçamento, cronograma, avanço físico, custo e forecast.</div>', unsafe_allow_html=True)

        cols = st.columns(5)
        items = [
            ("maturity_weight_budget", "Budget"),
            ("maturity_weight_schedule", "Cronograma"),
            ("maturity_weight_physical_progress", "Avanço Físico"),
            ("maturity_weight_cost_performance", "Custo"),
            ("maturity_weight_forecast", "Forecast"),
        ]
        for col, (key, label) in zip(cols, items):
            with col:
                v = st.number_input(label, 0, 100, int(get_param(key, 20)), 1, key=f"v231_{key}")
                audit_param_change(key, get_param(key), v)
                st.session_state.engine_params[key] = v

    with tabs[2]:
        st.markdown('<div class="param-section-title">Critérios CAPEX x OPEX</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            v = st.number_input("Valor mínimo CAPEX", 0, 100000000, int(get_param("capex_min_value", 1000000)), 10000)
            audit_param_change("capex_min_value", get_param("capex_min_value"), v)
            st.session_state.engine_params["capex_min_value"] = v
            st.markdown('<div class="config-help">Projetos abaixo deste valor podem ser sinalizados para revisão de capitalização.</div>', unsafe_allow_html=True)

        with c2:
            v = st.text_area("Palavras-chave OPEX", str(get_param("capex_opex_keywords", "")), height=110)
            audit_param_change("capex_opex_keywords", get_param("capex_opex_keywords"), v)
            st.session_state.engine_params["capex_opex_keywords"] = v
            st.markdown('<div class="config-help">Termos que sugerem despesa operacional, como manutenção, reparo, adequação ou correção.</div>', unsafe_allow_html=True)

        with c3:
            v = st.number_input("Payback limite OPEX (meses)", 0, 120, int(get_param("capex_payback_limit_months", 12)), 1)
            audit_param_change("capex_payback_limit_months", get_param("capex_payback_limit_months"), v)
            st.session_state.engine_params["capex_payback_limit_months"] = v
            st.markdown('<div class="config-help">Parâmetro de apoio para avaliação econômica e decisão de capitalização.</div>', unsafe_allow_html=True)

    with tabs[3]:
        st.markdown('<div class="param-section-title">Parâmetros do simulador e forecast</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            v = st.number_input("Corte orçamento padrão (%)", 0, 80, int(get_param("whatif_default_budget_cut_pct", 10)), 1)
            audit_param_change("whatif_default_budget_cut_pct", get_param("whatif_default_budget_cut_pct"), v)
            st.session_state.engine_params["whatif_default_budget_cut_pct"] = v
            st.markdown('<div class="config-help">Percentual padrão usado no simulador para redução do orçamento disponível.</div>', unsafe_allow_html=True)

        with c2:
            v = st.number_input("Atraso padrão (meses)", 0, 36, int(get_param("whatif_default_delay_months", 3)), 1)
            audit_param_change("whatif_default_delay_months", get_param("whatif_default_delay_months"), v)
            st.session_state.engine_params["whatif_default_delay_months"] = v
            st.markdown('<div class="config-help">Quantidade de meses usada para simular postergação ou atraso dos projetos.</div>', unsafe_allow_html=True)

        with c3:
            v = st.number_input("Aumento custo/câmbio padrão (%)", -50, 100, int(get_param("whatif_default_fx_cost_pct", 8)), 1)
            audit_param_change("whatif_default_fx_cost_pct", get_param("whatif_default_fx_cost_pct"), v)
            st.session_state.engine_params["whatif_default_fx_cost_pct"] = v
            st.markdown('<div class="config-help">Percentual usado para simular inflação, câmbio, insumos importados ou aumento de custo.</div>', unsafe_allow_html=True)

        with c4:
            options = ["Híbrido", "Linear", "Curva S", "Regressão", "IA"]
            current = str(get_param("forecast_model", "Híbrido"))
            idx = options.index(current) if current in options else 0
            v = st.selectbox("Modelo de forecast", options, index=idx)
            audit_param_change("forecast_model", get_param("forecast_model"), v)
            st.session_state.engine_params["forecast_model"] = v
            st.markdown('<div class="config-help">Modelo conceitual usado como referência para cálculo e explicação do forecast.</div>', unsafe_allow_html=True)

    with tabs[4]:
        st.markdown('<div class="param-section-title">ROI, ESG e qualidade dos dados</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)

        for col, key, label, desc in [
            (c1, "roi_weight_health", "Peso ROI Health", "Influência do Health Score no índice de eficiência do investimento."),
            (c2, "roi_weight_maturity", "Peso ROI Maturidade", "Influência da maturidade do projeto no índice de eficiência."),
            (c3, "roi_weight_risk", "Peso ROI Risco", "Influência do risco financeiro e de prazo no índice de eficiência."),
            (c4, "esg_keyword_bonus", "Bônus palavra-chave ESG", "Pontuação adicional quando o projeto contém termos ligados a ESG ou energia.")
        ]:
            with col:
                v = st.number_input(label, 0, 100, int(get_param(key, 30)), 1, key=f"v231_{key}")
                audit_param_change(key, get_param(key), v)
                st.session_state.engine_params[key] = v
                st.markdown(f'<div class="config-help">{desc}</div>', unsafe_allow_html=True)

        v = st.text_area("Campos obrigatórios Data Quality", str(get_param("data_quality_required_fields", "")), height=90)
        audit_param_change("data_quality_required_fields", get_param("data_quality_required_fields"), v)
        st.session_state.engine_params["data_quality_required_fields"] = v
        st.markdown('<div class="config-help">Lista de campos que impactam o índice de qualidade de dados. Separe os nomes por vírgula.</div>', unsafe_allow_html=True)

    with tabs[5]:
        st.markdown('<div class="param-section-title">Upload de tabela de parâmetros</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-help">Use uma tabela Excel ou CSV com as colunas parametro e valor para atualizar várias regras de uma vez.</div>', unsafe_allow_html=True)

        file_params = st.file_uploader("Upload tabela de parâmetros", type=["xlsx", "csv"], key="param_upload_table_v231")
        if file_params is not None:
            try:
                if file_params.name.lower().endswith(".csv"):
                    ptable = pd.read_csv(file_params)
                else:
                    ptable = pd.read_excel(file_params)

                st.dataframe(ptable, use_container_width=True)

                if {"parametro", "valor"}.issubset(set(ptable.columns)):
                    if st.button("Aplicar parâmetros carregados"):
                        for _, r in ptable.iterrows():
                            k = str(r["parametro"])
                            old = st.session_state.engine_params.get(k)
                            st.session_state.engine_params[k] = r["valor"]
                            audit_param_change(k, old, r["valor"])
                        st.success("Parâmetros aplicados com sucesso.")
                else:
                    st.warning("A tabela precisa conter as colunas: parametro, valor.")
            except Exception as e:
                st.error(f"Erro ao ler tabela: {e}")

    with tabs[6]:
        st.markdown('<div class="param-section-title">Auditoria de alterações</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-help">Registra alterações realizadas nos parâmetros durante a sessão atual.</div>', unsafe_allow_html=True)

        st.dataframe(pd.DataFrame(st.session_state.analytics_audit_log), use_container_width=True, hide_index=True)
        st.download_button(
            "Baixar parâmetros atuais",
            pd.DataFrame([st.session_state.engine_params]).to_csv(index=False).encode("utf-8"),
            "parametros_capexvision.csv",
            "text/csv"
        )



elif menu == "🏢 Empresas & Plantas":
    st.markdown(
        '<div class="story"><b>Empresas & Plantas:</b> o sistema identifica automaticamente as empresas do arquivo carregado e permite vincular uma imagem de planta para cada empresa. Ao alterar o filtro Empresa, a planta do painel muda junto.</div>',
        unsafe_allow_html=True
    )

    empresas_detectadas = get_companies_from_data(s if "s" in globals() else df)

    if not empresas_detectadas:
        st.warning("Nenhuma empresa identificada no campo 'empresa'. Carregue uma base com empresas para vincular plantas.")
    else:
        c1, c2 = st.columns([1, 1])

        with c1:
            with st.container(border=True):
                st.markdown('<div class="ptitle">VINCULAR PLANTA POR EMPRESA</div>', unsafe_allow_html=True)

                selected_company_upload = st.selectbox(
                    "Empresa para vincular imagem",
                    empresas_detectadas,
                    key="company_floorplan_select_v231"
                )
                st.markdown(
                    '<div class="config-help">Selecione a empresa exatamente como aparece no campo empresa da base. A imagem ficará vinculada a este código/nome.</div>',
                    unsafe_allow_html=True
                )

                uploaded_company_img = st.file_uploader(
                    "Upload da planta desta empresa",
                    type=["png", "jpg", "jpeg"],
                    key=f"company_floorplan_upload_v231_{selected_company_upload}"
                )
                st.markdown(
                    '<div class="config-help">Aceita PNG, JPG ou JPEG. Recomenda-se imagem horizontal e limpa da planta/layout da unidade.</div>',
                    unsafe_allow_html=True
                )

                if uploaded_company_img is not None:
                    company_key = normalize_company_key(selected_company_upload)
                    st.session_state.company_floorplan_images[company_key] = image_to_data_url(uploaded_company_img)
                    st.session_state.company_floorplan_names[company_key] = uploaded_company_img.name
                    st.success(f"Imagem vinculada à empresa {company_key}.")

                if selected_company_upload in st.session_state.company_floorplan_names:
                    st.info(f"Imagem atual: {st.session_state.company_floorplan_names[selected_company_upload]}")

                if st.button("Remover imagem desta empresa"):
                    company_key = normalize_company_key(selected_company_upload)
                    st.session_state.company_floorplan_images.pop(company_key, None)
                    st.session_state.company_floorplan_names.pop(company_key, None)
                    st.success("Imagem removida desta empresa.")

        with c2:
            with st.container(border=True):
                st.markdown('<div class="ptitle">EMPRESAS DETECTADAS NA BASE</div>', unsafe_allow_html=True)

                for emp in empresas_detectadas:
                    status = "✅ imagem vinculada" if emp in st.session_state.company_floorplan_names else "⚠ sem imagem"
                    st.markdown(f'<span class="company-tag">{emp} · {status}</span>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="ptitle">REGRA DE EXIBIÇÃO</div>', unsafe_allow_html=True)
                st.markdown(
                    """
                    <div class="rule-box">
                    1. O filtro <b>Empresa</b> controla qual planta aparece no painel.<br>
                    2. Se Empresa = Todas, o sistema exibe a primeira empresa visível que possui imagem.<br>
                    3. Os hotspots respeitam os filtros globais aplicados no painel.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with st.container(border=True):
            st.markdown('<div class="ptitle">PRÉ-VISUALIZAÇÃO DA PLANTA VINCULADA</div>', unsafe_allow_html=True)
            if "empresa" in df.columns:
                preview_df = df[df["empresa"].astype(str).str.strip() == normalize_company_key(selected_company_upload)]
            else:
                preview_df = df
            st.markdown(floor(preview_df, unidade, selected_company_upload), unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="ptitle">PLANTAS CADASTRADAS</div>', unsafe_allow_html=True)

            if st.session_state.company_floorplan_names:
                st.dataframe(
                    pd.DataFrame(
                        [{"Empresa": k, "Arquivo": v} for k, v in st.session_state.company_floorplan_names.items()]
                    ),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhuma planta vinculada ainda.")


elif menu == "◈ Análise Financeira":
    render_kpis()
    c1,c2=st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">Budget x Realizado x Comprometido</div>', unsafe_allow_html=True)
            chart=pd.DataFrame({"Indicador":["Orçado","Realizado","Comprometido","Saldo"],"Valor":[orc,real,comp,sal]})
            fig=px.bar(chart,x="Indicador",y="Valor",color="Indicador",height=450)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#EAF2FF", margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with c2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">Top desvios financeiros</div>', unsafe_allow_html=True)
            add_risk_legend()
            top=df.sort_values("VAC").head(15)
            fig=px.bar(top, x="VAC", y="elemento_pep", orientation="h", height=450, color="risk", color_discrete_map=RISK_COLOR_MAP, category_orders={"risk": RISK_ORDER})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#EAF2FF", margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
elif menu == "◷ Atrasos e Prazos":
    st.markdown(
        '<div class="story"><b>Leitura de prazo:</b> O Gantt mostra a janela planejada de execução. A cor representa a classe de risco e os filtros globais continuam afetando a visualização.</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):
        st.markdown('<div class="ptitle">GANTT DE PROJETOS — PRAZO E RISCO</div><div class="psub">Barra = duração planejada · Cor = risco do projeto · Hover = avanço físico e indicadores.</div>', unsafe_allow_html=True)
        add_risk_legend()

        gantt = prepare_gantt_data(df)

        fig = px.timeline(
            gantt,
            x_start="Inicio",
            x_end="Fim",
            y="Projeto",
            color="Risco",
            color_discrete_map=RISK_COLOR_MAP,
            category_orders={"Risco": RISK_ORDER},
            hover_data={
                "Avanço Planejado": True,
                "Avanço Real": True,
                "orcamento_aprovado_total": ":,.0f",
                "realizado": ":,.0f",
                "CPI": ":.2f",
                "SPI": ":.2f",
                "Inicio": True,
                "Fim": True
            },
            height=620
        )

        fig.update_yaxes(autorange="reversed", title="")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#EAF2FF",
            legend_title_text="Classe de risco",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0)"
            ),
            margin=dict(l=10, r=10, t=60, b=20),
            xaxis_title="Período planejado"
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.container(border=True):
        st.markdown('<div class="ptitle">DETALHE DE PRAZO E AVANÇO</div>', unsafe_allow_html=True)
        detail_cols = ["empresa", "definicao_projeto", "elemento_pep", "avanco_planejado_pct", "avanco_real_pct", "SPI", "risk", "prob_atraso"]
        available = [c for c in detail_cols if c in df.columns]
        st.dataframe(df[available].sort_values("SPI"), use_container_width=True, hide_index=True)


elif menu == "⌖ Mapa de Localizações":
    with st.container(border=True):
        st.markdown('<div class="ptitle">MAPA DE LOCALIZAÇÕES</div><div class="psub">Tamanho = orçamento; cor = risco.</div>', unsafe_allow_html=True)
        add_risk_legend()
        fig=px.scatter_mapbox(df,lat="latitude",lon="longitude",size="orcamento_aprovado_total",color="risk",hover_name="elemento_pep",hover_data=["realizado","EAC","health_score"],zoom=3,height=680,color_discrete_map=RISK_COLOR_MAP)
        fig.update_layout(mapbox_style="carto-darkmatter",margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
elif menu == "▥ Planta da Unidade":
    with st.container(border=True):
        st.markdown('<div class="ptitle">PLANTA INTERATIVA DA UNIDADE</div><div class="psub">Hotspots representam projetos de maior orçamento e risco.</div>', unsafe_allow_html=True)
        st.markdown(floor(df, unidade, empresa), unsafe_allow_html=True)
elif menu == "⚠ Alertas":
    alerts = df[(df["risk"].isin(["Crítico","Alto"])) | (df["VAC"]<0) | (df["CPI"]<1) | (df["SPI"]<1)].copy()
    with st.container(border=True):
        st.markdown('<div class="ptitle">CENTRAL DE ALERTAS</div>', unsafe_allow_html=True)
        st.dataframe(alerts[["empresa","definicao_projeto","elemento_pep","risk","VAC","CPI","SPI","prob_estouro","prob_atraso","health_score"]].sort_values(["risk","health_score"]), use_container_width=True, hide_index=True)
elif menu == "◎ Previsão (EVM)":
    render_kpis()
    st.dataframe(df[["empresa","definicao_projeto","elemento_pep","BAC","PV","EV","AC","CPI","SPI","EAC","ETC","VAC","prob_estouro","prob_atraso","health_score","risk"]], use_container_width=True, hide_index=True)
elif menu == "∿ Curva S":
    with st.container(border=True):
        st.markdown('<div class="ptitle">CURVA S — PROJETADO X REALIZADO</div>', unsafe_allow_html=True)
        months=pd.date_range("2024-01-01", periods=12, freq="MS")
        total_budget=orc if orc else 1
        x=np.linspace(-2,2,12)
        weights=1/(1+np.exp(-x))
        weights=(weights-weights.min())/(weights.max()-weights.min())
        planned=weights/weights[-1]*total_budget
        actual=np.linspace(0,real,12)*np.random.uniform(.9,1.05,12)
        curve=pd.DataFrame({"Mês":months.strftime("%Y-%m"),"Planejado acumulado":planned,"Realizado acumulado":actual})
        fig=px.line(curve,x="Mês",y=["Planejado acumulado","Realizado acumulado"],markers=True,height=560)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#EAF2FF", margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.dataframe(curve, use_container_width=True, hide_index=True)

elif menu == "ⓘ Notas Explicativas":
    with st.container(border=True):
        st.markdown(
            '<div class="ptitle">NOTAS EXPLICATIVAS — SIGLAS, INDICADORES E TERMINOLOGIAS ENTERPRISE</div>',
            unsafe_allow_html=True
        )

        terms = [
            ("BAC", "Budget at Completion: orçamento total aprovado para conclusão do projeto."),
            ("AC", "Actual Cost: custo real incorrido até a data de referência."),
            ("PV", "Planned Value: valor planejado do trabalho que deveria ter sido realizado."),
            ("EV", "Earned Value: valor agregado do trabalho efetivamente realizado."),
            ("CPI", "Cost Performance Index: eficiência de custo. CPI = EV / AC. Abaixo de 1 indica perda de eficiência financeira."),
            ("SPI", "Schedule Performance Index: eficiência de prazo. SPI = EV / PV. Abaixo de 1 indica atraso de avanço físico."),
            ("EAC", "Estimate at Completion: estimativa de custo total ao término do projeto."),
            ("ETC", "Estimate to Complete: estimativa de custo ainda necessário para concluir o projeto."),
            ("VAC", "Variance at Completion: variação estimada contra o orçamento. VAC = BAC - EAC."),
            ("Health Score", "Índice consolidado de saúde do projeto, combinando custo, prazo, forecast, risco e qualidade dos dados."),
            ("Maturity Score", "Índice de maturidade do projeto, avaliando planejamento, orçamento, cronograma, avanço físico e forecast."),
            ("Data Quality Score", "Índice de qualidade dos dados. Mede completude e confiabilidade dos campos obrigatórios configurados."),
            ("Param Risk", "Classificação de risco calculada pelo motor parametrizável da tela Governança & Parâmetros."),
            ("CAPEX", "Capital Expenditure: investimento capitalizável, associado a aquisição, construção ou melhoria de ativo."),
            ("OPEX", "Operational Expenditure: despesa operacional, associada a manutenção, reparo ou gasto recorrente."),
            ("CAPEX x OPEX Intelligence", "Motor que sugere revisão da classificação contábil com base em valor mínimo e palavras-chave configuradas."),
            ("Forecast", "Projeção do resultado futuro do projeto. Pode usar lógica linear, híbrida, curva S, regressão ou IA em evoluções futuras."),
            ("What-if", "Simulador de cenários para testar corte orçamentário, atraso, inflação, câmbio ou aumento de custos."),
            ("ROI", "Return on Investment: retorno estimado do investimento em relação ao capital aplicado."),
            ("Payback", "Prazo estimado para retorno do investimento."),
            ("ESG Score", "Pontuação ambiental, social e de governança aplicada aos projetos com características sustentáveis."),
            ("Carbon Avoidance", "Estimativa de carbono evitado por projetos de eficiência energética, ambiental ou sustentabilidade."),
            ("Pipeline", "Fluxo de aprovação e execução do investimento: ideia, estudo, aprovação, contratação, execução e encerramento."),
            ("SLA", "Service Level Agreement: prazo esperado para conclusão de uma etapa, aprovação ou atendimento."),
            ("Torre de Contratos", "Visão gerencial de fornecedores, saldos contratuais, consumo, aditivos e concentração de risco."),
            ("Benchmark", "Comparação entre projetos semelhantes para identificar eficiência, desvios e oportunidades de melhoria."),
            ("Digital Twin", "Representação visual da planta/unidade com hotspots financeiros e operacionais sobre a imagem."),
            ("Hotspot", "Marcador visual sobre mapa ou planta indicando projeto, risco, orçamento, realizado e consumo."),
            ("Explainable Analytics", "Análise explicável que mostra por que um projeto foi classificado como crítico, OPEX provável ou baixa maturidade."),
            ("Governança Analítica", "Controle de parâmetros, pesos, regras e auditoria que influenciam os resultados do painel."),
            ("Threshold", "Limite configurável usado para disparar alertas ou alterar classificação de risco."),
            ("Peso Analítico", "Coeficiente que define a influência de um indicador dentro de um score composto."),
            ("Curva S", "Representação acumulada do planejado, realizado e forecast ao longo do tempo."),
            ("Risco Crítico", "Alta exposição, geralmente associada a CPI/SPI baixos, VAC negativo ou forecast acima do orçamento."),
            ("Risco Alto", "Atenção executiva relevante, com sinais de desvio financeiro, prazo ou consumo elevado."),
            ("Risco Médio", "Acompanhamento preventivo, sem situação crítica imediata."),
            ("Risco Baixo", "Condição controlada dentro dos parâmetros esperados.")
        ]

        html = '<div class="note-grid">'
        for title, desc in terms:
            html += f'<div class="note"><div class="ntitle">{title}</div><div class="ntext">{desc}</div></div>'
        html += '</div>'

        st.markdown(html, unsafe_allow_html=True)


elif menu == "⚙ Configurações":
    st.markdown('<div class="panel"><div class="ptitle">CONFIGURAÇÕES E GOVERNANÇA</div>', unsafe_allow_html=True)
    st.write("Base carregada:", "Sim" if st.session_state.raw_data is not None else "Dados demonstrativos")
    st.write("Registros no log:", len(st.session_state.load_log))
    st.write("Parâmetros ativos:", len(st.session_state.engine_params))
    st.write("Imagens por empresa:", len(st.session_state.company_floorplan_names))
    st.write("Plantas cadastradas:", len(st.session_state.floorplan_names))
    if st.session_state.floorplan_names:
        st.dataframe(
            pd.DataFrame(
                [{"Unidade": k, "Arquivo": v} for k, v in st.session_state.floorplan_names.items()]
            ),
            use_container_width=True,
            hide_index=True
        )
    
    st.dataframe(pd.DataFrame(st.session_state.load_log), use_container_width=True)
    st.download_button("Baixar análise consolidada em Excel", export_excel(df), file_name="capexvision_v23_3_analise.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)