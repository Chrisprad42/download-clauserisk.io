# veille-energie — Agent de veille réglementaire énergie

Agent géré (Anthropic Managed Agents, bêta) qui surveille la réglementation
de l'énergie applicable aux entreprises françaises et produit un bulletin de
veille structuré, en français et sourcé.

## Ce que couvre la veille

- **Sources officielles** : Légifrance / Journal Officiel, CRE, ministère
  chargé de l'énergie (DGEC), EUR-Lex, ADEME, RTE.
- **Thématiques** : décret tertiaire (Éco Énergie Tertiaire), décret BACS,
  audits énergétiques obligatoires, BEGES, CSRD / ESRS E1, CEE, fiscalité
  de l'énergie, TURPE et dispositifs post-ARENH, loi APER (solarisation,
  ENR, autoconsommation), bornes de recharge IRVE.

Chaque bulletin contient : une synthèse, les nouveaux textes (références et
liens vérifiés à la source), un calendrier des échéances, des actions
recommandées adaptées au profil d'entreprise fourni, et la liste des sources.

> L'agent ne cite que des textes réellement trouvés et vérifiés via la
> recherche web. Le bulletin est un outil de veille, pas un avis juridique.

## Installation

```bash
pip install anthropic
```

## Création de l'agent (une seule fois)

```bash
ant beta:agents create < agent.yaml
# → notez l'ID d'agent retourné
```

## Veille à la demande (CLI)

```bash
export ANTHROPIC_API_KEY=<votre clé>
export VEILLE_ENERGIE_AGENT_ID=<id de l'agent>
python run_agent.py
```

Le script demande le profil de votre entreprise (secteur, taille, sites) et
la période à couvrir, puis affiche le bulletin en streaming. Au premier run
il crée un environnement et affiche son ID — exportez-le pour le réutiliser :

```bash
export VEILLE_ENERGIE_ENV_ID=<id de l'environnement>
```

## Interface web locale

```bash
pip install streamlit
streamlit run app.py
```

## Veille automatique hebdomadaire

Pour recevoir un bulletin chaque lundi à 8h (heure de Paris) sans rien
lancer manuellement :

```bash
export VEILLE_ENERGIE_PROFIL="PME industrielle, 120 salariés, 3 sites"  # optionnel
python schedule_agent.py
```

Le script crée un « scheduled deployment » : chaque lundi, une session est
ouverte automatiquement et le bulletin est consultable dans la console
Anthropic. Commandes utiles :

```bash
ant beta:deployments run --deployment-id <id>     # test immédiat
ant beta:deployments pause --deployment-id <id>   # mise en pause
```

## Fichiers

| Fichier | Rôle |
|---|---|
| `agent.yaml` | Configuration de l'agent (modèle, prompt système, outils) |
| `run_agent.py` | Veille à la demande en ligne de commande |
| `app.py` | Interface web locale (Streamlit) |
| `schedule_agent.py` | Planification hebdomadaire (deployment) |
