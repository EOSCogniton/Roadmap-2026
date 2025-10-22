from graphviz import Digraph

# Création du graphe orienté
dot = Digraph("DecisionTree", format="png")
dot.attr(rankdir="TB", fontsize="10", fontname="Arial")

# Nœud racine
dot.node("LAS", "Position des points LAS", shape="rectangle", style="rounded")

# Branche CAO
dot.node("CAO", "CAO", shape="rectangle", style="rounded")
dot.edge("LAS", "CAO")

dot.node("Conflit", "Conflit OK ?", shape="diamond", style="rounded")
dot.edge("CAO", "Conflit")

dot.node("FEA", "Analyse FEA", shape="rectangle", style="rounded")
dot.edge("Conflit", "FEA", label="Oui")

dot.node("Dim", "Dimensionnement OK ?", shape="diamond", style="rounded")
dot.edge("FEA", "Dim")

dot.node("OKfin", "OK", shape="rectangle", style="rounded")
dot.edge("Dim", "OKfin", label="Oui")

# retour Dim -> CAO
dot.edge("Dim", "CAO", label="Non", color="red")

# retour Conflit -> LAS
dot.edge("Conflit", "LAS", label="Non", color="red")

# Branche Mise à jour du filaire
dot.node("Filaire", "Mise à jour du filaire", shape="rectangle", style="rounded")
dot.edge("LAS", "Filaire")

dot.node("Templates", "Templates OK ?", shape="diamond", style="rounded")
dot.edge("Filaire", "Templates")

dot.node("Percy", "Percy OK ?", shape="diamond", style="rounded")
dot.edge("Templates", "Percy", label="Oui")

dot.node("OK", "OK", shape="rectangle", style="rounded")
dot.edge("Percy", "OK", label="Oui")

# retours côté droit
dot.edge("Percy", "LAS", label="Non", color="red")
dot.edge("Templates", "LAS", label="Non", color="red")




# Export en PNG
output_path = "arbre_decision"
dot.render(output_path, cleanup=True)

output_path + ".png"
