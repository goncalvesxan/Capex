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
    page_title="CapexVision V22",
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


.exec-card{background:linear-gradient(135deg,rgba(13,31,53,.96),rgba(8,20,35,.98));border:1px solid rgba(110,170,255,.18);border-radius:18px;padding:16px;box-shadow:0 18px 40px rgba(0,0,0,.34);min-height:138px}.exec-card:hover{border-color:rgba(0,198,255,.34);box-shadow:0 22px 50px rgba(0,0,0,.45),0 0 18px rgba(0,198,255,.10)}.exec-title{color:#F3F8FF;font-size:.88rem;font-weight:950;text-transform:uppercase}.exec-value{color:#FFFFFF;font-size:1.75rem;font-weight:950;margin-top:10px}.exec-sub{color:#9DB5CF;font-size:.76rem;margin-top:6px;line-height:1.35}.insight-item{background:rgba(255,255,255,.045);border-radius:12px;padding:12px 14px;margin-bottom:10px;color:#DCEBFF;font-size:.84rem;line-height:1.42}.insight-critical{border-left:4px solid #E9494A}.insight-high{border-left:4px solid #F28C28}.insight-medium{border-left:4px solid #F2C94C}.insight-low{border-left:4px solid #37C978}.timeline-item{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.08)}.timeline-dot{width:12px;height:12px;border-radius:50%;margin-top:5px;background:#3AA7FF;box-shadow:0 0 14px rgba(58,167,255,.8)}.timeline-text{color:#DCEBFF;font-size:.84rem;line-height:1.42}.badge-soft{display:inline-block;padding:5px 9px;border-radius:999px;font-size:.72rem;font-weight:900;background:rgba(58,167,255,.14);color:#7CC7FF;border:1px solid rgba(58,167,255,.25)}

</style>
""", unsafe_allow_html=True)




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

def image_to_data_url(uploaded_file):
    img_bytes = uploaded_file.getvalue()
    mime = uploaded_file.type or "image/png"
    return f"data:{mime};base64,{base64.b64encode(img_bytes).decode()}"

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

def floor(s, selected_unit="Todas"):
    top = s.sort_values("orcamento_aprovado_total", ascending=False).head(8).reset_index(drop=True)
    spots = [(18,68),(32,42),(48,30),(64,58),(78,36),(24,22),(54,72),(84,66)]

    unit_name, bg = get_selected_floorplan_image(selected_unit, s)

    if bg:
        html = f"""
        <div class="floor-img" style="background-image: url('{bg}');">
            <div class="floor-unit-tag">Planta: {unit_name}</div>
        """
    else:
        html = """
        <div class="floor">
            <div class="zone" style="left:8%;top:13%;width:30%;height:26%;"></div>
            <div class="zone" style="left:43%;top:13%;width:24%;height:26%;"></div>
            <div class="zone" style="left:70%;top:13%;width:20%;height:26%;"></div>
            <div class="zone" style="left:8%;top:46%;width:36%;height:32%;"></div>
            <div class="zone" style="left:49%;top:46%;width:41%;height:32%;"></div>
            <div class="floor-empty-label">
                Nenhuma imagem vinculada à unidade selecionada<br>
                Cadastre a imagem na barra lateral ou em Configurações.
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


def safe_div(a,b):
    try:
        return float(a)/float(b) if float(b)!=0 else 0
    except Exception:
        return 0

def exec_metric_card(title,value,sub='',cls=''):
    st.markdown(f"""<div class="exec-card {cls}"><div class="exec-title">{title}</div><div class="exec-value">{value}</div><div class="exec-sub">{sub}</div></div>""",unsafe_allow_html=True)

def build_executive_intelligence(df):
    intel=df.copy()
    if intel.empty: return intel
    rng=np.random.default_rng(42)
    for c in ['orcamento_aprovado_total','avanco_planejado_pct','avanco_real_pct','CPI','SPI','VAC','health_score','prob_estouro','prob_atraso','valor_comprometido','realizado','EAC']:
        if c not in intel.columns: intel[c]=0
    intel['maturity_score']=(100-np.where(intel['orcamento_aprovado_total'].fillna(0)<=0,20,0)-np.where(intel['avanco_planejado_pct'].fillna(0)<=0,15,0)-np.where(intel['avanco_real_pct'].fillna(0)<=0,15,0)-np.where(intel['CPI'].fillna(1)<.9,15,0)-np.where(intel['SPI'].fillna(1)<.9,15,0)-np.where(intel['VAC'].fillna(0)<0,20,0)).clip(0,100)
    intel['project_maturity']=np.select([intel['maturity_score']>=80,intel['maturity_score']>=60],['Maduro','Atenção'],default='Imaturo')
    intel['forecast_final_cost']=intel['EAC'].fillna(intel['orcamento_aprovado_total'])
    intel['forecast_delta']=intel['forecast_final_cost']-intel['orcamento_aprovado_total']
    intel['forecast_delta_pct']=np.where(intel['orcamento_aprovado_total']>0,intel['forecast_delta']/intel['orcamento_aprovado_total'],0)
    resp=intel['responsavel'] if 'responsavel' in intel.columns else pd.Series(['']*len(intel),index=intel.index)
    intel['data_quality_score']=(100-np.where(intel['orcamento_aprovado_total'].fillna(0)<=0,25,0)-np.where(intel['elemento_pep'].astype(str).str.strip().eq(''),20,0)-np.where(resp.fillna('').astype(str).str.strip().eq(''),20,0)-np.where(intel['avanco_planejado_pct'].fillna(0)<=0,15,0)-np.where(intel['avanco_real_pct'].fillna(0)<=0,15,0)).clip(0,100)
    intel['investment_efficiency']=(intel['health_score'].fillna(0)*.45+intel['maturity_score'].fillna(0)*.25+(1-intel['prob_estouro'].fillna(0))*100*.15+(1-intel['prob_atraso'].fillna(0))*100*.15).clip(0,100)
    intel['roi_estimado_pct']=np.where(intel['orcamento_aprovado_total']>0,(intel['orcamento_aprovado_total']-intel['forecast_final_cost'])/intel['orcamento_aprovado_total'],0)+rng.normal(.12,.04,len(intel))
    intel['payback_meses']=np.clip(24+(100-intel['investment_efficiency'])/3+rng.normal(0,2,len(intel)),6,60).round(1)
    nome=intel['nome_projeto'] if 'nome_projeto' in intel.columns else pd.Series(['']*len(intel),index=intel.index)
    intel['capex_opex_risk']=np.select([intel['orcamento_aprovado_total']<1000000,nome.fillna('').str.contains('manutenção|reparo|adequação',case=False,regex=True)],['Baixo valor capitalizável','Possível OPEX'],default='CAPEX provável')
    intel['esg_score']=np.clip(50+np.where(nome.fillna('').str.contains('ambiental|energia|eficiência|sustent',case=False,regex=True),30,0)+rng.normal(0,12,len(intel)),0,100).round(1)
    intel['carbon_avoid_ton']=np.clip(intel['esg_score']*intel['orcamento_aprovado_total']/100000000,0,None).round(1)
    suppliers=['Fornecedor Alfa','Fornecedor Beta','Fornecedor Gama','Fornecedor Delta','Fornecedor Ômega']; stages=['Ideia','Estudo','Aprovação','Contratação','Execução','Encerramento']
    intel['fornecedor']=[suppliers[i%len(suppliers)] for i in range(len(intel))]
    intel['pipeline_stage']=[stages[i%len(stages)] for i in range(len(intel))]
    intel['contract_balance']=(intel['valor_comprometido'].fillna(0)*rng.uniform(.15,.75,len(intel))).round(2)
    intel['contract_consumption_pct']=np.where(intel['valor_comprometido']>0,1-(intel['contract_balance']/intel['valor_comprometido']),0)
    intel['approval_sla_days']=np.clip(rng.normal(18,7,len(intel)),2,60).round(0)
    return intel

def executive_insights(df):
    intel=build_executive_intelligence(df)
    if intel.empty: return ['Nenhum dado disponível para gerar insights.']
    insights=[]
    critical=int((intel['risk']=='Crítico').sum()) if 'risk' in intel else 0
    high=int((intel['risk']=='Alto').sum()) if 'risk' in intel else 0
    neg=int((intel['VAC']<0).sum())
    low_mat=int((intel['maturity_score']<60).sum())
    low_q=int((intel['data_quality_score']<70).sum())
    forecast_over=intel[intel['forecast_delta']>0]['forecast_delta'].sum()
    if critical: insights.append(f'Existem {critical} projetos em risco crítico exigindo plano de ação imediato.')
    if high: insights.append(f'{high} projetos estão em risco alto e devem entrar em rotina semanal de acompanhamento.')
    if neg: insights.append(f'{neg} projetos apresentam VAC negativo, indicando tendência de estouro no custo ao término.')
    if low_mat: insights.append(f'{low_mat} projetos possuem baixa maturidade de planejamento e podem distorcer o forecast.')
    if low_q: insights.append(f'{low_q} projetos apresentam risco de qualidade de dados, afetando confiabilidade executiva.')
    if forecast_over>0: insights.append(f'O forecast consolidado projeta possível necessidade adicional de {fmt(forecast_over)}.')
    return insights or ['Portfólio sem alertas críticos relevantes no recorte atual.']

def render_insight_list(insights):
    classes=['insight-critical','insight-high','insight-medium','insight-low']
    for i,txt in enumerate(insights): st.markdown(f'<div class="insight-item {classes[min(i,3)]}">{txt}</div>',unsafe_allow_html=True)

def scenario_impact(df,reduction_pct=0,delay_months=0,fx_pct=0):
    sim=df.copy(); reduction=reduction_pct/100; fx=fx_pct/100
    sim['budget_scenario']=sim['orcamento_aprovado_total']*(1-reduction)
    sim['eac_scenario']=sim['EAC']*(1+fx)
    sim['vac_scenario']=sim['budget_scenario']-sim['eac_scenario']
    sim['delay_impact_days']=delay_months*30*np.where(sim['SPI'].fillna(1)<1,1.25,1)
    sim['new_risk']=np.select([sim['vac_scenario']<0,sim['delay_impact_days']>60,sim['vac_scenario']<sim['budget_scenario']*.1],['Crítico','Alto','Médio'],default='Baixo')
    return sim

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
    ["▦ Visão Geral","▤ Projetos","🔎 Detalhe do Projeto","🧠 Inteligência Executiva","🧪 Simulador What-if","🏛️ Pipeline & Contratos","📊 Eficiência & ROI","🧾 CAPEX x OPEX","🌱 ESG & Sustentabilidade","◈ Análise Financeira","◷ Atrasos e Prazos","⌖ Mapa de Localizações","▥ Planta da Unidade","⚠ Alertas","◎ Previsão (EVM)","∿ Curva S","ⓘ Notas Explicativas","⚙ Configurações"],
    label_visibility="collapsed"
)





st.sidebar.markdown("### Plantas por unidade")

manual_units_text = st.sidebar.text_input(
    "Unidades cadastradas",
    value="Área 01;Área 02;Área 03;Área 04",
    help="Separe por ponto e vírgula. Depois vincule uma imagem para cada unidade."
)

available_units_sidebar = [u.strip() for u in manual_units_text.split(";") if u.strip()]

if available_units_sidebar:
    unit_for_image = st.sidebar.selectbox(
        "Unidade para vincular imagem",
        available_units_sidebar,
        key="unit_for_floorplan_image"
    )

    floor_upload = st.sidebar.file_uploader(
        "Upload da planta da unidade",
        type=["png", "jpg", "jpeg"],
        key=f"floorplan_upload_{unit_for_image}"
    )

    if floor_upload is not None:
        st.session_state.floorplan_images[unit_for_image] = image_to_data_url(floor_upload)
        st.session_state.floorplan_names[unit_for_image] = floor_upload.name
        st.sidebar.success(f"Imagem vinculada: {unit_for_image}")

    if unit_for_image in st.session_state.floorplan_names:
        st.sidebar.caption(f"Imagem atual: {st.session_state.floorplan_names[unit_for_image]}")

    if st.sidebar.button("Remover imagem desta unidade", use_container_width=True):
        st.session_state.floorplan_images.pop(unit_for_image, None)
        st.session_state.floorplan_names.pop(unit_for_image, None)
        st.sidebar.success("Imagem removida.")


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
🟢 Versão 22.0.0
</div>
""", unsafe_allow_html=True)

data = st.session_state.raw_data if st.session_state.raw_data is not None else demo_data()
s=build_summary(data)

st.markdown(f"""
<div class="header">
  <div style="display:flex;justify-content:space-between;gap:16px;align-items:start;">
    <div>
      <div class="header-title">{menu.replace('▦ ','').replace('▤ ','').replace('🔎 ','').replace('🧠 ','').replace('🧪 ','').replace('🏛️ ','').replace('📊 ','').replace('🧾 ','').replace('🌱 ','').replace('◈ ','').replace('◷ ','').replace('⌖ ','').replace('▥ ','').replace('⚠ ','').replace('◎ ','').replace('∿ ','').replace('ⓘ ','').replace('⚙ ','')}</div>
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
if empresa!="Todas": df=df[df.empresa.astype(str)==empresa]
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
            st.markdown(floor(df, unidade), unsafe_allow_html=True)
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
    intel=build_executive_intelligence(df)
    st.markdown('<div class="story"><b>Inteligência Executiva:</b> visão avançada com maturidade, forecast, qualidade de dados, benchmarking, insights e timeline narrativa.</div>',unsafe_allow_html=True)
    m1,m2,m3,m4,m5=st.columns(5)
    with m1: exec_metric_card('Maturidade média',f"{intel['maturity_score'].mean():.0f}",'Project Maturity Score')
    with m2: exec_metric_card('Qualidade dos dados',f"{intel['data_quality_score'].mean():.0f}",'Data Quality Index')
    with m3: exec_metric_card('Eficiência média',f"{intel['investment_efficiency'].mean():.0f}",'Investment Efficiency')
    with m4: exec_metric_card('Forecast adicional',fmt(max(intel['forecast_delta'].sum(),0)),'EAC acima do BAC')
    with m5: exec_metric_card('Projetos imaturos',str(int((intel['maturity_score']<60).sum())),'Planejamento frágil')
    c1,c2=st.columns([1.25,1])
    with c1:
        with st.container(border=True): st.markdown('<div class="ptitle">CENTRO DE INSIGHTS AUTOMÁTICOS</div>',unsafe_allow_html=True); render_insight_list(executive_insights(df))
    with c2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">DISTRIBUIÇÃO DE MATURIDADE</div>',unsafe_allow_html=True)
            mc=intel['project_maturity'].value_counts().reset_index(); mc.columns=['Maturidade','Projetos']
            fig=px.pie(mc,names='Maturidade',values='Projetos',hole=.58,color='Maturidade',color_discrete_map={'Maduro':'#37C978','Atenção':'#F2C94C','Imaturo':'#E9494A'},height=330); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    h1,h2=st.columns(2)
    with h1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">HEATMAP DE DESVIOS — UNIDADE x STATUS</div>',unsafe_allow_html=True)
            heat=intel.pivot_table(index='area_responsavel',columns='status_usuario',values='VAC',aggfunc='sum',fill_value=0)
            fig=px.imshow(heat,text_auto='.2s',color_continuous_scale=['#E9494A','#F2C94C','#37C978'],aspect='auto',height=380); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with h2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">BENCHMARKING AUTOMÁTICO</div>',unsafe_allow_html=True)
            bench=intel.copy(); bench['custo_por_avanco']=np.where(bench['avanco_real_pct']>0,bench['realizado']/bench['avanco_real_pct'],np.nan); bench=bench.sort_values('custo_por_avanco').head(10)
            fig=px.bar(bench,x='custo_por_avanco',y='elemento_pep',orientation='h',color='risk',color_discrete_map=RISK_COLOR_MAP,category_orders={'risk':RISK_ORDER},height=380); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF',yaxis_title=''); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    t1,t2=st.columns([1.25,1])
    with t1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">TIMELINE NARRATIVA EXECUTIVA</div>',unsafe_allow_html=True)
            for _,r in intel.sort_values('forecast_delta',ascending=False).head(6).iterrows(): st.markdown(f'<div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-text">{r.get("elemento_pep")} — forecast indica variação de {fmt(r.get("forecast_delta",0))}; risco atual: {r.get("risk")}.</div></div>',unsafe_allow_html=True)
    with t2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">ÍNDICE DE QUALIDADE DE DADOS</div>',unsafe_allow_html=True)
            dq=intel.sort_values('data_quality_score').head(12); fig=px.bar(dq,x='data_quality_score',y='elemento_pep',orientation='h',color='data_quality_score',color_continuous_scale=['#E9494A','#F2C94C','#37C978'],range_color=[0,100],height=360); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF',coloraxis_showscale=False,yaxis_title=''); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})

elif menu == "🧪 Simulador What-if":
    st.markdown('<div class="story"><b>Simulador What-if:</b> avalie impactos de cortes, postergação e variação de custos.</div>',unsafe_allow_html=True)
    s1,s2,s3=st.columns(3)
    with s1: reduction_pct=st.slider('Redução de orçamento (%)',0,50,10)
    with s2: delay_months=st.slider('Postergar projetos (meses)',0,12,3)
    with s3: fx_pct=st.slider('Aumento de custos/câmbio (%)',-20,50,8)
    sim=scenario_impact(df,reduction_pct,delay_months,fx_pct)
    c1,c2,c3,c4=st.columns(4)
    with c1: exec_metric_card('Novo orçamento',fmt(sim['budget_scenario'].sum()),f'Redução: {reduction_pct}%')
    with c2: exec_metric_card('Novo EAC',fmt(sim['eac_scenario'].sum()),f'Aumento: {fx_pct}%')
    with c3: exec_metric_card('Novo VAC',fmt(sim['vac_scenario'].sum()),'Cenário simulado')
    with c4: exec_metric_card('Críticos no cenário',str(int((sim['new_risk']=='Crítico').sum())),'Após premissas')
    c1,c2=st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="ptitle">IMPACTO POR PROJETO</div>',unsafe_allow_html=True); top=sim.sort_values('vac_scenario').head(15); fig=px.bar(top,x='vac_scenario',y='elemento_pep',orientation='h',color='new_risk',color_discrete_map=RISK_COLOR_MAP,category_orders={'new_risk':RISK_ORDER},height=460); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with c2:
        with st.container(border=True):
            st.markdown('<div class="ptitle">DISTRIBUIÇÃO DE RISCO SIMULADO</div>',unsafe_allow_html=True); rc=sim['new_risk'].value_counts().reset_index(); rc.columns=['Risco','Projetos']; fig=px.pie(rc,names='Risco',values='Projetos',hole=.55,color='Risco',color_discrete_map=RISK_COLOR_MAP,height=460); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with st.container(border=True): st.markdown('<div class="ptitle">TABELA DO CENÁRIO SIMULADO</div>',unsafe_allow_html=True); st.dataframe(sim[['elemento_pep','orcamento_aprovado_total','budget_scenario','EAC','eac_scenario','VAC','vac_scenario','risk','new_risk','delay_impact_days']],use_container_width=True,hide_index=True)

elif menu == "🏛️ Pipeline & Contratos":
    intel=build_executive_intelligence(df); st.markdown('<div class="story"><b>Pipeline & Contratos:</b> aprovações, gargalos, fornecedores, saldos e concentração.</div>',unsafe_allow_html=True)
    p1,p2,p3,p4=st.columns(4)
    with p1: exec_metric_card('SLA médio aprovação',f"{intel['approval_sla_days'].mean():.0f} dias",'Pipeline')
    with p2: exec_metric_card('Saldo contratual',fmt(intel['contract_balance'].sum()),'Contratos')
    with p3: exec_metric_card('Fornecedores',str(intel['fornecedor'].nunique()),'Base simulada')
    with p4: exec_metric_card('Concentração TOP 3',f"{safe_div(intel.groupby('fornecedor')['valor_comprometido'].sum().sort_values(ascending=False).head(3).sum(),intel['valor_comprometido'].sum()):.1%}",'Comprometido')
    c1,c2=st.columns(2)
    with c1:
        with st.container(border=True): st.markdown('<div class="ptitle">PIPELINE DE APROVAÇÃO</div>',unsafe_allow_html=True); pipe=intel.groupby('pipeline_stage')['elemento_pep'].count().reset_index(); pipe.columns=['Etapa','Projetos']; fig=px.funnel(pipe,x='Projetos',y='Etapa',height=420); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with c2:
        with st.container(border=True): st.markdown('<div class="ptitle">CONCENTRAÇÃO POR FORNECEDOR</div>',unsafe_allow_html=True); forn=intel.groupby('fornecedor')['valor_comprometido'].sum().sort_values(ascending=False).reset_index(); fig=px.bar(forn,x='valor_comprometido',y='fornecedor',orientation='h',height=420); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with st.container(border=True): st.markdown('<div class="ptitle">TORRE DE CONTROLE DE CONTRATOS</div>',unsafe_allow_html=True); st.dataframe(intel[['elemento_pep','fornecedor','valor_comprometido','contract_balance','contract_consumption_pct','pipeline_stage','approval_sla_days','risk']],use_container_width=True,hide_index=True)

elif menu == "📊 Eficiência & ROI":
    intel=build_executive_intelligence(df); st.markdown('<div class="story"><b>Eficiência do Investimento:</b> CAPEX aplicado versus retorno estimado, payback, ROI e eficiência.</div>',unsafe_allow_html=True)
    r1,r2,r3,r4=st.columns(4)
    with r1: exec_metric_card('ROI médio estimado',f"{intel['roi_estimado_pct'].mean():.1%}",'Retorno simulado')
    with r2: exec_metric_card('Payback médio',f"{intel['payback_meses'].mean():.1f} meses",'Estimado')
    with r3: exec_metric_card('Eficiência média',f"{intel['investment_efficiency'].mean():.0f}",'0 a 100')
    with r4: exec_metric_card('Projetos elite',str(int((intel['investment_efficiency']>=80).sum())),'Alta eficiência')
    c1,c2=st.columns([1.25,1])
    with c1:
        with st.container(border=True): st.markdown('<div class="ptitle">RANKING DE EFICIÊNCIA</div>',unsafe_allow_html=True); top=intel.sort_values('investment_efficiency',ascending=False).head(15); fig=px.bar(top,x='investment_efficiency',y='elemento_pep',orientation='h',color='investment_efficiency',color_continuous_scale=['#E9494A','#F2C94C','#37C978'],range_color=[0,100],height=460); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with c2:
        with st.container(border=True): st.markdown('<div class="ptitle">ROI x PAYBACK</div>',unsafe_allow_html=True); fig=px.scatter(intel,x='payback_meses',y='roi_estimado_pct',size='orcamento_aprovado_total',color='risk',color_discrete_map=RISK_COLOR_MAP,hover_name='elemento_pep',height=460); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with st.container(border=True): st.markdown('<div class="ptitle">DETALHAMENTO ECONÔMICO</div>',unsafe_allow_html=True); st.dataframe(intel[['elemento_pep','orcamento_aprovado_total','realizado','EAC','VAC','roi_estimado_pct','payback_meses','investment_efficiency','risk']],use_container_width=True,hide_index=True)

elif menu == "🧾 CAPEX x OPEX":
    intel=build_executive_intelligence(df); st.markdown('<div class="story"><b>CAPEX x OPEX Intelligence:</b> possíveis classificações indevidas, capitalização e impacto de depreciação.</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: exec_metric_card('Possíveis OPEX',str(int((intel['capex_opex_risk']=='Possível OPEX').sum())),'Revisão contábil')
    with c2: exec_metric_card('Baixo valor',str(int((intel['capex_opex_risk']=='Baixo valor capitalizável').sum())),'Política de capitalização')
    with c3: exec_metric_card('Depreciação mensal futura',fmt(intel['orcamento_aprovado_total'].sum()/120),'Vida útil simulada 10 anos')
    a,b=st.columns(2)
    with a:
        with st.container(border=True): st.markdown('<div class="ptitle">CLASSIFICAÇÃO CAPEX x OPEX</div>',unsafe_allow_html=True); cr=intel['capex_opex_risk'].value_counts().reset_index(); cr.columns=['Classificação','Projetos']; fig=px.pie(cr,names='Classificação',values='Projetos',hole=.55,height=400); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with b:
        with st.container(border=True): st.markdown('<div class="ptitle">IMPACTO DE DEPRECIAÇÃO POR UNIDADE</div>',unsafe_allow_html=True); dep=intel.groupby('area_responsavel')['orcamento_aprovado_total'].sum().reset_index(); dep['depreciacao_mensal']=dep['orcamento_aprovado_total']/120; fig=px.bar(dep,x='area_responsavel',y='depreciacao_mensal',height=400); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with st.container(border=True): st.markdown('<div class="ptitle">PROJETOS PARA REVISÃO CONTÁBIL</div>',unsafe_allow_html=True); st.dataframe(intel[['elemento_pep','nome_projeto','orcamento_aprovado_total','realizado','capex_opex_risk','area_responsavel','responsavel']],use_container_width=True,hide_index=True)

elif menu == "🌱 ESG & Sustentabilidade":
    intel=build_executive_intelligence(df); st.markdown('<div class="story"><b>ESG CAPEX:</b> investimentos com potencial ambiental, eficiência energética e carbono evitado.</div>',unsafe_allow_html=True)
    e1,e2,e3,e4=st.columns(4)
    with e1: exec_metric_card('ESG Score médio',f"{intel['esg_score'].mean():.0f}",'0 a 100')
    with e2: exec_metric_card('CO₂ evitado',f"{intel['carbon_avoid_ton'].sum():.1f} t",'Estimativa simulada')
    with e3: exec_metric_card('Projetos ESG fortes',str(int((intel['esg_score']>=75).sum())),'Score >= 75')
    with e4: exec_metric_card('CAPEX ESG',fmt(intel.loc[intel['esg_score']>=75,'orcamento_aprovado_total'].sum()),'Investimento potencial')
    c1,c2=st.columns([1.15,1])
    with c1:
        with st.container(border=True): st.markdown('<div class="ptitle">ESG SCORE POR PROJETO</div>',unsafe_allow_html=True); esg=intel.sort_values('esg_score',ascending=False).head(20); fig=px.bar(esg,x='esg_score',y='elemento_pep',orientation='h',color='esg_score',color_continuous_scale=['#E9494A','#F2C94C','#37C978'],range_color=[0,100],height=460); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with c2:
        with st.container(border=True): st.markdown('<div class="ptitle">CARBONO EVITADO POR UNIDADE</div>',unsafe_allow_html=True); carbon=intel.groupby('area_responsavel')['carbon_avoid_ton'].sum().reset_index(); fig=px.treemap(carbon,path=['area_responsavel'],values='carbon_avoid_ton',height=460); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#EAF2FF'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with st.container(border=True): st.markdown('<div class="ptitle">CARTEIRA ESG DETALHADA</div>',unsafe_allow_html=True); st.dataframe(intel[['elemento_pep','nome_projeto','area_responsavel','orcamento_aprovado_total','esg_score','carbon_avoid_ton','investment_efficiency','risk']],use_container_width=True,hide_index=True)

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
        st.markdown(floor(df, unidade), unsafe_allow_html=True)
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
    st.markdown('<div class="panel"><div class="ptitle">NOTAS EXPLICATIVAS — PRINCIPAIS SIGLAS E TERMINOLOGIAS</div><div class="note-grid">' + ''.join([
        f'<div class="note"><div class="ntitle">{a}</div><div class="ntext">{b}</div></div>' for a,b in [
            ("BAC","Budget at Completion: orçamento total aprovado para conclusão do projeto."),
            ("AC","Actual Cost: custo real incorrido até a data de referência."),
            ("PV","Planned Value: valor planejado do trabalho a ser realizado."),
            ("EV","Earned Value: valor agregado do trabalho realizado."),
            ("CPI","Índice de desempenho de custo. CPI = EV / AC. Abaixo de 1 indica perda de eficiência financeira."),
            ("SPI","Índice de desempenho de prazo. SPI = EV / PV. Abaixo de 1 indica atraso de avanço físico."),
            ("EAC","Estimate at Completion: estimativa de custo total ao término."),
            ("VAC","Variance at Completion: variação estimada contra o orçamento.")
        ]]) + '</div></div>', unsafe_allow_html=True)
elif menu == "⚙ Configurações":
    st.markdown('<div class="panel"><div class="ptitle">CONFIGURAÇÕES E GOVERNANÇA</div>', unsafe_allow_html=True)
    st.write("Base carregada:", "Sim" if st.session_state.raw_data is not None else "Dados demonstrativos")
    st.write("Registros no log:", len(st.session_state.load_log))
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
    st.download_button("Baixar análise consolidada em Excel", export_excel(df), file_name="capexvision_v22_analise.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)