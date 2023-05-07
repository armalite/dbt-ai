import networkx as nx

# Assume that you have a list of models and their dependencies
models = [
    {
        "name": "model_a",
        "dependencies": ["model_b"]
    },
    {
        "name": "model_b",
        "dependencies": []
    }
]

# Create a directed graph
graph = nx.DiGraph()

# Add nodes to the graph
for model in models:
    graph.add_node(model["name"])

# Add edges to the graph
for model in models:
    for dep in model["dependencies"]:
        graph.add_edge(dep, model["name"])

# Draw the graph
nx.draw(graph, with_labels=True)
