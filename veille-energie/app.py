"""Interface web locale pour l'agent veille-energie.

Prérequis :
    pip install anthropic streamlit
    export ANTHROPIC_API_KEY=<clé>
    export VEILLE_ENERGIE_AGENT_ID=<id>
    export VEILLE_ENERGIE_ENV_ID=<id>   # optionnel — réutilise un environnement

Lancement :
    streamlit run app.py
"""

import os

import anthropic
import streamlit as st

st.set_page_config(page_title="Veille Énergie", page_icon="⚡", layout="wide")

st.title("⚡ Veille réglementaire énergie")
st.caption(
    "Décrivez votre entreprise — l'agent surveille les sources officielles "
    "(Légifrance, CRE, EUR-Lex, ADEME...) et produit un bulletin de veille "
    "structuré et sourcé."
)

col1, col2 = st.columns([2, 1])
with col1:
    profil = st.text_area(
        "Profil de l'entreprise",
        placeholder=(
            "Ex. : PME industrielle agroalimentaire, 120 salariés, "
            "3 sites dont 2 bâtiments tertiaires > 1 000 m², flotte de "
            "véhicules en cours d'électrification"
        ),
        height=100,
    )
with col2:
    periode = st.selectbox(
        "Période de veille",
        [
            "les 30 derniers jours",
            "les 7 derniers jours",
            "les 3 derniers mois",
            "les 6 derniers mois",
        ],
    )

if st.button("🔍 Lancer la veille", type="primary"):
    client = anthropic.Anthropic()
    agent_id = os.environ["VEILLE_ENERGIE_AGENT_ID"]

    with st.status("Création de la session...", expanded=False) as status:
        env_id = os.environ.get("VEILLE_ENERGIE_ENV_ID")
        if not env_id:
            environment = client.beta.environments.create(
                name="veille-energie-env",
                config={
                    "type": "cloud",
                    "networking": {"type": "unrestricted"},
                },
            )
            env_id = environment.id
        session = client.beta.sessions.create(
            agent={"type": "agent", "id": agent_id},
            environment_id=env_id,
            title=f"Veille énergie : {(profil or 'générale')[:50]}",
        )
        status.update(
            label="Veille en cours... (quelques minutes)", state="running"
        )

    prompt = (
        f"Réalise une veille réglementaire énergie couvrant {periode}, "
        f"pour ce profil d'entreprise : "
        f"{profil or 'toutes entreprises françaises, tous secteurs'}\n\n"
        f"Produis le bulletin complet au format défini : synthèse, nouveaux "
        f"textes (avec références et liens vérifiés), échéances à venir, "
        f"actions recommandées et sources."
    )

    output = st.empty()
    collected = ""

    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        )
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        collected += block.text
                        output.markdown(collected)
            elif event.type == "session.status_idle":
                if getattr(event.stop_reason, "type", None) == "requires_action":
                    continue
                break
            elif event.type == "session.status_terminated":
                break

    st.success("Veille terminée ! Le bulletin complet est affiché ci-dessus.")
    st.download_button(
        "💾 Télécharger le bulletin (Markdown)",
        collected,
        file_name="bulletin-veille-energie.md",
        mime="text/markdown",
    )
