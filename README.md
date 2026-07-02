# linkedin-lead — Agent de génération de leads

Agent géré (Anthropic Managed Agents, bêta) qui trouve des leads LinkedIn
qualifiés via recherche web et produit 10 messages d'approche personnalisés
en français, prêts à envoyer manuellement.

> Aucune automatisation LinkedIn : l'agent ne fait que rechercher et rédiger.
> Vous envoyez les messages vous-même — conforme aux conditions d'utilisation
> de LinkedIn.

## Installation

```bash
pip install anthropic
```

## Création de l'agent (une seule fois)

```bash
ant beta:agents create < agent.yaml
# → notez l'ID d'agent retourné
```

## Exécution

```bash
export ANTHROPIC_API_KEY=<votre clé>
export LINKEDIN_LEAD_AGENT_ID=<id de l'agent>
python run_agent.py
```

Le script vous demande de décrire votre lead idéal (ex. « CTO de startups
SaaS françaises de 10 à 50 employés ») puis affiche en streaming la liste
de 10 leads : URL LinkedIn, justification, message personnalisé.
