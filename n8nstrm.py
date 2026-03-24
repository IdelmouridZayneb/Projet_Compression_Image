"""
app_presentation.py — PixelMind AI · Light Premium Design
Lance avec : streamlit run app_presentation.py
Adapté pour server_groq.py (Groq LLM — port 5000)
"""

import streamlit as st
import requests, base64, json, re, time, io, os, zipfile
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

try:
    from streamlit_extras.add_vertical_space import add_vertical_space
except ImportError:
    def add_vertical_space(n):
        for _ in range(n): st.write("")

def var_text(): return '#1A1F2E'

SERVER_URL      = "http://127.0.0.1:5000"
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/compression-pipeline"
# Pour le mode production (workflow activé) :
# N8N_WEBHOOK_URL = "http://localhost:5678/webhook/compression-pipeline"

RAPPORTS_DIR = r"C:\Users\Lenovo ThinkPad T470\OneDrive\Documents\Bureau\Projet_Compression\rapports"

st.set_page_config(page_title="PixelMind AI", layout="wide", page_icon="🧠", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg:#F8F7FF;--bg2:#FFFFFF;--bg3:#F2F0FC;--card:#FFFFFF;
  --border:#E8E4F8;--violet:#7C5CBF;--pink:#E8559A;
  --gold:#E5A800;--green:#22C55E;--red:#EF4444;
  --text:#1A1F2E;--muted:#6B7280;--shadow:rgba(124,92,191,0.1);
  --grad:linear-gradient(135deg,#7C5CBF 0%,#E8559A 100%);
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;}
.stApp{background:var(--bg)!important;}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:var(--bg3)}::-webkit-scrollbar-thumb{background:var(--violet);border-radius:10px}
[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid var(--border)!important;box-shadow:2px 0 20px rgba(124,92,191,0.06)!important;}
[data-testid="stSidebar"] *{color:var(--text)!important;}
section[data-testid="stSidebar"]>div{padding:0!important;}
[data-testid="stSidebar"] .stButton>button{
  background:transparent!important;color:var(--muted)!important;
  border:1px solid var(--border)!important;border-radius:10px!important;
  box-shadow:none!important;font-weight:500!important;font-size:0.84rem!important;
  padding:9px 14px!important;transition:all 0.2s!important;margin-bottom:3px!important;
  transform:none!important;filter:none!important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  background:var(--bg3)!important;color:var(--violet)!important;
  border-color:rgba(124,92,191,0.35)!important;transform:none!important;box-shadow:none!important;
}
.main .block-container{padding:0 2.5rem 3rem 2.5rem!important;max-width:1400px;background:var(--bg)!important;}
.hero-wrap{min-height:85vh;display:flex;flex-direction:column;justify-content:center;padding:60px 0 40px;position:relative;overflow:hidden;}
.hero-glow-1{position:absolute;top:-100px;right:-60px;width:450px;height:450px;border-radius:50%;background:radial-gradient(circle,rgba(124,92,191,0.1) 0%,transparent 70%);pointer-events:none;}
.hero-glow-2{position:absolute;bottom:-80px;left:-40px;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(232,85,154,0.08) 0%,transparent 70%);pointer-events:none;}
.hero-chip{display:inline-flex;align-items:center;gap:8px;background:rgba(124,92,191,0.08);border:1px solid rgba(124,92,191,0.25);color:var(--violet)!important;padding:6px 16px;border-radius:100px;font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:24px;width:fit-content;}
.hero-chip::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--violet);animation:blink 1.8s infinite;}
.hero-title{font-size:clamp(2.4rem,5vw,3.8rem)!important;font-weight:800!important;line-height:1.1!important;letter-spacing:-1.5px!important;color:var(--text)!important;margin-bottom:18px!important;}
.hero-title .grad{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.hero-sub{font-size:1.05rem!important;color:var(--muted)!important;max-width:500px;line-height:1.75;margin-bottom:32px!important;}
.hero-tags{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:44px;}
.hero-tag{background:white;border:1px solid var(--border);color:var(--muted)!important;padding:6px 14px;border-radius:8px;font-size:0.77rem;font-weight:500;box-shadow:0 1px 4px var(--shadow);}
.hero-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;max-width:480px;}
.hero-stat{background:white;border:1px solid var(--border);border-radius:14px;padding:18px 14px;text-align:center;box-shadow:0 2px 12px var(--shadow);transition:transform 0.2s,box-shadow 0.2s;}
.hero-stat:hover{transform:translateY(-3px);box-shadow:0 6px 20px var(--shadow);}
.hero-stat-val{font-size:1.6rem;font-weight:800;font-family:'JetBrains Mono',monospace;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.hero-stat-lbl{font-size:0.68rem;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:1px;}
.sec-hd{font-size:0.65rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;gap:12px;margin:32px 0 16px;}
.sec-hd::after{content:'';flex:1;height:1px;background:var(--border);}
.card{background:white;border:1px solid var(--border);border-radius:16px;padding:22px;margin-bottom:16px;box-shadow:0 2px 12px var(--shadow);transition:box-shadow 0.2s,transform 0.2s;}
.card:hover{box-shadow:0 6px 24px var(--shadow);transform:translateY(-1px);}
.m-tile{background:white;border:1px solid var(--border);border-radius:14px;padding:18px 14px;text-align:center;position:relative;overflow:hidden;box-shadow:0 2px 10px var(--shadow);transition:all 0.25s;}
.m-tile::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--grad);}
.m-tile:hover{box-shadow:0 8px 24px rgba(124,92,191,0.18);transform:translateY(-2px);}
.m-val{font-size:1.7rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--text);line-height:1;margin:8px 0 4px;}
.m-lbl{font-size:0.65rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);}
.m-sub{font-size:0.72rem;color:var(--violet);margin-top:3px;font-weight:500;}
.dash-card{background:white;border:1px solid var(--border);border-radius:14px;padding:20px;box-shadow:0 2px 12px var(--shadow);transition:all 0.2s;}
.dash-card:hover{box-shadow:0 8px 24px var(--shadow);transform:translateY(-2px);}
.dash-card-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:12px;}
.dash-card-val{font-size:1.6rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--text);}
.dash-card-lbl{font-size:0.75rem;color:var(--muted);margin-top:3px;}
.ag-row{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0;}
.ag-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:8px;font-size:0.77rem;font-weight:600;border:1px solid transparent;transition:all 0.3s;}
.ag-wait{background:#F9F9F9;color:var(--muted);border-color:var(--border);}
.ag-run{background:rgba(124,92,191,0.08);color:var(--violet);border-color:rgba(124,92,191,0.25);animation:pulse 1.2s infinite;}
.ag-done{background:rgba(34,197,94,0.08);color:#16A34A;border-color:rgba(34,197,94,0.25);}
.ag-error{background:rgba(239,68,68,0.08);color:#DC2626;border-color:rgba(239,68,68,0.25);}
.tag{display:inline-block;padding:3px 10px;border-radius:6px;font-size:0.72rem;font-weight:600;background:rgba(124,92,191,0.08);color:var(--violet);border:1px solid rgba(124,92,191,0.2);}
.rpt{background:var(--bg3);border:1px solid var(--border);border-radius:12px;padding:16px 20px;font-size:0.87rem;line-height:2;color:var(--text);margin:10px 0;}
.hist-wrap{background:white;border:1px solid var(--border);border-radius:14px;overflow:hidden;box-shadow:0 2px 12px var(--shadow);}
.hist-row{display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr 90px;gap:12px;padding:12px 16px;font-size:0.82rem;align-items:center;border-bottom:1px solid var(--border);}
.hist-row:last-child{border-bottom:none;}
.hist-header{color:var(--muted);font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;background:var(--bg3);}
.ch-badge{background:rgba(229,168,0,0.1);color:var(--gold);border:1px solid rgba(229,168,0,0.25);padding:4px 12px;border-radius:8px;font-size:0.73rem;font-weight:600;}
.stButton>button{background:var(--grad)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:700!important;font-size:0.88rem!important;padding:12px 24px!important;width:100%!important;transition:all 0.3s cubic-bezier(0.4,0,0.2,1)!important;box-shadow:0 4px 15px rgba(124,92,191,0.3)!important;}
.stButton>button:hover{box-shadow:0 8px 25px rgba(232,85,154,0.4)!important;transform:translateY(-2px) scale(1.01)!important;filter:brightness(1.05)!important;}
.stButton>button:active{transform:translateY(0) scale(0.98)!important;}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:white;border:1px solid var(--border);border-radius:12px;padding:4px;margin-bottom:24px;box-shadow:0 2px 8px var(--shadow);}
.stTabs [data-baseweb="tab"]{border-radius:9px!important;font-weight:600!important;font-size:0.85rem!important;color:var(--muted)!important;padding:8px 20px!important;border:none!important;}
.stTabs [aria-selected="true"]{background:var(--grad)!important;color:white!important;box-shadow:0 4px 12px rgba(124,92,191,0.3)!important;}
.streamlit-expanderHeader{background:white!important;border:1px solid var(--border)!important;border-radius:12px!important;color:var(--text)!important;font-weight:600!important;box-shadow:0 1px 4px var(--shadow)!important;}
.streamlit-expanderHeader:hover{border-color:rgba(124,92,191,0.35)!important;}
[data-testid="stFileUploader"]{border:2px dashed rgba(124,92,191,0.3)!important;border-radius:14px!important;background:var(--bg3)!important;}
.sb-logo{padding:24px 18px 18px;border-bottom:1px solid var(--border);}
.sb-logo-name{font-size:1.05rem;font-weight:800;letter-spacing:-0.3px;color:var(--text);}
.sb-logo-name span{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.sb-logo-sub{font-size:0.62rem;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;margin-top:3px;}
.sb-section-lbl{font-size:0.6rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);padding:14px 18px 6px;}
.sb-agent{display:flex;align-items:center;gap:10px;padding:9px 16px;border-radius:10px;margin:2px 8px;border:1px solid transparent;transition:all 0.2s;}
.sb-agent:hover{background:var(--bg3);border-color:var(--border);}
.sb-agent-icon{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;background:var(--bg3);flex-shrink:0;}
.sb-agent-name{font-size:.82rem;font-weight:600;color:var(--text);}
.sb-agent-who{font-size:.65rem;color:var(--muted);}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;}
.dot-g{background:#22C55E;box-shadow:0 0 7px #22C55E88;animation:blink 2s infinite;}
.dot-o{background:var(--gold);}
.dot-m{background:#D1D5DB;}
#MainMenu{visibility:hidden}footer{visibility:hidden}header{visibility:hidden}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.6}}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.anim-1{animation:fadeUp 0.4s 0.1s both}
.anim-2{animation:fadeUp 0.4s 0.2s both}
.anim-3{animation:fadeUp 0.4s 0.3s both}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = True

def toggle_sidebar():
    st.session_state.show_sidebar = not st.session_state.show_sidebar

st.markdown("""
<style>
.sidebar-toggle {
    position: fixed; top: 20px; left: 20px; z-index: 99999;
    background: linear-gradient(135deg, #7C5CBF 0%, #E8559A 100%);
    color: white; border: none; border-radius: 50px; padding: 10px 18px;
    font-size: 14px; font-weight: 600; cursor: pointer;
    box-shadow: 0 4px 15px rgba(124,92,191,0.3);
}
</style>
""", unsafe_allow_html=True)

arrow    = "◀" if st.session_state.show_sidebar else "▶"
btn_text = "Fermer menu" if st.session_state.show_sidebar else "Ouvrir menu"
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button(f"{arrow} {btn_text}", key="menu_btn", use_container_width=True):
        toggle_sidebar()
        st.rerun()

if "page"    not in st.session_state: st.session_state["page"]    = "accueil"
if "history" not in st.session_state: st.session_state["history"] = []

def check_server():
    try: return requests.get(f"{SERVER_URL}/health", timeout=3).status_code == 200
    except: return False

def call_agent(endpoint, payload, timeout=120):
    try:
        r = requests.post(f"{SERVER_URL}/{endpoint}", json=payload, timeout=timeout)
        return json.loads(r.content)
    except json.JSONDecodeError as e:
        return {"error": f"JSON invalide : {e}"}
    except Exception as e:
        return {"error": str(e)}

def compute_eval(ssim_val):
    try:
        sv = float(ssim_val)
        if sv >= 0.95: return "Excellent"
        if sv >= 0.90: return "Bon"
        if sv >= 0.80: return "Acceptable"
        return "Dégradé"
    except:
        return "?"

# ══════════════════════════════════════════════════════
# UTILITAIRES — safe_dict + safe_b64decode
# ══════════════════════════════════════════════════════

def safe_dict(val):
    """Convertit une string JSON en dict, ou retourne le dict tel quel."""
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, dict):
                return parsed
        except:
            pass
    return {}

def safe_b64decode(s):
    """
    Décode base64 en gérant :
    - padding manquant (erreur binascii)
    - préfixe data:image/...;base64,
    - espaces / sauts de ligne ajoutés par n8n
    """
    if not s:
        return None
    try:
        if isinstance(s, str):
            # Supprimer préfixe data:image si présent
            if ',' in s and s.startswith('data:'):
                s = s.split(',', 1)[1]
            # Nettoyer espaces et sauts de ligne ajoutés par n8n
            s = s.strip().replace('\n', '').replace('\r', '').replace(' ', '')
        # Corriger le padding manquant
        missing = len(s) % 4
        if missing:
            s += '=' * (4 - missing)
        return base64.b64decode(s)
    except Exception as e:
        print(f"[safe_b64decode] Erreur : {e}")
        return None

# ══════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════

def run_pipeline(img_bytes, filename):
    img_b64 = base64.b64encode(img_bytes).decode()
    ph = st.empty()
    states = {"Analyste": "wait", "Décideur": "wait", "Comparateur": "wait", "Exécuteur": "wait", "Rapporteur": "wait"}

    def show(s):
        icons = {"wait": "○", "run": "◉", "done": "●", "error": "✕"}
        cls   = {"wait": "ag-wait", "run": "ag-run", "done": "ag-done", "error": "ag-error"}
        badges = "".join(f'<span class="ag-badge {cls[v]}">{icons[v]} {k}</span>' for k, v in s.items())
        ph.markdown(f'<div class="ag-row">{badges}</div>', unsafe_allow_html=True)

    for agent in states:
        states[agent] = "run"
    show(states)

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json={"image_base64": img_b64, "filename": filename},
            timeout=300
        )

        print("STATUS:", response.status_code)
        print("CONTENT TYPE:", response.headers.get('content-type', ''))
        print("RESPONSE TEXT:", response.text[:800])

        # ── Parser la réponse ──────────────────────────────────────────
        try:
            result = response.json()
        except Exception as e:
            st.error(f"n8n a renvoyé une réponse invalide : {response.text[:300]}")
            for agent in states: states[agent] = "error"
            show(states)
            return None

        # n8n retourne parfois une liste
        if isinstance(result, list):
            result = result[0] if result else {}

        # Vérifier que c'est un dict
        if not isinstance(result, dict):
            st.error(f"Format inattendu depuis n8n : {type(result)}")
            for agent in states: states[agent] = "error"
            show(states)
            return None

        if result.get("status") != "success":
            for agent in states: states[agent] = "error"
            show(states)
            st.error(f"Erreur pipeline n8n : {result}")
            return None

        # ── Tout OK ────────────────────────────────────────────────────
        for agent in states: states[agent] = "done"
        show(states)

        # ✅ Convertir TOUTES les valeurs qui peuvent être des strings JSON
        features         = safe_dict(result.get("features", {}))
        decision_init    = safe_dict(result.get("decision_initiale", {}))
        decision_fin     = safe_dict(result.get("decision_finale", {}))
        metrics          = safe_dict(result.get("metrics", {}))
        rapport          = safe_dict(result.get("rapport", {}))
        fichiers         = safe_dict(result.get("fichiers", {}))
        compressed_b64   = result.get("compressed_b64", "") or ""
        decision_changee = result.get("decision_changee", False)

        # ✅ Extraire format et qualité en sécurité
        fmt = str(decision_fin.get("format_choisi", decision_fin.get("format", "WEBP"))).upper()
        try:
            qual = int(decision_fin.get("qualite", decision_fin.get("quality", 85)))
        except:
            qual = 85

        ssim_val = metrics.get("ssim", "?")
        gain_val = metrics.get("taux_compression_pct", "?")
        ev_val   = compute_eval(ssim_val)

        st.session_state["history"].insert(0, {
            "image":  filename,
            "format": fmt,
            "ssim":   ssim_val,
            "gain":   gain_val,
            "eval":   ev_val,
            "time":   datetime.now().strftime("%d/%m/%Y %H:%M"),
        })

        return {
            "filename":          filename,
            "timestamp":         datetime.now().strftime("%d/%m/%Y %H:%M"),
            "analyste":          features,
            "decision_initiale": decision_init,
            "decision_finale":   decision_fin,
            "decision_changee":  decision_changee,
            "metrics":           metrics,
            "compressed_b64":    compressed_b64,
            "rapport":           rapport,
            "fichiers":          fichiers,
        }

    except Exception as e:
        for agent in states: states[agent] = "error"
        show(states)
        st.error(f"Erreur connexion n8n : {e}")
        import traceback
        print(traceback.format_exc())
        return None

# ─── SIDEBAR ────────────────────────────────────────────────
srv_ok = check_server()

if st.session_state.show_sidebar:
    with st.sidebar:
        st.markdown(
            '<div class="sb-logo">'
            '<div class="sb-logo-name">🧠 <span>PixelMind</span></div>'
            '<div class="sb-logo-sub">AI Compression System · Groq</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="sb-section-lbl">Navigation</div>', unsafe_allow_html=True)
        nav_pages = [
            ("nav_home", "🏠  Accueil",    "accueil"),
            ("nav_comp", "🗜️  Compresser", "compress"),
            ("nav_dash", "📊  Dashboard",  "dashboard"),
            ("nav_hist", "🕒  Historique", "history"),
            ("nav_30",   "🖼️  30 Images",  "n8n"),
        ]
        for key, label, pg in nav_pages:
            if st.button(label, key=key, use_container_width=True):
                st.session_state["page"] = pg; st.rerun()

        st.markdown('<hr style="border:none;border-top:1px solid #E8E4F8;margin:12px 8px">', unsafe_allow_html=True)
        st.markdown('<div class="sb-section-lbl">Agents du pipeline</div>', unsafe_allow_html=True)
        for icon, name, who in [
            ("🔬","Analyste",    "Sara"),
            ("🧠","Décideur",    "Kaoutar (Groq llama-70b)"),
            ("⚖️","Comparateur", "Kaoutar (Groq 2 LLM)"),
            ("⚙️","Exécuteur",   "Zayneb"),
            ("📋","Rapporteur",  "Bassma"),
        ]:
            st.markdown(
                f'<div class="sb-agent">'
                f'<div class="sb-agent-icon">{icon}</div>'
                f'<div><div class="sb-agent-name">{name}</div>'
                f'<div class="sb-agent-who">{who}</div></div>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('<hr style="border:none;border-top:1px solid #E8E4F8;margin:12px 8px">', unsafe_allow_html=True)
        srv_c = "dot-g" if srv_ok else "dot-m"
        st.markdown(
            f'<div style="padding:8px 16px 20px;font-size:.73rem;color:var(--muted)">'
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">'
            f'<span class="dot {srv_c}"></span> Flask {"en ligne" if srv_ok else "hors ligne"}</div>'
            f'<div style="display:flex;align-items:center;gap:6px">'
            f'<span class="dot dot-g"></span> Groq LLM (cloud)</div></div>',
            unsafe_allow_html=True
        )

page = st.session_state["page"]

# ═══════════════════════════════════════════════════════
# ACCUEIL
# ═══════════════════════════════════════════════════════
if page == "accueil":
    st.markdown(
        '<div class="hero-wrap">'
        '<div class="hero-glow-1"></div><div class="hero-glow-2"></div>'
        '<div class="hero-chip">Système Multi-Agents · IA Générative</div>'
        '<h1 class="hero-title">Compression d\'images<br><span class="grad">intelligente & adaptative</span></h1>'
        '<p class="hero-sub">Un pipeline automatisé de 5 agents IA qui analyse chaque image, choisit la meilleure stratégie de compression et génère un rapport complet avec métriques de qualité.</p>'
        '<div class="hero-tags">'
        '<span class="hero-tag">PSNR · SSIM · MSE</span>'
        '<span class="hero-tag">JPEG · PNG · WebP · AVIF</span>'
        '<span class="hero-tag">Groq LLM (llama-3.3-70b)</span>'
        '<span class="hero-tag">Rapport automatique</span>'
        '<span class="hero-tag">5 agents autonomes</span>'
        '</div>'
        '<div class="hero-stats">'
        '<div class="hero-stat"><div class="hero-stat-val">5</div><div class="hero-stat-lbl">Agents IA</div></div>'
        '<div class="hero-stat"><div class="hero-stat-val">5</div><div class="hero-stat-lbl">Métriques</div></div>'
        '<div class="hero-stat"><div class="hero-stat-val">30+</div><div class="hero-stat-lbl">Images testées</div></div>'
        '</div></div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="sec-hd">Pipeline de traitement</div>', unsafe_allow_html=True)
    cols5 = st.columns(5)
    for col, (icon, name, desc, who) in zip(cols5, [
        ("🔬","Analyste",    "Extrait les caractéristiques visuelles",     "Sara"),
        ("🧠","Décideur",    "Groq llama-70b choisit le format optimal",   "Kaoutar"),
        ("⚖️","Comparateur", "2 LLM Groq comparent et valident",           "Kaoutar"),
        ("⚙️","Exécuteur",   "Applique la compression + retry SSIM",       "Zayneb"),
        ("📋","Rapporteur",  "Génère rapport + graphiques + JSON",          "Bassma"),
    ]):
        with col:
            st.markdown(
                f'<div class="card anim-1" style="text-align:center;padding:24px 14px">'
                f'<div style="font-size:1.9rem;margin-bottom:10px">{icon}</div>'
                f'<div style="font-weight:700;font-size:.88rem;margin-bottom:5px">{name}</div>'
                f'<div style="font-size:.72rem;color:var(--muted);line-height:1.5;margin-bottom:10px">{desc}</div>'
                f'<span style="font-size:.66rem;background:rgba(124,92,191,0.08);color:var(--violet);padding:3px 10px;border-radius:100px;border:1px solid rgba(124,92,191,0.2)">{who}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
    st.markdown('<br>', unsafe_allow_html=True)
    btn_cols = st.columns([1, 2, 1])
    with btn_cols[1]:
        if st.button("🚀  Commencer la compression →", use_container_width=True):
            st.session_state["page"] = "compress"; st.rerun()

# ═══════════════════════════════════════════════════════
# COMPRESSER
# ═══════════════════════════════════════════════════════
elif page == "compress":
    if not srv_ok:
        st.error("Lance d'abord : python server_groq.py"); st.stop()

    st.markdown('<div class="sec-hd">Importer & compresser</div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1.5], gap="large")

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📤 Image source**")
        uploaded = st.file_uploader("", type=["jpg","jpeg","png","webp","bmp","tiff"], label_visibility="collapsed")
        if uploaded:
            st.image(uploaded.getvalue(), use_container_width=True)
            st.markdown(f'<p style="font-size:.75rem;color:var(--muted);margin-top:8px">📁 {uploaded.name} · {uploaded.size/1024:.1f} KB</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**🤖 Pipeline Multi-Agents (Groq)**")
        st.markdown('<p style="font-size:.8rem;color:var(--muted);margin-bottom:16px">Analyste → Décideur (Groq) → Comparateur (Groq) → Exécuteur → Rapporteur</p>', unsafe_allow_html=True)
        if uploaded:
            if st.button("▶  Lancer l'optimisation", use_container_width=True):
                with st.spinner("Pipeline en cours…"):
                    res = run_pipeline(uploaded.getvalue(), uploaded.name)
                if res:
                    st.session_state["results"]        = res
                    st.session_state["original_bytes"] = uploaded.getvalue()
                    st.success("✅ Pipeline terminé !")
        else:
            st.info("⬅ Importe une image pour commencer")
        st.markdown('</div>', unsafe_allow_html=True)

    if "results" in st.session_state and "original_bytes" in st.session_state:
        results    = st.session_state["results"]
        orig_bytes = st.session_state["original_bytes"]
        metrics    = results.get("metrics", {})
        features   = results.get("analyste", {})
        dec_init   = results.get("decision_initiale", {})
        dec_fin    = results.get("decision_finale", {})
        changed    = results.get("decision_changee", False)
        rapport    = results.get("rapport", {})
        comp_b64   = results.get("compressed_b64", "")
        fichiers   = results.get("fichiers", {})

        fmt  = dec_fin.get("format_choisi", dec_fin.get("format", "?"))
        qual = dec_fin.get("qualite", dec_fin.get("quality", "?"))

        st.markdown('<div class="sec-hd">Métriques de qualité</div>', unsafe_allow_html=True)
        t1,t2,t3,t4,t5 = st.columns(5)
        for col, (val, lbl, sub) in zip([t1,t2,t3,t4,t5], [
            (metrics.get("ssim","—"),                        "SSIM", "Qualité visuelle"),
            (f"{metrics.get('psnr_db','—')} dB",             "PSNR", "Fidélité signal"),
            (metrics.get("mse","—"),                          "MSE",  "Erreur"),
            (f"{metrics.get('taux_compression_pct','—')}%",  "Gain", "Espace économisé"),
            (metrics.get("ratio_qualite_taille","—"),         "Q/T",  "Score composite"),
        ]):
            with col:
                st.markdown(f'<div class="m-tile"><div class="m-lbl">{lbl}</div><div class="m-val">{val}</div><div class="m-sub">{sub}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-hd">Résultat visuel</div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**Originale**")
            st.image(orig_bytes, use_container_width=True)
            st.markdown(f'<p style="font-size:.75rem;color:var(--muted);margin-top:6px">{metrics.get("original_size_kb","?")} KB</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with cb:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if changed:
                init_fmt = dec_init.get("format_choisi", dec_init.get("format","?"))
                st.markdown(f'<span class="ch-badge">⚡ {init_fmt} → {fmt}</span>', unsafe_allow_html=True)
            st.markdown(f"**Compressée — {fmt} q={qual}**")
            if comp_b64:
                # ✅ Utiliser safe_b64decode — corrige padding et espaces n8n
                comp_bytes = safe_b64decode(comp_b64)
                if comp_bytes:
                    st.image(comp_bytes, use_container_width=True)
                    st.markdown(
                        f'<p style="font-size:.75rem;color:#16A34A;margin-top:6px">'
                        f'▼ {metrics.get("compressed_size_kb","?")} KB · économie {metrics.get("taux_compression_pct","?")}%'
                        f'</p>',
                        unsafe_allow_html=True
                    )
                    fmt_ext   = {"JPEG":"jpg","PNG":"png","WEBP":"webp","JPEG2000":"jp2"}.get(str(fmt).upper(),"webp")
                    base_name = os.path.splitext(results.get("filename","image"))[0]
                    rj = json.dumps(
                        {"image":results.get("filename"),"analyse":features,"decision":dec_fin,"metriques":metrics,"rapport":rapport},
                        indent=2, ensure_ascii=False
                    ).encode("utf-8")
                    d1,d2,d3 = st.columns(3)
                    d1.download_button("⬇ Image", comp_bytes, file_name=f"{base_name}.{fmt_ext}", use_container_width=True)
                    d2.download_button("⬇ JSON",  rj, file_name=f"{base_name}_rapport.json", mime="application/json", use_container_width=True)
                    zb = io.BytesIO()
                    with zipfile.ZipFile(zb,"w",zipfile.ZIP_DEFLATED) as zf:
                        zf.writestr(f"{base_name}.{fmt_ext}", comp_bytes)
                        zf.writestr(f"{base_name}_rapport.json", rj)
                    zb.seek(0)
                    d3.download_button("⬇ ZIP", zb, file_name=f"{base_name}_pack.zip", mime="application/zip", use_container_width=True)
                else:
                    st.warning("⚠️ Image compressée non disponible (erreur décodage base64)")
            else:
                st.info("Image compressée non reçue depuis n8n")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-hd">Rapport par agent</div>', unsafe_allow_html=True)

        with st.expander("🔬 Agent Analyste — Sara"):
            meta   = features.get("metadonnees",{})
            stats  = features.get("features_statistiques",{})
            cont   = features.get("contours",{})
            ocr    = features.get("ocr",{})
            c1, c2 = st.columns(2)
            c1.markdown(f'<div class="rpt"><b>Type</b> <span class="tag">{features.get("type_image","?")}</span><br><b>Résolution</b> {meta.get("largeur","?")}×{meta.get("hauteur","?")} px<br><b>Format</b> {meta.get("format","?")}<br><b>Taille</b> {meta.get("taille_kb","?")} KB</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="rpt"><b>Entropie</b> {stats.get("entropy","?")}<br><b>Variance</b> {stats.get("variance","?")}<br><b>Contours</b> {cont.get("nombre_contours","?")}<br><b>Texte</b> {"✅" if ocr.get("contient_texte") else "❌"}</div>', unsafe_allow_html=True)

        with st.expander("🧠 Agent Décideur — Kaoutar (Groq llama-3.3-70b)"):
            st.markdown(
                f'<div class="rpt">'
                f'<b>Source</b> <span style="color:#16A34A;font-weight:700">Groq llama-3.3-70b-versatile</span><br>'
                f'<b>Format choisi</b> <span class="tag">{dec_init.get("format_choisi","?")}</span> '
                f'q={dec_init.get("qualite","?")}<br>'
                f'<b>Raison</b> {dec_init.get("raison","—")}<br>'
                f'<b>Cas usage</b> {dec_init.get("cas_usage","—")}'
                f'</div>',
                unsafe_allow_html=True
            )

        with st.expander("⚖️ Agent Comparateur — Kaoutar (Groq 2 LLM)"):
            if changed:
                st.info(f"Décision corrigée : {dec_init.get('format_choisi','?')} → **{fmt}**")
            else:
                st.success(f"Décision confirmée : {fmt} q={qual}")
            st.markdown(
                f'<div class="rpt">'
                f'<b>Méthode sélection</b> {dec_fin.get("methode_selection","—")}<br>'
                f'<b>Format final</b> <span class="tag">{fmt}</span> q={qual}<br>'
                f'<b>Raison</b> {dec_fin.get("raison","—")}'
                f'</div>',
                unsafe_allow_html=True
            )

        with st.expander("⚙️ Agent Exécuteur — Zayneb"):
            adj = metrics.get("quality_adjusted", False)
            st.markdown(
                f'<div class="rpt">'
                f'<b>Format</b> <span class="tag">{metrics.get("format_used","?")}</span><br>'
                f'<b>Qualité</b> {metrics.get("quality_used","?")} {"(ajusté automatiquement)" if adj else ""}<br>'
                f'<b>Réduction</b> {metrics.get("original_size_kb","?")} KB → {metrics.get("compressed_size_kb","?")} KB ({metrics.get("compression_ratio","?")}×)<br>'
                f'<b>Retries SSIM</b> {metrics.get("retry_count",0)}'
                f'</div>',
                unsafe_allow_html=True
            )
            m1,m2,m3,m4 = st.columns(4)
            for col, (l, v) in zip([m1,m2,m3,m4], [
                ("PSNR", f"{metrics.get('psnr_db','?')} dB"),
                ("SSIM", metrics.get("ssim","?")),
                ("MSE",  metrics.get("mse","?")),
                ("Gain", f"{metrics.get('taux_compression_pct','?')}%")
            ]):
                col.metric(l, v)

        with st.expander("📋 Agent Rapporteur — Bassma", expanded=True):
            rc_data = rapport.get("rapport_compression", {})
            ia_ok   = rc_data.get("decision_ia", {}).get("decision_pertinente", False)
            ev      = rc_data.get("metriques_qualite", {}).get("evaluation", "")
            concl   = rc_data.get("conclusion", "")
            if not ev:
                ev = compute_eval(metrics.get("ssim","0"))
            if not concl:
                concl = (f"Compression {ev} — {metrics.get('taux_compression_pct','?')}% économisé. "
                         f"PSNR={metrics.get('psnr_db','?')} dB | SSIM={metrics.get('ssim','?')} | MSE={metrics.get('mse','?')}.")
            ev_color = "#16A34A" if ev=="Excellent" else "#E5A800" if ev in ("Bon","Acceptable") else "#EF4444"
            st.markdown(
                f'<div class="rpt">'
                f'<b>Évaluation</b> <span style="color:{ev_color};font-weight:700">{ev}</span><br>'
                f'<b>Décision IA pertinente</b> {"✅ Oui" if ia_ok else "⚠️ À revoir"}<br>'
                f'<b>Conclusion</b> {concl}'
                f'</div>',
                unsafe_allow_html=True
            )
            if fichiers.get("gauge") or fichiers.get("metrics_chart"):
                fa, fb = st.columns(2)
                if fichiers.get("gauge"):
                    fa.image(fichiers["gauge"], caption="Jauge SSIM", use_container_width=True)
                if fichiers.get("metrics_chart"):
                    fb.image(fichiers["metrics_chart"], caption="Comparaison stratégies", use_container_width=True)

        with st.expander("{ } JSON brut"):
            st.json(results)

# ═══════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════
elif page == "dashboard":
    st.markdown('<div class="sec-hd">Dashboard · Vue d\'ensemble</div>', unsafe_allow_html=True)
    hist      = st.session_state.get("history", [])
    total     = len(hist)
    excellent = sum(1 for h in hist if str(h.get("eval","")) == "Excellent")
    bon       = sum(1 for h in hist if str(h.get("eval","")) == "Bon")
    gains     = []
    for h in hist:
        try:
            g = h.get("gain","")
            if g and str(g) not in ("","?"):
                gains.append(float(g))
        except: pass
    avg_gain = round(sum(gains)/max(len(gains),1), 1)

    c1,c2,c3,c4 = st.columns(4)
    for col, (icon, lbl, val, sub, bg) in zip([c1,c2,c3,c4], [
        ("🗜️","Total traité",  str(total),     "images",    "rgba(124,92,191,0.1)"),
        ("✅","Excellent",     str(excellent), "résultats", "rgba(34,197,94,0.1)"),
        ("📊","Bon",           str(bon),       "résultats", "rgba(229,168,0,0.1)"),
        ("💾","Gain moyen",    f"{avg_gain}%", "économisé", "rgba(124,92,191,0.1)"),
    ]):
        with col:
            st.markdown(
                f'<div class="dash-card anim-1">'
                f'<div class="dash-card-icon" style="background:{bg}">{icon}</div>'
                f'<div class="dash-card-val">{val}</div>'
                f'<div class="dash-card-lbl">{lbl} · {sub}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    if hist:
        df_h = pd.DataFrame(hist)
        df_h["ssim_f"] = pd.to_numeric(df_h["ssim"], errors='coerce')
        df_h["gain_f"] = pd.to_numeric(df_h["gain"], errors='coerce')
        st.markdown('<div class="sec-hd">Activité récente</div>', unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            sv = df_h["ssim_f"].fillna(0).tolist()[::-1]
            nm = df_h["image"].tolist()[::-1]
            bc = ["#22C55E" if v>0.95 else "#E5A800" if v>0.9 else "#EF4444" for v in sv]
            fig = go.Figure(go.Bar(x=nm, y=sv, marker_color=bc, text=[f'{v:.3f}' for v in sv], textposition='outside', textfont=dict(color='#1A1F2E',size=10)))
            fig.update_layout(title="SSIM par image", height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#1A1F2E',family='Plus Jakarta Sans'), xaxis=dict(tickangle=-30,gridcolor='#F0EDE8'), yaxis=dict(range=[0,1.15],gridcolor='#F0EDE8'), margin=dict(t=32,b=0,l=0,r=0))
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            gv = df_h["gain_f"].fillna(0).tolist()[::-1]
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=list(range(len(gv))), y=gv, fill='tozeroy', fillcolor='rgba(124,92,191,0.1)', line=dict(color='#7C5CBF',width=2), mode='lines+markers', marker=dict(color='#E8559A',size=7)))
            fig2.update_layout(title="Taux compression τ%", height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#1A1F2E',family='Plus Jakarta Sans'), xaxis=dict(gridcolor='#F0EDE8'), yaxis=dict(gridcolor='#F0EDE8'), margin=dict(t=32,b=0,l=0,r=0))
            st.plotly_chart(fig2, use_container_width=True)
        g3, g4 = st.columns(2)
        with g3:
            fc = pd.Series([h.get("format","?") for h in hist]).value_counts()
            fig3 = go.Figure(go.Pie(labels=fc.index.tolist(), values=fc.values.tolist(), hole=0.55, marker_colors=['#7C5CBF','#E8559A','#4AAFCA','#E5A800']))
            fig3.update_layout(title="Formats utilisés", height=260, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#1A1F2E',family='Plus Jakarta Sans'), margin=dict(t=32,b=0,l=0,r=0))
            st.plotly_chart(fig3, use_container_width=True)
        with g4:
            ec  = pd.Series([h.get("eval","?") for h in hist]).value_counts()
            ecm = {"Excellent":"#22C55E","Bon":"#E5A800","Acceptable":"#F97316","Dégradé":"#EF4444","?":"#9CA3AF"}
            bc2 = [ecm.get(e,"#9CA3AF") for e in ec.index.tolist()]
            fig4 = go.Figure(go.Bar(x=ec.index.tolist(), y=ec.values.tolist(), marker_color=bc2, text=ec.values.tolist(), textposition='outside', textfont=dict(color='#1A1F2E')))
            fig4.update_layout(title="Distribution évaluations", height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#1A1F2E',family='Plus Jakarta Sans'), xaxis=dict(gridcolor='#F0EDE8'), yaxis=dict(gridcolor='#F0EDE8'), margin=dict(t=32,b=0,l=0,r=0))
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.markdown('<div class="card" style="text-align:center;padding:60px;color:var(--muted)">Aucune donnée · Compresse d\'abord des images</div>', unsafe_allow_html=True)
        if st.button("→ Aller à Compresser"):
            st.session_state["page"] = "compress"; st.rerun()

# ═══════════════════════════════════════════════════════
# HISTORIQUE
# ═══════════════════════════════════════════════════════
elif page == "history":
    st.markdown('<div class="sec-hd">Historique des compressions</div>', unsafe_allow_html=True)
    hist = st.session_state.get("history", [])
    if hist:
        st.markdown(f'<p style="font-size:.8rem;color:var(--muted);margin-bottom:16px">{len(hist)} compression(s) cette session</p>', unsafe_allow_html=True)
        header    = '<div class="hist-wrap"><div class="hist-row hist-header"><span>Image</span><span>Format</span><span>SSIM</span><span>Gain</span><span>Évaluation</span><span>Heure</span></div>'
        rows_html = ""
        for h in hist:
            ev = str(h.get("eval","?"))
            ec = "#16A34A" if ev=="Excellent" else "#E5A800" if ev=="Bon" else "#EF4444"
            rows_html += (
                f'<div class="hist-row">'
                f'<span style="font-weight:600">{h.get("image","?")}</span>'
                f'<span><span class="tag">{h.get("format","?")}</span></span>'
                f'<span style="font-family:JetBrains Mono,monospace">{h.get("ssim","?")}</span>'
                f'<span style="color:#16A34A;font-weight:600">{h.get("gain","?")}%</span>'
                f'<span style="color:{ec};font-weight:600">{ev}</span>'
                f'<span style="color:var(--muted);font-size:.73rem">{h.get("time","")}</span>'
                f'</div>'
            )
        st.markdown(header + rows_html + '</div>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("🗑  Effacer l'historique"):
            st.session_state["history"] = []; st.rerun()
    else:
        st.markdown('<div class="card" style="text-align:center;padding:60px;color:var(--muted)">Aucun historique · Compresse d\'abord une image</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# 30 IMAGES
# ═══════════════════════════════════════════════════════
elif page == "n8n":
    st.markdown('<div class="sec-hd">Résultats · 30 images via n8n</div>', unsafe_allow_html=True)

    DATABASE_DIR = r"C:\Users\Lenovo ThinkPad T470\OneDrive\Documents\Bureau\Projet_Compression\database-projet"

    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("▶ Lancer les tests", use_container_width=True):
            # Trouver toutes les images
            import glob as gb

            extensions = ['jpg', 'jpeg', 'png', 'bmp', 'webp', 'tiff']
            images = []
            seen = set()
            for ext in extensions:
                for p in gb.glob(os.path.join(DATABASE_DIR, '**', f'*.{ext}'), recursive=True):
                    if p.lower() not in seen:
                        seen.add(p.lower())
                        images.append(p)
                for p in gb.glob(os.path.join(DATABASE_DIR, '**', f'*.{ext.upper()}'), recursive=True):
                    if p.lower() not in seen:
                        seen.add(p.lower())
                        images.append(p)

            st.info(f"📁 {len(images)} images trouvées — envoi vers n8n...")

            resultats = []
            progress = st.progress(0)
            status_text = st.empty()

            for i, img_path in enumerate(images):
                nom = os.path.basename(img_path)
                categorie = os.path.basename(os.path.dirname(img_path))
                status_text.text(f"⚡ Traitement {i + 1}/{len(images)} : {nom}")

                try:
                    # Lire l'image et l'envoyer au webhook n8n
                    with open(img_path, 'rb') as f:
                        img_bytes = f.read()
                    img_b64 = base64.b64encode(img_bytes).decode()

                    # Envoyer au webhook n8n
                    N8N_PROD_URL = "http://localhost:5678/webhook/compression-pipeline"
                    response = requests.post(
                        N8N_PROD_URL,
                        json={
                            "image_base64": img_b64,
                            "filename": nom,
                            "categorie": categorie
                        },
                        timeout=300
                    )

                    result = response.json()
                    if isinstance(result, list):
                        result = result[0] if result else {}

                    # Parser les métriques
                    metrics = safe_dict(result.get("metrics", {}))
                    dec_fin = safe_dict(result.get("decision_finale", {}))
                    fmt = str(dec_fin.get("format_choisi", "?")).upper()

                    resultats.append({
                        "image": nom,
                        "categorie": categorie,
                        "decision_finale": fmt,
                        "ssim": metrics.get("ssim", "?"),
                        "psnr_db": metrics.get("psnr_db", "?"),
                        "mse": metrics.get("mse", "?"),
                        "tau": metrics.get("taux_compression_pct", "?"),
                        "statut": "✅" if result.get("status") == "success" else "❌"
                    })

                except Exception as e:
                    resultats.append({
                        "image": nom,
                        "categorie": categorie,
                        "statut": "❌",
                        "erreur": str(e)
                    })

                progress.progress((i + 1) / len(images))

            status_text.text("✅ Tous les tests terminés !")

            # Sauvegarder le résumé
            resume = {
                "total": len(images),
                "succes": sum(1 for r in resultats if r.get("statut") == "✅"),
                "erreurs": sum(1 for r in resultats if r.get("statut") == "❌"),
                "resultats": resultats
            }
            os.makedirs(RAPPORTS_DIR, exist_ok=True)
            with open(os.path.join(RAPPORTS_DIR, "resume_global.json"), 'w', encoding='utf-8') as f:
                json.dump(resume, f, indent=2, ensure_ascii=False)

            st.success(f"✅ {resume['succes']}/{len(images)} images traitées via n8n !")
            st.rerun()

    # Afficher les résultats
    resume_path = os.path.join(RAPPORTS_DIR, "resume_global.json")
    if not os.path.exists(resume_path):
        st.markdown(
            '<div class="card" style="text-align:center;padding:60px;color:var(--muted)">Aucun résultat · Lance les tests d\'abord</div>',
            unsafe_allow_html=True)
    else:
        with open(resume_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        m1, m2, m3, m4 = st.columns(4)
        for col, (lbl, val, sub) in zip([m1, m2, m3, m4], [
            ("Total", data.get("total", 0), "images"),
            ("Succès", data.get("succes", 0), "OK"),
            ("Erreurs", data.get("erreurs", 0), "failed"),
            ("Durée", f"{data.get('duree_sec', 0)}s", "elapsed"),
        ]):
            with col:
                st.markdown(
                    f'<div class="m-tile"><div class="m-lbl">{lbl}</div><div class="m-val">{val}</div><div class="m-sub">{sub}</div></div>',
                    unsafe_allow_html=True)

        if data.get("resultats"):
            df = pd.DataFrame(data["resultats"])
            st.markdown('<div class="sec-hd">Tableau détaillé</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Graphiques
            g1, g2 = st.columns(2)
            with g1:
                df_s = df.copy()
                df_s["ssim"] = pd.to_numeric(df_s["ssim"], errors='coerce')
                if "categorie" in df_s.columns:
                    fig = px.box(df_s, x="categorie", y="ssim", color="categorie",
                                 title="Distribution SSIM par catégorie",
                                 color_discrete_sequence=["#7C5CBF", "#E8559A", "#4AAFCA", "#E5A800"])
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      font=dict(color='#1A1F2E', family='Plus Jakarta Sans'), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            with g2:
                df_t = df.copy()
                df_t["tau"] = pd.to_numeric(df_t["tau"], errors='coerce')
                if "categorie" in df_t.columns:
                    fig2 = px.bar(df_t.groupby("categorie")["tau"].mean().reset_index(),
                                  x="categorie", y="tau", color="categorie",
                                  title="Taux compression moyen %",
                                  color_discrete_sequence=["#7C5CBF", "#E8559A", "#4AAFCA", "#E5A800"])
                    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                       font=dict(color='#1A1F2E', family='Plus Jakarta Sans'), showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)

            if st.button("🔄 Rafraîchir"):
                st.rerun()

st.markdown('<p style="text-align:center;color:var(--muted);font-size:.7rem;margin-top:40px;border-top:1px solid var(--border);padding-top:20px">© 2025-2026 · Équipe 4 · Université Hassan II · FSTM · PixelMind AI</p>', unsafe_allow_html=True)