from graphviz import Digraph

dot = Digraph("Sprints", format="png")
dot.attr(rankdir="LR")
dot.node_attr.update({
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "white"
})

counter = 0

def new_node(label, cluster=None):
    global counter
    counter += 1
    name = f"n{counter}"
    if cluster:
        cluster.node(name, label)
    else:
        dot.node(name, label)
    return name

def parse(expr, cluster=None):
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
        start, end = new_node("▶", cluster), new_node("■", cluster)
        for n in nodes:
            dot.edge(start, n[0])
            dot.edge(n[1], end)
        return start, end

    # Bloc hiérarchique
    elif expr.startswith("b(") and expr.endswith(")"):
        args = split_args(expr[2:-1])
        name = args[0].strip('"')
        content = ",".join(args[1:])
        cluster_name = f"cluster_{counter+1}"
        with dot.subgraph(name=cluster_name) as c:
            c.attr(label=name)
            c.attr(style="filled,rounded")
            c.attr(color="blue")
            c.attr(fillcolor="lightblue")
            start, end = parse(content, cluster=c)
            return start, end

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

with open("sprints_blocs.txt", "r", encoding="utf-8") as f:
    expr = f.read().strip()

parse(expr)

output_path = dot.render("roadmap_sprints_auto", cleanup=True)
print(f"✅ Graphe généré : {output_path}")
