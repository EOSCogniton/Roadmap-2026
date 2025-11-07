from graphviz import Digraph

dot = Digraph("Sprints", format="png")

# Attributs globaux du graphe
dot.attr(rankdir="LR")

# Attributs par défaut des nœuds
dot.node_attr.update({
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "white"
})

counter = 0

def new_node(label):
    """Crée un nouveau nœud avec un identifiant unique"""
    global counter
    counter += 1
    name = f"n{counter}"
    dot.node(name, label)
    return name

def parse(expr):
    expr = expr.strip()
    if expr.startswith("s(") and expr.endswith(")"):
        items = split_args(expr[2:-1])
        nodes = [parse(item) for item in items]
        # relier en série
        for a, b in zip(nodes, nodes[1:]):
            dot.edge(a[1], b[0])
        return nodes[0][0], nodes[-1][1]

    elif expr.startswith("p(") and expr.endswith(")"):
        items = split_args(expr[2:-1])
        nodes = [parse(item) for item in items]

        # parallèle : même entrée et sortie
        start, end = new_node("▶"), new_node("■")

        # créer un sous-graphe invisible pour aligner les noeuds
        with dot.subgraph() as s:
            s.attr(rank="same")
            for n in nodes:
                s.node(n[0])  # entrée de la branche
                s.node(n[1])  # sortie de la branche

        for n in nodes:
            dot.edge(start, n[0])
            dot.edge(n[1], end)

        return start, end

    else:
        # feuille = tâche simple
        n = new_node(expr)
        return n, n

def split_args(s):
    """Découpe les arguments d'une expression en tenant compte des parenthèses imbriquées"""
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

# --- Lecture depuis un fichier texte ---
with open("sprints.txt", "r", encoding="utf-8") as f:
    expr = f.read().strip()

# --- Génération du graphe ---
parse(expr)

output_path = dot.render("roadmap_sprints_auto", cleanup=True)
print(f"✅ Graphe généré : {output_path}")
