"""Planifie la veille en automatique : un bulletin chaque lundi à 8h (Paris).

Crée un « scheduled deployment » Managed Agents : chaque déclenchement ouvre
une nouvelle session qui produit le bulletin hebdomadaire, consultable dans
la console Anthropic (https://platform.claude.com).

Prérequis :
    pip install anthropic
    export ANTHROPIC_API_KEY=<clé>
    export VEILLE_ENERGIE_AGENT_ID=<id>
    export VEILLE_ENERGIE_ENV_ID=<id>
    export VEILLE_ENERGIE_PROFIL="PME industrielle, 120 salariés..."  # optionnel

Usage :
    python3 schedule_agent.py
"""

import os

import anthropic

client = anthropic.Anthropic()

AGENT_ID = os.environ["VEILLE_ENERGIE_AGENT_ID"]
ENV_ID = os.environ["VEILLE_ENERGIE_ENV_ID"]
PROFIL = os.environ.get(
    "VEILLE_ENERGIE_PROFIL", "toutes entreprises françaises, tous secteurs"
)

PROMPT = (
    f"Réalise la veille réglementaire énergie hebdomadaire (les 7 derniers "
    f"jours) pour ce profil d'entreprise : {PROFIL}\n\n"
    f"Produis le bulletin complet au format défini : synthèse, nouveaux "
    f"textes (avec références et liens vérifiés), échéances à venir, "
    f"actions recommandées et sources."
)

if not hasattr(client.beta, "deployments"):
    raise SystemExit(
        "Votre version du SDK anthropic n'expose pas encore les deployments. "
        "Mettez à jour : pip install -U anthropic"
    )

deployment = client.beta.deployments.create(
    name="Veille énergie hebdomadaire",
    agent=AGENT_ID,
    environment_id=ENV_ID,
    initial_events=[
        {
            "type": "user.message",
            "content": [{"type": "text", "text": PROMPT}],
        }
    ],
    schedule={
        "type": "cron",
        "expression": "0 8 * * 1",  # chaque lundi à 8h00
        "timezone": "Europe/Paris",
    },
)

print(f"Deployment créé : {deployment.id}")
print(f"Prochaines exécutions : {deployment.schedule.upcoming_runs_at}")
print(
    "\nTest immédiat sans attendre lundi :\n"
    f"  ant beta:deployments run --deployment-id {deployment.id}\n"
    "Mise en pause :\n"
    f"  ant beta:deployments pause --deployment-id {deployment.id}"
)
