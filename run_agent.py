"""Lance une session de l'agent linkedin-lead.

Prérequis :
    pip install anthropic
    ant agents create --file agent.yaml   # une seule fois — notez l'ID
    export LINKEDIN_LEAD_AGENT_ID=<id>
    export ANTHROPIC_API_KEY=<clé>

Usage :
    python run_agent.py
"""

import os

import anthropic

client = anthropic.Anthropic()

AGENT_ID = os.environ["LINKEDIN_LEAD_AGENT_ID"]


def run_lead_session(target_profile: str) -> None:
    """target_profile : description en langage naturel du lead idéal,
    ex. "CTO de startups SaaS françaises de 10 à 50 employés".
    """
    session = client.beta.agents.sessions.create(
        agent_id=AGENT_ID,
        environment={"type": "cloud"},
    )
    session_id = session.id
    print(f"Session créée : {session_id}")

    # Critère de réussite évalué par rubrique (boucle itérer-noter-réviser)
    outcome = {
        "type": "user.define_outcome",
        "rubric": (
            "L'agent a trouvé et produit exactement 10 leads LinkedIn "
            "qualifiés correspondant au profil cible, chacun avec une URL "
            "LinkedIn, une justification de qualification et un message "
            "d'approche personnalisé prêt à envoyer."
        ),
    }

    # Ouvrir le flux d'événements avant d'envoyer le message de lancement
    with client.beta.agents.sessions.events.stream(
        agent_id=AGENT_ID,
        session_id=session_id,
    ) as stream:
        client.beta.agents.sessions.messages.create(
            agent_id=AGENT_ID,
            session_id=session_id,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Trouve 10 leads LinkedIn qualifiés correspondant à "
                        f"ce profil : {target_profile}\n\n"
                        f"Pour chaque lead, fournis :\n"
                        f"- son URL LinkedIn\n"
                        f"- la raison pour laquelle il est qualifié\n"
                        f"- un court message d'approche personnalisé en français\n\n"
                        f"Utilise web_search pour trouver de vrais profils."
                    ),
                }
            ],
            outcome=outcome,
        )

        for event in stream:
            if event.type == "content_block_delta":
                delta = event.delta
                if hasattr(delta, "text"):
                    print(delta.text, end="", flush=True)
            elif event.type == "message_stop":
                print("\n\n--- Session terminée ---")
            elif event.type == "session.outcome":
                print(f"\nRésultat : {event.outcome.get('result', 'inconnu')}")
                print(f"Score : {event.outcome.get('score', 'N/A')}")


if __name__ == "__main__":
    target_profile = input("Décrivez votre lead idéal : ")
    run_lead_session(target_profile)
