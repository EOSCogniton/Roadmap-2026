from graphviz import Digraph
from datetime import datetime
import json

dot = Digraph("Sprints", format="png")
dot.attr(rankdir="LR")
dot.node_attr.update({
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "white",
    "fontsize": "10"
})

today = datetime.now().strftime("%d/%m/%Y")
dot.attr(
    label=f"<<FONT POINT-SIZE='30'>Roadmap conception EPSA 2026 — {today}</FONT>>",
    labelloc="b",
    labeljust="r"
)

# --- Légende ---
with dot.subgraph(name="cluster_legend") as legend:
    legend.attr(label="Légende", labelloc="t", fontsize="20", color="white")

    legend.node("leg_tostart", "À faire", fillcolor="#FFFFFF", style="filled,rounded", fontsize="12")
    legend.node("leg_running", "En cours", fillcolor="#ff951c", style="filled,rounded", fontsize="12")
    legend.node("leg_almost", "Revue à venir", fillcolor="#ff38dd", style="filled,rounded", fontsize="12")
    legend.node("leg_finished", "Terminé", fillcolor="#4deb4d", style="filled,rounded", fontsize="12")
    legend.node("leg_blocked", "Bloqué", fillcolor="#de2b23", style="filled,rounded", fontsize="12")

dot.attr(labeljust="r", labelloc="b")

counter = 0

# --- Couleurs pastel pour les états ---
STATE_COLORS = {
    "tostart":  ("#E6EEF8", "#000000", "#FFFFFF"),
    "running":  ("#FFF4CC", "#E0B93B", "#ff951c"),
    "finished": ("#D9F2D9", "#6AAF6A", "#4deb4d"),
    "almost":   ("#f03ed2", "#b30e97", "#ff38dd"),
    "blocked":  ("#F9D6D5", "#C74C48", "#de2b23"),
    "leaf":     ("#DDE7FF", "#5A7DBA", "#E6EFFF")
}


def new_node(label, cluster=None, invisible=False, fill=None, color=None):
    """Crée un nœud (invisible ou coloré selon état)"""
    global counter
    counter += 1
    name = f"n{counter}"
    attrs = {"fontsize": "10"}

    if invisible:
        attrs.update({"style": "invis", "label": ""})
    else:
        attrs.update({"label": label, "style": "rounded,filled"})
        if fill:
            attrs["fillcolor"] = fill
        if color:
            attrs["color"] = color

    if cluster:
        cluster.node(name, **attrs)
    else:
        dot.node(name, **attrs)
    return name


def parse_json(node, cluster=None, is_root=False):
    """Lecture récursive du JSON et génération des liens"""
    ntype = node.get("type")
    state = node.get("state")
    name = node.get("name")
    children = node.get("children", [])

    # Séquence
    if ntype == "s":
        parsed = [parse_json(child, cluster) for child in children]
        for a, b in zip(parsed, parsed[1:]):
            dot.edge(a[1], b[0])
        return parsed[0][0], parsed[-1][1]

    # Parallèle
    elif ntype == "p":
        parsed = [parse_json(child, cluster) for child in children]
        start = new_node("▶", cluster, invisible=not is_root)
        end = new_node("■", cluster, invisible=not is_root)
        for n in parsed:
            dot.edge(start, n[0])
            dot.edge(n[1], end)
        return start, end

    # Bloc hiérarchique
    elif ntype == "b":
        cluster_name = f"cluster_{counter+1}"
        with dot.subgraph(name=cluster_name) as c:
            if state and state in STATE_COLORS:
                fill, border = STATE_COLORS[state][0], STATE_COLORS[state][1]
                c.attr(label=name, style="filled,rounded", color=border, fillcolor=fill)
            else:
                c.attr(label=name, style="filled,rounded", color="blue", fillcolor="lightblue")

            start, end = parse_json({"type": "s", "children": children}, cluster=c)
            return start, end

    # Feuille simple
    else:
        if state and state in STATE_COLORS:
            fill, border = STATE_COLORS[state][2], STATE_COLORS[state][1]
        else:
            fill, border = STATE_COLORS["tostart"][2], STATE_COLORS["tostart"][1]
        n = new_node(name or "?", cluster, fill=fill, color=border)
        return n, n


# --- Lecture du JSON ---
with open("sprints.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Génération du graphe ---
parse_json(data["root"], is_root=True)

# --- Sortie avec la date du jour ---
output_filename = dot.render("roadmap_sprints_latest", cleanup=True)
print(f"✅ Graphe généré : {output_filename}")
