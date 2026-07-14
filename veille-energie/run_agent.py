"""Lance une session de veille réglementaire énergie à la demande.

Prérequis :
    pip install anthropic
    ant beta:agents create < agent.yaml   # une seule fois — notez l'ID
    export ANTHROPIC_API_KEY=<clé>
    export VEILLE_ENERGIE_AGENT_ID=<id>
    export VEILLE_ENERGIE_ENV_ID=<id>     # optionnel — réutilise un environnement

Usage :
    python3 run_agent.py
"""

import os

import anthropic

client = anthropic.Anthropic()

AGENT_ID = os.environ["VEILLE_ENERGIE_AGENT_ID"]


def get_environment_id() -> str:
    """Réutilise l'environnement existant si fourni, sinon en crée un."""
    env_id = os.environ.get("VEILLE_ENERGIE_ENV_ID")
    if env_id:
        return env_id
    environment = client.beta.environments.create(
        name="veille-energie-env",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    print(f"Environnement créé : {environment.id}")
    print("Exportez VEILLE_ENERGIE_ENV_ID pour le réutiliser aux prochains runs.\n")
    return environment.id


def run_veille_session(profil: str, periode: str) -> None:
    """profil : description de l'entreprise (secteur, taille, sites),
    ex. "PME industrielle agroalimentaire, 120 salariés, 3 sites tertiaires".
    periode : période de veille, ex. "les 30 derniers jours".
    """
    session = client.beta.sessions.create(
        agent={"type": "agent", "id": AGENT_ID},
        environment_id=get_environment_id(),
        title=f"Veille énergie : {profil[:50]}",
    )
    print(f"Session créée : {session.id}")
    print(
        "Suivi en direct : "
        f"https://platform.claude.com/workspaces/default/sessions/{session.id}"
    )
    print("Veille en cours...\n")

    prompt = (
        f"Réalise une veille réglementaire énergie couvrant {periode}, "
        f"pour ce profil d'entreprise : {profil}\n\n"
        f"Produis le bulletin complet au format défini : synthèse, nouveaux "
        f"textes (avec références et liens vérifiés), échéances à venir, "
        f"actions recommandées et sources."
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
                if getattr(event.stop_reason, "type", None) == "requires_action":
                    continue
                print("\n\n--- Veille terminée ---")
                break
            elif event.type == "session.status_terminated":
                print("\n\n--- Session terminée ---")
                break


if __name__ == "__main__":
    profil = input(
        "Profil de l'entreprise (secteur, taille, sites — vide pour une veille "
        "générale) : "
    ).strip() or "toutes entreprises françaises, tous secteurs"
    periode = input(
        "Période de veille (défaut : les 30 derniers jours) : "
    ).strip() or "les 30 derniers jours"
    run_veille_session(profil, periode)
