import heapq
import time

grafo = {
    "Morelia": {"Queretaro": 195, "Toluca": 245},
    "Queretaro": {"CDMX": 213, "Morelia": 195, "Pachuca": 240, "Toluca": 190},
    "Toluca": {"CDMX": 66, "Cuernavaca": 110, "Morelia": 245, "Queretaro": 190},
    "CDMX": {"Cuernavaca": 89, "Pachuca": 95, "Puebla": 130, "Queretaro": 213, "Toluca": 66},
    "Pachuca": {"CDMX": 95, "Queretaro": 240, "Tlaxcala": 150},
    "Cuernavaca": {"CDMX": 89, "Puebla": 160, "Toluca": 110},
    "Tlaxcala": {"Pachuca": 150, "Puebla": 35},
    "Puebla": {"CDMX": 130, "Cuernavaca": 160, "Tlaxcala": 35}
}

hmap = {
    "Morelia": 330,
    "Toluca": 150,
    "Queretaro": 250,
    "CDMX": 100,
    "Pachuca": 110,
    "Cuernavaca": 100,
    "Tlaxcala": 30,
    "Puebla": 0
}

def costos_reales(meta):
    dist = {meta: 0}
    cola = [(0, meta)]

    while cola:
        d, actual = heapq.heappop(cola)

        if d != dist[actual]:
            continue

        for vecino, km in grafo[actual].items():
            nuevo = d + km

            if nuevo < dist.get(vecino, float("inf")):
                dist[vecino] = nuevo
                heapq.heappush(cola, (nuevo, vecino))

    return dist

def verificar_heuristica(meta):
    consistente = True

    print("\nVERIFICACION DE CONSISTENCIA")
  
    print(f"{'Arco':<30}{'h(n)':>8}{'c+h(n2)':>12}{'Cumple':>10}")
   

    for ciudad in grafo:
        for vecino, km in grafo[ciudad].items():
            valor = km + hmap[vecino]
            cumple = hmap[ciudad] <= valor

            if not cumple:
                consistente = False

            print(
                f"{ciudad + ' -> ' + vecino:<30}"
                f"{hmap[ciudad]:>8}"
                f"{valor:>12}"
                f"{'SI' if cumple else 'NO':>10}"
            )

    reales = costos_reales(meta)
    admisible = True

    print("\nVERIFICACION DE ADMISIBILIDAD")
    print(f"{'Ciudad':<15}{'h(n)':>10}{'h*(n)':>10}{'Cumple':>10}")

    for ciudad in grafo:
        cumple = hmap[ciudad] <= reales[ciudad]

        if not cumple:
            admisible = False

        print(
            f"{ciudad:<15}"
            f"{hmap[ciudad]:>10}"
            f"{reales[ciudad]:>10}"
            f"{'SI' if cumple else 'NO':>10}"
        )

    print("\nConsistente:", "SI" if consistente else "NO")
    print("Admisible:", "SI" if admisible else "NO")

def buscar_mapa(inicio, meta, tipo):
    cola = []
    mejor = {inicio: 0}
    visitados = set()
    expandidos = 0

    valor = hmap[inicio] if tipo != "UCS" else 0
    heapq.heappush(cola, (valor, 0, inicio, [inicio]))

    while cola:
        f, g, actual, ruta = heapq.heappop(cola)

        if tipo == "Voraz":
            if actual in visitados:
                continue
            visitados.add(actual)
        else:
            if g != mejor.get(actual):
                continue

        expandidos += 1

        if actual == meta:
            return ruta, g, expandidos

        for vecino in sorted(grafo[actual]):
            nuevo_g = g + grafo[actual][vecino]

            if tipo == "Voraz":
                if vecino not in visitados:
                    heapq.heappush(
                        cola,
                        (hmap[vecino], nuevo_g, vecino, ruta + [vecino])
                    )

            elif nuevo_g < mejor.get(vecino, float("inf")):
                mejor[vecino] = nuevo_g

                if tipo == "UCS":
                    nuevo_f = nuevo_g
                else:
                    nuevo_f = nuevo_g + hmap[vecino]

                heapq.heappush(
                    cola,
                    (nuevo_f, nuevo_g, vecino, ruta + [vecino])
                )

    return None, 0, expandidos

inicio_puzzle = (7, 2, 4, 5, 0, 6, 8, 3, 1)
meta_puzzle = (0, 1, 2, 3, 4, 5, 6, 7, 8)

pos_meta = {
    valor: i
    for i, valor in enumerate(meta_puzzle)
}

def vecinos_puzzle(estado):
    pos = estado.index(0)
    fila = pos // 3
    col = pos % 3
    movimientos = []

    if fila > 0:
        movimientos.append(pos - 3)

    if fila < 2:
        movimientos.append(pos + 3)

    if col > 0:
        movimientos.append(pos - 1)

    if col < 2:
        movimientos.append(pos + 1)

    for nueva_pos in movimientos:
        nuevo = list(estado)
        nuevo[pos], nuevo[nueva_pos] = nuevo[nueva_pos], nuevo[pos]
        yield tuple(nuevo)

def h1(estado):
    return sum(
        1
        for i in range(9)
        if estado[i] != 0 and estado[i] != meta_puzzle[i]
    )

def h2(estado):
    total = 0

    for i, valor in enumerate(estado):
        if valor != 0:
            j = pos_meta[valor]
            total += abs(i // 3 - j // 3)
            total += abs(i % 3 - j % 3)

    return total

def resolver_puzzle(tipo):
    if tipo == "UCS":
        h = lambda estado: 0

    elif tipo == "Voraz":
        h = h2

    elif tipo == "A*h1":
        h = h1

    else:
        h = h2

    cola = []
    mejor = {inicio_puzzle: 0}
    visitados = set()
    contador = 0
    expandidos = 0

    heapq.heappush(
        cola,
        (h(inicio_puzzle), 0, contador, inicio_puzzle)
    )

    while cola:
        f, g, _, actual = heapq.heappop(cola)

        if tipo == "Voraz":
            if actual in visitados:
                continue
            visitados.add(actual)

        else:
            if g != mejor.get(actual):
                continue

        expandidos += 1

        if actual == meta_puzzle:
            return g, expandidos

        for vecino in vecinos_puzzle(actual):
            nuevo_g = g + 1
            contador += 1

            if tipo == "Voraz":
                if vecino not in visitados:
                    heapq.heappush(
                        cola,
                        (
                            h(vecino),
                            nuevo_g,
                            contador,
                            vecino
                        )
                    )

            elif nuevo_g < mejor.get(vecino, float("inf")):
                mejor[vecino] = nuevo_g

                heapq.heappush(
                    cola,
                    (
                        nuevo_g + h(vecino),
                        nuevo_g,
                        contador,
                        vecino
                    )
                )

    return None, expandidos

def main():
    verificar_heuristica("Puebla")

    print("\nMAPA MORELIA -> PUEBLA")

    resultados_mapa = []

    for tipo in ["UCS", "Voraz", "A*"]:
        inicio = time.perf_counter()

        ruta, km, nodos = buscar_mapa(
            "Morelia",
            "Puebla",
            tipo
        )

        tiempo = time.perf_counter() - inicio

        print("\n" + tipo)
        print("Ruta:", " -> ".join(ruta))
        print("Kilometros:", km)
        print("Nodos expandidos:", nodos)
        print(f"Tiempo: {tiempo:.6f} s")

        resultados_mapa.append(
            (
                tipo,
                " -> ".join(ruta),
                km,
                nodos,
                tiempo
            )
        )

    print("\nTABLA COMPARATIVA DEL MAPA")
   
    print(
        f"{'Metodo':<10}"
        f"{'Ruta':<50}"
        f"{'Km':>8}"
        f"{'Nodos':>10}"
        f"{'Tiempo':>15}"
    )
    

    for metodo, ruta, km, nodos, tiempo in resultados_mapa:
        print(
            f"{metodo:<10}"
            f"{ruta:<50}"
            f"{km:>8}"
            f"{nodos:>10}"
            f"{tiempo:>15.6f}"
        )

    print("\n8-PUZZLE")
    print("h1 inicio:", h1(inicio_puzzle))
    print("h2 inicio:", h2(inicio_puzzle))

    resultados_puzzle = []

    for tipo in ["UCS", "Voraz", "A*h1", "A*h2"]:
        inicio = time.perf_counter()

        movimientos, nodos = resolver_puzzle(tipo)

        tiempo = time.perf_counter() - inicio

        print("\n" + tipo)
        print("Movimientos:", movimientos)
        print("Nodos expandidos:", nodos)
        print(f"Tiempo: {tiempo:.6f} s")

        resultados_puzzle.append(
            (
                tipo,
                movimientos,
                nodos,
                tiempo
            )
        )

    print("\nTABLA COMPARATIVA DEL 8-PUZZLE")
    
    print(
        f"{'Metodo':<12}"
        f"{'Movimientos':>15}"
        f"{'Nodos':>12}"
        f"{'Tiempo':>15}"
    )
    

    for metodo, movimientos, nodos, tiempo in resultados_puzzle:
        print(
            f"{metodo:<12}"
            f"{movimientos:>15}"
            f"{nodos:>12}"
            f"{tiempo:>15.6f}"
        )

if __name__ == "__main__":
    main()