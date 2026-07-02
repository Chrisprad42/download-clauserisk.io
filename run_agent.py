"""Lance une session de l'agent linkedin-lead.

Prérequis :
    pip install anthropic
    ant beta:agents create < agent.yaml   # une seule fois — notez l'ID
    export ANTHROPIC_API_KEY=<clé>
    export LINKEDIN_LEAD_AGENT_ID=<id>

Usage :
    python3 run_agent.py
"""

import os

import anthropic

client = anthropic.Anthropic()

AGENT_ID = os.environ["LINKEDIN_LEAD_AGENT_ID"]


def run_lead_session(target_profile: str) -> None:
    """target_profile : description en langage naturel du lead idéal,
    ex. "CTO de startups SaaS françaises de 10 à 50 employés".
    """
    environment = client.beta.environments.create(
        name="linkedin-lead-env",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )

    session = client.beta.sessions.create(
        agent={"type": "agent", "id": AGENT_ID},
        environment_id=environment.id,
        title=f"Leads : {target_profile[:60]}",
    )
    print(f"Session créée : {session.id}\nRecherche en cours...\n")

    prompt = (
        f"Trouve 10 leads LinkedIn qualifiés correspondant à ce profil : "
        f"{target_profile}\n\n"
        f"Pour chaque lead, fournis :\n"
        f"- son URL LinkedIn\n"
        f"- la raison pour laquelle il est qualifié\n"
        f"- un court message d'approche personnalisé en français\n\n"
        f"Utilise web_search pour trouver de vrais profils."
    )

    # Stream-first : ouvrir le flux avant d'envoyer le message
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
                        print(block.text, end="", flush=True)
            elif event.type == "session.status_idle":
                print("\n\n--- Recherche terminée ---")
                break
            elif event.type == "session.status_terminated":
                print("\n\n--- Session terminée ---")
                break


if __name__ == "__main__":
    target_profile = input("Décrivez votre lead idéal : ")
    run_lead_session(target_profile)
