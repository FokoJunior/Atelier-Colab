# Atelier agents IA — De la recherche à l'article sourcé

Version locale (hors Google Colab) du notebook [`Agents_IA_Recherche_Article_Colab.ipynb`](Agents_IA_Recherche_Article_Colab.ipynb).

Le programme reçoit un sujet, effectue une recherche Google réelle via Gemini, organise un
dossier de preuves, fait écrire un article en français par un agent IA, le fait relire et
corriger par un autre agent, puis exporte le résultat (Markdown, HTML, JSON, archive ZIP).

## Fonctionnement en bref

1. **Recherche** — l'outil Google Search est transmis à l'API Gemini. Le modèle choisit les
   requêtes ; le programme exige au moins 3 sources réellement citées (sinon il s'arrête).
2. **Planification** — un agent produit un plan Markdown à partir du dossier de preuves.
3. **Rédaction** — un agent écrit l'article (900 à 1400 mots), avec des citations `[S1]`, `[S2]`...
   reliées aux sources trouvées, sans jamais inventer d'URL.
4. **Relecture** — un agent contrôle l'article contre les preuves et rend un avis structuré
   (`accepté` / `corrections`). Un contrôle automatique (regex) vérifie en plus la structure
   (titre H1, sections H2, absence d'URL/HTML/images) et le nombre de sources citées.
5. **Correction** — jusqu'à 2 versions : si la version 1 n'est pas validée, les corrections sont
   renvoyées au rédacteur pour une version 2.
6. **Export** — un dossier `sorties/article_<id>/` est créé avec l'article, le plan, les sources,
   le dossier de recherche complet et un rapport de contrôle, puis compressé en `.zip`.

**Important :** la relecture automatique ne remplace pas une vérification humaine des faits.
Les segments cités proviennent de la réponse de Gemini associée aux sources, pas d'une lecture
intégrale garantie des pages d'origine. Vérifiez les sources avant toute publication.

## Prérequis

- Python 3.11+ (testé avec Python 3.14)
- Une clé API Gemini, créée sur [Google AI Studio](https://aistudio.google.com/apikey)
- Un modèle Gemini compatible avec Google Search et les sorties structurées
  (`gemini-3.8-flash` par défaut — `gemini-2.5-flash` n'est plus disponible aux nouveaux comptes)

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copiez `.env.example` en `.env` et renseignez votre clé :

```
GOOGLE_API_KEY=votre_cle_ici
```

`.env` est ignoré par git (`.gitignore`) : ne la partagez jamais, ne la commitez jamais.

## Utilisation

```powershell
.\.venv\Scripts\python.exe atelier_agents.py --sujet "votre sujet" --public "votre public" --angle "votre angle"
```

### Exemple

```powershell

.\.venv\Scripts\python.exe atelier_agents.py `
  --sujet "Bonnes pratiques de sauvegarde de donnees pour les PME" `
  --public "dirigeants de PME" `
  --angle "pratique, cout maitrise"


```

Sortie attendue dans le terminal :

```
Configuration prete. Modele : gemini-3.8-flash
{'google-adk': '2.2.0', 'google-genai': '2.28.0', 'Markdown': '3.11'}

--- Etape 3 : recherche reelle ---
Requetes reellement renvoyees : [...]
Sources etayees : 18
S1 ... S2 ... S3 ...

--- Etape 4-5 : agents, redaction et correction ---
Redaction et controle : version 1/2
Statut : CONTROLES_AUTOMATIQUES_PASSES

--- Etape 6 : export ---
Archive creee : sorties\article_20261011T062414Z_c7cd9a.zip

Termine. Dossier : sorties\article_20261011T062414Z_c7cd9a | Archive : sorties\article_20261011T062414Z_c7cd9a.zip
```

Le dossier `sorties\article_20261011T062414Z_c7cd9a\` contient alors `article.md`, `article.html`,
`plan.md`, `sources.json`, `dossier_recherche.json` et `controle.json`, en plus de l'archive `.zip`.

Options disponibles :

| Option | Défaut | Description |
| --- | --- | --- |
| `--sujet` | sujet de démonstration (veille cybersécurité) | Le sujet de l'article |
| `--public` | public de démonstration | Le public visé, pour adapter le ton |
| `--angle` | angle de démonstration | L'angle éditorial |
| `--modele` | `gemini-3.8-flash` | Modèle Gemini à utiliser (doit accepter Google Search + sorties structurées) |
| `--sortie` | `sorties` | Dossier local où créer `article_<id>/` et l'archive `.zip` |
| `--copier-vers` | *(aucun)* | Dossier local optionnel où copier aussi l'archive (équivalent local de l'étape Drive du notebook) |

Résultat produit dans `sorties/article_<id>/` :

- `article.md` ou `brouillon.md` (selon que le contrôle a été validé), avec la liste des sources
- `article.html` ou `brouillon.html` — version de lecture avec les suggestions Google
- `plan.md` — le plan généré par l'agent Planificateur
- `sources.json` — les sources retenues (id, titre, URL)
- `dossier_recherche.json` — le dossier de preuves complet (requêtes, sources, segments)
- `controle.json` — le statut final et l'historique des versions/corrections
- `article_<id>.zip` — l'archive de tous les fichiers ci-dessus

## Structure du code

```
atelier_agents.py          # point d'entree CLI (orchestration uniquement)
atelier/
├── config.py               # constantes (MIN_SOURCES, MAX_VERSIONS) + chargement de la cle API
├── recherche.py             # etape 3 : recherche Google reelle + dossier de preuves
├── pipeline.py              # etapes 4-5 : construit les agents, enchaine plan -> redaction -> relecture
├── export.py                 # etape 6 : export Markdown/HTML/JSON + archive ZIP
└── agents/
    ├── commun.py             # regle de securite partagee (donnees non fiables) + schema Avis
    ├── planificateur.py      # agent qui produit le plan
    ├── redacteur.py            # agent qui redige l'article
    ├── relecteur.py            # agent qui controle et rend un avis structure
    ├── runner.py                # execution generique d'un agent ADK dans sa propre session
    └── controle.py              # controle automatique des references [S1]... par regex
```

## Dépannage

| Situation | Action |
| --- | --- |
| Clé API manquante ou invalide | Vérifiez `.env`, ou saisissez la clé quand le programme la demande |
| Erreur 401/403 | Vérifiez la clé, le projet et les restrictions d'accès à l'API |
| Erreur 404 (modèle) | Choisissez un modèle disponible acceptant Google Search et les sorties structurées (`--modele`) |
| Erreur 429 (quota) | Vérifiez le quota et la facturation ; patientez avant de relancer |
| `Aucune recherche web attestée` | Précisez le sujet (`--sujet`) et relancez |
| `Dossier insuffisant` | Le sujet n'a pas assez de sources fiables ; choisissez un sujet plus documenté |
| Statut final `BROUILLON_A_REVOIR` | Lisez `controle.json` pour voir les corrections manquantes après les 2 versions autorisées |

## Origine

Adaptation locale de l'atelier Google Colab « De la recherche à l'article », basé sur le
codelab Google Cloud *Build your first AI agent in 8 minutes* (Gemini + Google ADK).
