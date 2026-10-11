"""Etape 6 : export de l'article, du plan, des sources et du controle en ZIP."""

import html
import json
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import markdown


def construire_html(final_md, dossier, statut, valide, refs):
    titre_match = re.match(r"#\s+(.+)", final_md.lstrip())
    titre = titre_match.group(1).strip() if titre_match else "Article"

    # Les sources sont deja ajoutees en Markdown (annexe + definitions) ;
    # on les retire du corps pour les afficher nous-memes avec un style propre.
    corps_md = re.split(r"\n\n## Sources\n\n", final_md, maxsplit=1)[0]
    # Echappement du HTML brut genere par le modele avant conversion Markdown.
    corps_html = markdown.markdown(html.escape(corps_md, quote=False), extensions=["fenced_code", "tables"])

    badge_classe = "badge-ok" if valide else "badge-attention"
    badge_texte = "Controles automatiques passes" if valide else "Brouillon a revoir"

    lignes_sources = "\n".join(
        f'<li><span class="source-id">[{s["id"]}]</span> '
        f'<span class="source-titre">{html.escape(s["titre"])}</span> '
        f'<a class="source-lien" href="{html.escape(s["url"])}" target="_blank" rel="noopener noreferrer">Ouvrir ↗</a></li>'
        for s in refs
    )

    suggestions = dossier.get("suggestions_html") or ""
    bloc_suggestions = (
        f'<section class="carte"><h2>Suggestions de recherche Google</h2>{suggestions}</section>' if suggestions else ""
    )

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titre)}</title>
<style>
  :root {{
    --fond: #f6f7fb;
    --carte: #ffffff;
    --texte: #1b1f27;
    --texte-attenue: #5b6472;
    --accent: #155cb7;
    --bordure: #e3e7ee;
    --ok-fond: #e6f4ea; --ok-texte: #1e7a3b;
    --attn-fond: #fdf1e3; --attn-texte: #9a5b00;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 40px 20px 80px;
    background: var(--fond); color: var(--texte);
    font: 17px/1.7 -apple-system, "Segoe UI", system-ui, sans-serif;
  }}
  .page {{ max-width: 760px; margin: 0 auto; }}
  header.entete {{ margin-bottom: 28px; }}
  h1 {{ font-size: 2rem; line-height: 1.25; margin: 0 0 10px; }}
  .badge {{
    display: inline-block; padding: 4px 12px; border-radius: 999px;
    font-size: 0.8rem; font-weight: 600; letter-spacing: .02em;
  }}
  .badge-ok {{ background: var(--ok-fond); color: var(--ok-texte); }}
  .badge-attention {{ background: var(--attn-fond); color: var(--attn-texte); }}
  .avertissement {{
    margin-top: 14px; padding: 12px 16px; border-left: 3px solid var(--accent);
    background: var(--carte); border-radius: 0 8px 8px 0; color: var(--texte-attenue); font-size: 0.95rem;
  }}
  .carte {{
    background: var(--carte); border: 1px solid var(--bordure); border-radius: 14px;
    padding: 28px 32px; margin-bottom: 24px;
  }}
  .carte h2 {{ margin-top: 0; }}
  h2 {{ font-size: 1.3rem; border-bottom: 1px solid var(--bordure); padding-bottom: 8px; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  pre {{ overflow: auto; background: #eef3fa; padding: 16px; border-radius: 8px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  table th, table td {{ border: 1px solid var(--bordure); padding: 8px 10px; text-align: left; }}
  ul.sources {{ list-style: none; margin: 0; padding: 0; }}
  ul.sources li {{
    display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap;
    padding: 10px 0; border-bottom: 1px solid var(--bordure);
  }}
  ul.sources li:last-child {{ border-bottom: none; }}
  .source-id {{ font-weight: 700; color: var(--accent); min-width: 2.4em; }}
  .source-titre {{ flex: 1; }}
  .source-lien {{ white-space: nowrap; font-size: 0.9rem; }}
  footer {{ text-align: center; color: var(--texte-attenue); font-size: 0.85rem; margin-top: 40px; }}
</style>
</head>
<body>
<div class="page">
  <header class="entete">
    <span class="badge {badge_classe}">{badge_texte}</span>
    <h1>{html.escape(titre)}</h1>
    <p class="avertissement">Verification humaine requise avant toute publication : les citations
    sont reliees aux sources ci-dessous, mais ne garantissent pas une lecture integrale des pages d'origine.</p>
  </header>

  <article class="carte">{corps_html}</article>

  <section class="carte">
    <h2>Sources ({len(refs)})</h2>
    <ul class="sources">{lignes_sources}</ul>
  </section>

  {bloc_suggestions}

  <footer>Genere par l'atelier agents IA - {html.escape(dossier.get("date_recherche_utc", ""))} - modele {html.escape(dossier.get("modele", ""))}</footer>
</div>
</body>
</html>"""


def exporter(dossier_sortie_base, dossier, plan, article, statut, valide, historique):
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:6]
    sortie = Path(dossier_sortie_base) / ("article_" + run_id)
    sortie.mkdir(parents=True, exist_ok=False)
    nom = "article" if valide else "brouillon"
    cites = set(re.findall(r"\[(S\d+)\]", article))
    refs = [s for s in dossier["sources"] if s["id"] in cites]
    annexe = "\n\n## Sources\n\n" + "\n".join(f'- [{s["id"]}] {s["titre"]}' for s in refs)
    definitions = "\n\n" + "\n".join(f'[{s["id"]}]: {s["url"]}' for s in refs)
    final_md = article + annexe + definitions
    (sortie / f"{nom}.md").write_text(final_md, encoding="utf-8")
    (sortie / "plan.md").write_text(plan, encoding="utf-8")
    (sortie / "sources.json").write_text(json.dumps(dossier["sources"], ensure_ascii=False, indent=2), encoding="utf-8")
    (sortie / "dossier_recherche.json").write_text(json.dumps(dossier, ensure_ascii=False, indent=2), encoding="utf-8")
    (sortie / "controle.json").write_text(
        json.dumps({"statut": statut, "verification_humaine_requise": True, "historique": historique}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    document = construire_html(final_md, dossier, statut, valide, refs)
    (sortie / f"{nom}.html").write_text(document, encoding="utf-8")
    archive = sortie.with_suffix(".zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for fichier in sortie.iterdir():
            z.write(fichier, arcname=fichier.name)
    print("Archive creee :", archive)
    return sortie, archive
