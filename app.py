"""Interface web locale pour l'agent linkedin-lead.

Prérequis :
    pip install anthropic streamlit
    export ANTHROPIC_API_KEY=<clé>
    export LINKEDIN_LEAD_AGENT_ID=<id>

Lancement :
    streamlit run app.py
"""

import os

import anthropic
import streamlit as st

st.set_page_config(page_title="LinkedIn Lead", page_icon="🎯", layout="wide")

st.title("🎯 LinkedIn Lead")
st.caption(
    "Décrivez votre client idéal — l'agent cherche 10 leads qualifiés et "
    "rédige un message personnalisé pour chacun."
)

target_profile = st.text_area(
    "Votre lead idéal",
    placeholder=(
        "Ex. : Dirigeants de PME françaises dans les services B2B, "
        "intéressés par l'automatisation et l'IA"
    ),
    height=100,
)

if st.button("🔍 Trouver 10 leads", type="primary", disabled=not target_profile):
    client = anthropic.Anthropic()
    agent_id = os.environ["LINKEDIN_LEAD_AGENT_ID"]

    with st.status("Création de la session...", expanded=False) as status:
        environment = client.beta.environments.create(
            name="linkedin-lead-env",
            config={
                "type": "cloud",
                "networking": {"type": "unrestricted"},
            },
        )
        session = client.beta.sessions.create(
            agent={"type": "agent", "id": agent_id},
            environment_id=environment.id,
            title=f"Leads : {target_profile[:60]}",
        )
        status.update(
            label="Recherche en cours... (quelques minutes)", state="running"
        )

    prompt = (
        f"Trouve 10 leads LinkedIn qualifiés correspondant à ce profil : "
        f"{target_profile}\n\n"
        f"Pour chaque lead, fournis :\n"
        f"- son URL LinkedIn\n"
        f"- la raison pour laquelle il est qualifié\n"
        f"- un court message d'approche personnalisé en français\n\n"
        f"Utilise web_search pour trouver de vrais profils."
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
            elif event.type in ("session.status_idle", "session.status_terminated"):
                break

    st.success("Recherche terminée ! Copiez les messages ci-dessus.")
