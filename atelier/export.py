"""Etape 6 : export de l'article, du plan, des sources et du controle en ZIP."""

import html
import json
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import markdown


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
    # Echappement du HTML brut genere par le modele avant conversion Markdown.
    body = markdown.markdown(html.escape(final_md, quote=False), extensions=["fenced_code", "tables"])
    document = (
        "<!doctype html><html lang='fr'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Article et sources</title><style>body{font:18px/1.7 system-ui;"
        "max-width:850px;margin:40px auto;padding:0 24px}a{color:#155cb7}"
        "pre{overflow:auto;background:#eef3fa;padding:18px}</style>"
        f"<p><strong>{statut}</strong> - Verification humaine requise.</p>"
        + body
        + "<section><h2>Suggestions de recherche Google</h2>"
        + dossier["suggestions_html"]
        + "</section></html>"
    )
    (sortie / f"{nom}.html").write_text(document, encoding="utf-8")
    archive = sortie.with_suffix(".zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for fichier in sortie.iterdir():
            z.write(fichier, arcname=fichier.name)
    print("Archive creee :", archive)
    return sortie, archive
