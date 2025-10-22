from graphviz import Digraph
from datetime import datetime

dot = Digraph("Sprints", format="png")
dot.attr(rankdir="LR")
dot.node_attr.update({
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "white"
})
today = datetime.now().strftime("%d/%m/%Y")
dot.attr(
    label=f"<<FONT POINT-SIZE='30'>Roadmap conception EPSA 2026 — {today}</FONT>>",
    labelloc="b",
    labeljust="r"
)

with dot.subgraph(name="cluster_legend") as legend:
    legend.attr(label="Légende", labelloc="t", fontsize="30")
    legend.attr(color="white")  # contour invisible

    legend.node("leg_tostart", "À faire", fillcolor="#F2F2F2", style="filled,rounded", fontsize="20")
    legend.node("leg_running", "En cours", fillcolor="#ff951c", style="filled,rounded", fontsize="20")
    legend.node("leg_almost", "Revue à venir", fillcolor="#ff38dd", style="filled,rounded", fontsize="20")
    legend.node("leg_finished", "Terminé", fillcolor="#4deb4d", style="filled,rounded", fontsize="20")
    legend.node("leg_blocked", "Bloqué", fillcolor="#de2b23", style="filled,rounded", fontsize="20")
dot.attr(labeljust="r", labelloc="b")


counter = 0

# --- Visuel noeuds ---
dot.node_attr.update({
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "white"
})

# Couleurs pastel pour les états
STATE_COLORS = {
    "tostart":  ("#F8F8F8", "#B0B0B0", "#F2F2F2"),   # gris très clair (bloc standard)
    "running":  ("#FFF4CC", "#E0B93B", "#ff951c"),   # jaune pastel (en cours)
    "finished": ("#D9F2D9", "#6AAF6A", "#4deb4d"),   # vert calme (terminé)
    "almost": ("#f03ed2", "#b30e97", "#ff38dd"), # Revue technique en cours / à venir
    "blocked":  ("#F9D6D5", "#C74C48", "#de2b23"),   #rouge (bloqué)
    "leaf":     ("#DDE7FF", "#5A7DBA", "#E6EFFF")    # bleu très doux (feuilles)
}


def new_node(label, cluster=None, invisible=False):
    """Crée un nœud, invisible si demandé"""
    global counter
    counter += 1
    name = f"n{counter}"
    if invisible:
        attrs = {"style": "invis", "label": ""}
    else:
        attrs = {"label": label}
    if cluster:
        cluster.node(name, **attrs)
    else:
        dot.node(name, **attrs)
    return name

def parse(expr, cluster=None, is_root=False):
    expr = expr.strip()

    # Séquence
    if expr.startswith("s(") and expr.endswith(")"):
        items = split_args(expr[2:-1])
        nodes = [parse(item, cluster) for item in items]
        for a, b in zip(nodes, nodes[1:]):
            dot.edge(a[1], b[0])
        return nodes[0][0], nodes[-1][1]

    # Parallèle
    elif expr.startswith("p(") and expr.endswith(")"):
        items = split_args(expr[2:-1])
        nodes = [parse(item, cluster) for item in items]

        # Nœuds de début et fin invisibles pour les parallèles internes
        start = new_node("▶", cluster, invisible=not is_root)
        end = new_node("■", cluster, invisible=not is_root)

        for n in nodes:
            dot.edge(start, n[0])
            dot.edge(n[1], end)
        return start, end

    # Bloc hiérarchique
    elif expr.startswith("b(") and expr.endswith(")"):
        args = split_args(expr[2:-1])
        name = args[0].strip('"')

        # Vérifie si un état est présent
        state = None
        content_start_index = 1
        if len(args) > 2 and args[1] in ("running", "finished", "tostart"):
            state = args[1]
            content_start_index = 2

        content = ",".join(args[content_start_index:])
        cluster_name = f"cluster_{counter+1}"

        with dot.subgraph(name=cluster_name) as c:
            # Couleurs selon état
            if state and state in STATE_COLORS:
                fill = STATE_COLORS[state][0]
                border = STATE_COLORS[state][1]
                c.attr(label=name, style="filled,rounded", color=border, fillcolor=fill)
            else:
                # Couleur standard
                c.attr(label=name, style="filled,rounded", color="blue", fillcolor="lightblue")

            start, end = parse(content, cluster=c)
            return start, end


    # Feuille colorée
    if expr.startswith("(") and expr.endswith(")"):
        name, state = split_args(expr[1:-1])
        n = new_node(name, cluster)
        if state in STATE_COLORS:
            fill = STATE_COLORS[state][2]
            border = STATE_COLORS[state][1]
            dot.node(n, style="rounded,filled", fillcolor=fill, color=border)
        return n, n
    # Feuille simple
    else:
        n = new_node(expr, cluster)
        return n, n

def split_args(s):
    depth, start, parts = 0, 0, []
    for i, c in enumerate(s):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(s[start:i].strip())
            start = i + 1
    parts.append(s[start:].strip())
    return [p for p in parts if p]

# --- Lecture depuis fichier ---
with open("sprints_blocs.txt", "r", encoding="utf-8") as f:
    expr = f.read().strip()

# --- Génération du graphe ---
parse(expr, is_root=True)
today = datetime.now().strftime("%Y-%m-%d")

output_filename = dot.render("roadmap_sprints_auto", cleanup=True)


print(f"✅ Graphe généré : {output_filename}")
