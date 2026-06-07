"""
Visualizzazione interattiva del grafo sentenza->norma.
Genera un file HTML apribile nel browser con pyvis.

Uso:
  python scripts/visualize_graph.py
  python scripts/visualize_graph.py --top-norme 20 --sentenze-per-norma 8
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from loguru import logger

_GRAPH_PATH = Path("C:/project/AiUraLegalLab/workspaces/jurisprudence_graph.json")
_OUTPUT_DEFAULT = Path("C:/project/AiUraLegalLab/workspaces/grafo_giurisprudenza.html")

_ORGANO_COLORS = {
    "cassazione":      "#4A90D9",
    "tar":             "#27AE60",
    "consiglio_stato": "#1ABC9C",
    "corte_conti":     "#E74C3C",
    "corte_cost":      "#9B59B6",
    "unknown":         "#95A5A6",
}
_NORMA_COLOR  = "#F39C12"
_NORMA_BORDER = "#D35400"


def build_subgraph(
    top_norme: int = 30,
    sentenze_per_norma: int = 6,
    output: Path = _OUTPUT_DEFAULT,
) -> None:
    from pyvis.network import Network
    from aiura_legal.jurisprudence.graph_builder import JurisprudenceGraphBuilder

    logger.info("Caricamento grafo da {}", _GRAPH_PATH)
    builder = JurisprudenceGraphBuilder(_GRAPH_PATH)
    g = builder.graph

    sentenze_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "sentenza"]
    norme_nodes    = [n for n, d in g.nodes(data=True) if d.get("type") == "norma"]
    logger.info("Grafo: {} sentenze, {} norme, {} archi",
                len(sentenze_nodes), len(norme_nodes), g.number_of_edges())

    # Top N norme per citazioni
    norme_count = Counter(
        nbr
        for s in sentenze_nodes
        for nbr in g.successors(s)
        if g.nodes[nbr].get("type") == "norma"
    )
    top_n = [norma for norma, _ in norme_count.most_common(top_norme)]
    top_n_set = set(top_n)
    max_count = norme_count.most_common(1)[0][1]

    # Campione sentenze per norma
    norma_to_sentenze: dict[str, list[str]] = defaultdict(list)
    for s in sentenze_nodes:
        for nbr in g.successors(s):
            if nbr in top_n_set and len(norma_to_sentenze[nbr]) < sentenze_per_norma:
                norma_to_sentenze[nbr].append(s)

    selected_sentenze = set(s for lst in norma_to_sentenze.values() for s in lst)
    logger.info("Subgrafo: {} norme + {} sentenze", len(top_n), len(selected_sentenze))

    net = Network(
        height="900px", width="100%",
        bgcolor="#1a1a2e", font_color="white", directed=True,
    )
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -60, "centralGravity": 0.005,
          "springLength": 130, "springConstant": 0.08, "damping": 0.5
        },
        "solver": "forceAtlas2Based",
        "stabilization": { "iterations": 200 }
      },
      "edges": {
        "arrows": { "to": { "enabled": true, "scaleFactor": 0.4 } },
        "color": { "opacity": 0.3 },
        "smooth": { "type": "continuous" }
      },
      "nodes": { "font": { "size": 11, "face": "arial" }, "borderWidth": 2 },
      "interaction": { "hover": true, "tooltipDelay": 80, "hideEdgesOnDrag": true }
    }
    """)

    # Nodi norma
    for norma in top_n:
        count = norme_count[norma]
        label = norma[:38] + ("..." if len(norma) > 38 else "")
        size = 22 + (count / max_count) * 48
        net.add_node(
            norma, label=label,
            title=f"<b>{norma}</b><br>Citata da <b>{count:,}</b> sentenze",
            color={"background": _NORMA_COLOR, "border": _NORMA_BORDER},
            size=size, shape="dot", group="norma",
            font={"size": 12, "color": "#1a1a2e", "bold": True},
        )

    # Nodi sentenza
    for s in selected_sentenze:
        data = g.nodes[s]
        organo = data.get("organo", "unknown")
        numero = data.get("numero", "?")
        anno   = data.get("anno", "?")
        color  = _ORGANO_COLORS.get(organo, _ORGANO_COLORS["unknown"])
        norme_s = list(g.successors(s))
        net.add_node(
            s, label=f"{numero}/{anno}",
            title=(f"<b>{organo.upper()}</b><br>n. {numero}/{anno}"
                   f"<br>Cita {len(norme_s)} norme"),
            color={"background": color, "border": color},
            size=9, shape="dot", group=organo,
        )

    # Archi
    for norma in top_n:
        for s in norma_to_sentenze[norma]:
            ed = g.get_edge_data(s, norma, default={})
            net.add_edge(s, norma, title=ed.get("relation", "cita"),
                         color={"opacity": 0.25})

    legend = """
    <div style="position:fixed;top:16px;right:16px;background:#16213e;
                padding:14px 18px;border-radius:10px;border:1px solid #0f3460;
                color:white;font-family:arial;font-size:13px;z-index:9999;
                box-shadow:0 4px 20px rgba(0,0,0,.5);">
      <b style="font-size:15px">Grafo Giurisprudenza</b><br>
      <span style="color:#aaa;font-size:11px">AiUra LegalLab</span><br><br>
      <span style="color:#F39C12;font-size:17px">&#9679;</span>
        <b>Norma</b> <span style="color:#aaa">(dim. = citazioni)</span><br>
      <span style="color:#4A90D9;font-size:17px">&#9679;</span> Cassazione<br>
      <span style="color:#27AE60;font-size:17px">&#9679;</span> TAR<br>
      <span style="color:#1ABC9C;font-size:17px">&#9679;</span> Cons. Stato<br>
      <span style="color:#E74C3C;font-size:17px">&#9679;</span> Corte dei Conti<br>
      <span style="color:#9B59B6;font-size:17px">&#9679;</span> Corte Cost.<br><br>
      <hr style="border-color:#0f3460;margin:6px 0">
      <i style="color:#aaa;font-size:11px">Hover per dettagli<br>
      Drag per esplorare &bull; Scroll per zoom</i>
    </div>
    <div style="position:fixed;top:16px;left:16px;background:#16213e;
                padding:10px 16px;border-radius:10px;border:1px solid #0f3460;
                color:#aaa;font-family:arial;font-size:12px;z-index:9999;">
      Top {top} norme &bull; {sent} sentenze campione &bull; {edges} archi
    </div>
    """.format(
        top=len(top_n),
        sent=len(selected_sentenze),
        edges=sum(len(v) for v in norma_to_sentenze.values()),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    html = net.generate_html()
    html = html.replace("</body>", legend + "\n</body>")
    output.write_text(html, encoding="utf-8")

    logger.success("Salvato: {}", output)
    logger.info("Apri: file:///{}", str(output).replace("\\", "/"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-norme", type=int, default=30)
    parser.add_argument("--sentenze-per-norma", type=int, default=6)
    parser.add_argument("--output", type=Path, default=_OUTPUT_DEFAULT)
    args = parser.parse_args()
    build_subgraph(args.top_norme, args.sentenze_per_norma, args.output)
