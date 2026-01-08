import streamlit as st
import pandas as pd
import altair as alt
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Consultation Management 2050",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DESIGN SYSTÈME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); color: white; }

    /* ONGLETS */
    button[data-baseweb="tab"] { font-size: 24px !important; font-weight: 900 !important; color: #64748b; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #38bdf8 !important; border-bottom: 4px solid #38bdf8 !important; }

    /* TITRE */
    h1 { font-size: 4rem !important; text-align: center; font-weight: 900; color: #f8fafc; margin-bottom: 20px; }

    /* BOITE QUESTION */
    .question-box { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 20px; margin-bottom: 20px; }
    .question-title { font-size: 28px; font-weight: 700; color: #38bdf8; }

    /* PROPOSITIONS */
    .stRadio > div { gap: 15px; }
    .stRadio > div > label { background: rgba(255, 255, 255, 0.05); border: 2px solid rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; transition: all 0.3s ease; }
    .stRadio p { font-size: 22px !important; font-weight: 500; color: #f1f5f9; line-height: 1.4; }
    
    /* Style une fois voté (grisé mais lisible) */
    .stRadio > div[aria-disabled="true"] > label { opacity: 1 !important; background: rgba(255,255,255,0.02); border-color: #334155; }
    .stRadio > div[aria-disabled="true"] p { color: #94a3b8 !important; }

    /* BOUTON VALIDER */
    .stButton > button { width: 100%; font-size: 24px !important; padding: 15px !important; border-radius: 15px; background: #38bdf8; border: none; font-weight: 900; color: #0f172a; }
    .stButton > button:hover { background: #7dd3fc; transform: scale(1.02); }

    /* BOX GAGNANT */
    .winner-box { background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%); border: 2px solid #38bdf8; padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 20px; }
    
    /* MESSAGE ATTENTE */
    .waiting-box { padding: 40px; text-align: center; color: #64748b; border: 2px dashed #334155; border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES GLOBALE ---
@st.cache_resource
def get_global_db():
    return {
        "votes": {
            "Télétravail": {"A": 0, "B": 0, "C": 0},
            "Bienveillance": {"A": 0, "B": 0, "C": 0},
            "IA": {"A": 0, "B": 0, "C": 0},
            "Perturbateurs": {"A": 0, "B": 0, "C": 0}
        }
    }

db = get_global_db()

# --- CONTENU ---
questions = {
    "Télétravail": {
        "theme": "Quelle place pour le télétravail à l'horizon 2050 ?",
        "opts": {
            "A": "Par défaut : le télétravail est la norme, soutenue par des rituels et du lien.",
            "B": "Exception encadrée : le présentiel prime, le télétravail reste limité et cadré.",
            "C": "Non-sujet : seuls les résultats comptent, le lieu importe peu."
        }
    },
    "Bienveillance": {
        "theme": "Quelle définition concrète de la bienveillance managériale ?",
        "opts": {
            "A": "La vraie bienveillance, c’est un cadre clair avec la capacité de récompenser et sanctionner.",
            "B": "Viser les résultats sans stress, oser dire non aux objectifs irréalistes, valoriser et traiter les sujets en tête-à-tête.",
            "C": "La bienveillance est une culture congruente soutenue par des pratiques exigeantes (attentes claires, feedback, droit à l’erreur, sécurité psy)."
        }
    },
    "IA": {
        "theme": "Quelle limite poser à l'usage de l'IA dans le management ?",
        "opts": {
            "A": "L’IA assiste sur des tâches techniques, mais le manager reste seul décisionnaire.",
            "B": "Le manager s’appuie sur l’IA pour éclairer et challenger ses choix, sans lui déléguer la décision finale.",
            "C": "L’usage de l’IA est volontairement limité pour préserver le lien humain et l’équité."
        }
    },
    "Perturbateurs": {
        "theme": "Quelle attitude adopter face aux éléments perturbateurs ?",
        "opts": {
            "A": "Moteur : intégrer le radical pour innover et s’adapter.",
            "B": "Encadrée : diversité oui, mais avec un cadre.",
            "C": "À contenir : freiner le disruptif pour préserver la stabilité."
        }
    }
}

# --- ÉTAT DE SESSION ---
for key in questions.keys():
    if f"has_voted_{key}" not in st.session_state:
        st.session_state[f"has_voted_{key}"] = False
    if f"user_choice_{key}" not in st.session_state:
        st.session_state[f"user_choice_{key}"] = None

# --- MENU LATÉRAL (ADMIN) ---
with st.sidebar:
    st.header("Admin Prof")
    st.warning("Zone dangereuse")
    if st.button("🗑️ RÉINITIALISER TOUT (0 votes)", type="primary"):
        for k in db["votes"]:
            for opt in db["votes"][k]:
                db["votes"][k][opt] = 0
        st.cache_resource.clear()
        st.session_state.clear()
        st.rerun()

# --- HEADER & MODE LIVE ---
col_h1, col_live = st.columns([4, 1])
with col_h1:
    st.markdown("<h1>MANAGEMENT 2050</h1>", unsafe_allow_html=True)
with col_live:
    st.write("")
    st.write("")
    live_mode = st.toggle("🔄 Mode Live", value=False)

if live_mode:
    time.sleep(2)
    st.rerun()

# --- CORPS DE PAGE ---
tabs = st.tabs(list(questions.keys()))

for i, (key, data) in enumerate(questions.items()):
    with tabs[i]:
        col_vote, col_stats = st.columns([1, 1], gap="large")

        # --- GAUCHE : LE SONDAGE ---
        with col_vote:
            st.markdown(f'<div class="question-box"><div class="question-title">{data["theme"]}</div></div>', unsafe_allow_html=True)
            
            already_voted = st.session_state[f"has_voted_{key}"]
            user_prev_choice = st.session_state[f"user_choice_{key}"]

            # 1. FORMULAIRE DE VOTE
            if not already_voted:
                with st.form(f"form_{key}"):
                    user_choice = st.radio(
                        "Propositions :",
                        options=list(data['opts'].keys()),
                        format_func=lambda x: data['opts'][x],
                        label_visibility="collapsed"
                    )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("VALIDER MA DÉCISION"):
                        db["votes"][key][user_choice] += 1
                        st.session_state[f"has_voted_{key}"] = True
                        st.session_state[f"user_choice_{key}"] = user_choice
                        st.toast("Vote envoyé !", icon="🚀")
                        time.sleep(0.5)
                        st.rerun()

            # 2. AFFICHAGE APRÈS VOTE (SANS FORMULAIRE pour éviter l'erreur)
            else:
                # On recrée l'affichage des radios mais désactivés
                keys_list = list(data['opts'].keys())
                # Sécurité si la clé n'existe pas
                idx = 0
                if user_prev_choice in keys_list:
                    idx = keys_list.index(user_prev_choice)
                
                st.radio(
                    "Votre choix :",
                    options=keys_list,
                    format_func=lambda x: data['opts'][x],
                    index=idx,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"view_only_{key}"
                )
                
                st.markdown(f"""
                <div style="margin-top:20px; padding:15px; border:1px solid #10b981; background:rgba(16,185,129,0.1); border-radius:10px; color:#10b981; font-weight:bold; text-align:center;">
                    ✅ Vote bien pris en compte
                </div>
                """, unsafe_allow_html=True)

        # --- DROITE : LE CAMEMBERT ---
        with col_stats:
            st.markdown("<h2 style='text-align:center;'>Résultats</h2>", unsafe_allow_html=True)
            
            vals = db["votes"][key]
            total = sum(vals.values())
            
            if total > 0:
                # Affichage des résultats
                winner_key = max(vals, key=vals.get)
                winner_pct = int((vals[winner_key] / total) * 100)
                
                st.markdown(f"""
                    <div class="winner-box">
                        <small style="text-transform: uppercase; letter-spacing: 2px; color: #38bdf8;">Tendance</small><br>
                        <span style="font-size: 40px; font-weight: 900;">{winner_pct}%</span><br>
                        <span style="font-size: 18px;">"{data['opts'][winner_key]}"</span>
                    </div>
                """, unsafe_allow_html=True)

                source = pd.DataFrame({
                    "Proposition": [data['opts'][k] for k in data['opts']],
                    "Votes": list(vals.values())
                })

                pie = alt.Chart(source).mark_arc(innerRadius=70, outerRadius=140).encode(
                    theta=alt.Theta(field="Votes", type="quantitative"),
                    color=alt.Color(field="Proposition", legend=alt.Legend(orient='bottom', columns=1, labelColor='white', labelLimit=500)),
                    tooltip=["Proposition", "Votes"]
                ).properties(height=450)

                st.altair_chart(pie, use_container_width=True)
            else:
                # Affichage VIDE (Pas de camembert)
                st.markdown("""
                    <div class="waiting-box">
                        <div style="font-size: 40px;">🗳️</div>
                        <p style="font-size: 20px; font-weight: bold;">Le scrutin est ouvert</p>
                        <p>En attente du premier vote...</p>
                    </div>
                """, unsafe_allow_html=True)

# --- FOOTER ---
st.write("---")
total_global = sum([sum(v.values()) for v in db["votes"].values()])
prog_classe = min(total_global / (23 * 4), 1.0)
st.progress(prog_classe)
st.caption(f"Participation classe : {int(prog_classe*100)}%")