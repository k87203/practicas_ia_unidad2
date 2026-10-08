from collections import deque
import heapq
import networkx as nx
import matplotlib.pyplot as plt

grafo = {
    "Morelia": {"Queretaro": 195, "Toluca": 245},
    "Queretaro": {"Morelia": 195, "Toluca": 190, "CDMX": 213, "Pachuca": 240},
    "Toluca": {"Morelia": 245, "Queretaro": 190, "CDMX": 66, "Cuernavaca": 110},
    "CDMX": {"Queretaro": 213, "Toluca": 66, "Pachuca": 95, "Puebla": 130, "Cuernavaca": 89},
    "Pachuca": {"Queretaro": 240, "CDMX": 95, "Tlaxcala": 150},
    "Cuernavaca": {"Toluca": 110, "CDMX": 89, "Puebla": 160},
    "Tlaxcala": {"Pachuca": 150, "Puebla": 35},
    "Puebla": {"CDMX": 130, "Tlaxcala": 35, "Cuernavaca": 160}
}

def costo(ruta):
    if not ruta:
        return 0
    return sum(grafo[ruta[i]][ruta[i + 1]] for i in range(len(ruta) - 1))

def bfs(inicio, meta):
    cola = deque([(inicio, [inicio])])
    visitados = set()
    expandidos = []

    while cola:
        nodo, ruta = cola.popleft()

        if nodo in visitados:
            continue

        visitados.add(nodo)
        expandidos.append(nodo)

        if nodo == meta:
            return ruta, expandidos

        for v in sorted(grafo[nodo]):
            if v not in visitados:
                cola.append((v, ruta + [v]))

    return None, expandidos

def dfs(inicio, meta):
    pila = [(inicio, [inicio])]
    visitados = set()
    expandidos = []

    while pila:
        nodo, ruta = pila.pop()

        if nodo in visitados:
            continue

        visitados.add(nodo)
        expandidos.append(nodo)

        if nodo == meta:
            return ruta, expandidos

        for v in sorted(grafo[nodo], reverse=True):
            if v not in visitados:
                pila.append((v, ruta + [v]))

    return None, expandidos

def dls(nodo, meta, limite, ruta, expandidos):
    expandidos.append(nodo)

    if nodo == meta:
        return ruta

    if limite == 0:
        return None

    for v in sorted(grafo[nodo]):
        if v not in ruta:
            r = dls(v, meta, limite - 1, ruta + [v], expandidos)
            if r:
                return r

    return None

def ids(inicio, meta, limite_max=20):
    limite = 0

    while limite <= limite_max:
        expandidos = []
        ruta = dls(inicio, meta, limite, [inicio], expandidos)

        if ruta:
            return ruta, expandidos, limite

        limite += 1

    return None, [], None

def ucs(inicio, meta):
    cola = [(0, inicio, [inicio])]
    visitados = set()
    expandidos = []

    while cola:
        c, nodo, ruta = heapq.heappop(cola)

        if nodo in visitados:
            continue

        visitados.add(nodo)
        expandidos.append(nodo)

        if nodo == meta:
            return ruta, c, expandidos

        for v in sorted(grafo[nodo]):
            if v not in visitados:
                heapq.heappush(
                    cola,
                    (c + grafo[nodo][v], v, ruta + [v])
                )

    return None, 0, expandidos

def dibujar():
    G = nx.Graph()

    for a in grafo:
        for b, km in grafo[a].items():
            G.add_edge(a, b, weight=km)

    pos = {
        "Morelia": (0, 2),
        "Queretaro": (2, 3),
        "Toluca": (2, 1),
        "CDMX": (4, 1.5),
        "Pachuca": (5.5, 3),
        "Cuernavaca": (4, 0),
        "Tlaxcala": (7, 2.5),
        "Puebla": (7.5, 1)
    }

    plt.figure(figsize=(12, 7))

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=1800,
        font_weight="bold"
    )

    etiquetas = nx.get_edge_attributes(G, "weight")

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=etiquetas
    )

    plt.title("Practica 4 - Mapa de carreteras")
    plt.savefig("grafo_p4.png", dpi=150, bbox_inches="tight")
    plt.show()

inicio = "Morelia"
meta = "Puebla"

dibujar()

resultados = []

ruta, exp = bfs(inicio, meta)

print("\nBFS")
print("Ruta:", " -> ".join(ruta))
print("Kilometros:", costo(ruta))
print("Nodos expandidos:", len(exp))

resultados.append(
    ("BFS", " -> ".join(ruta), costo(ruta), len(exp), "-")
)

ruta, exp = dfs(inicio, meta)

print("\nDFS")
print("Ruta:", " -> ".join(ruta))
print("Kilometros:", costo(ruta))
print("Nodos expandidos:", len(exp))

resultados.append(
    ("DFS", " -> ".join(ruta), costo(ruta), len(exp), "-")
)

ruta, exp, limite = ids(inicio, meta)

print("\nIDS")
print("Ruta:", " -> ".join(ruta))
print("Kilometros:", costo(ruta))
print("Nodos expandidos:", len(exp))
print("Limite:", limite)

resultados.append(
    ("IDS", " -> ".join(ruta), costo(ruta), len(exp), limite)
)

ruta, km, exp = ucs(inicio, meta)

print("\nUCS")
print("Ruta:", " -> ".join(ruta))
print("Kilometros:", km)
print("Nodos expandidos:", len(exp))

resultados.append(
    ("UCS", " -> ".join(ruta), km, len(exp), "-")
)

print("\nTABLA COMPARATIVA")

print(f"{'Algoritmo':<10}{'Ruta':<50}{'Km':>8}{'Nodos':>10}{'Limite':>10}")


for alg, ruta, km, nodos, limite in resultados:
    print(
        f"{alg:<10}"
        f"{ruta:<50}"
        f"{km:>8}"
        f"{nodos:>10}"
        f"{str(limite):>10}"
    )