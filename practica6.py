import math
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

INICIO = (3, 3, 1)
META = (0, 0, 0)
MOVIMIENTOS = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

def valido(m, c):
    if not 0 <= m <= 3 or not 0 <= c <= 3:
        return False

    if m > 0 and c > m:
        return False

    md, cd = 3 - m, 3 - c

    return md == 0 or cd <= md

def sucesores_mc(estado):
    m, c, bote = estado

    for dm, dc in MOVIMIENTOS:
        if bote:
            nuevo = (m - dm, c - dc, 0)
        else:
            nuevo = (m + dm, c + dc, 1)

        if valido(nuevo[0], nuevo[1]):
            yield nuevo

def resolver_mc():
    cola = deque([(INICIO, [INICIO])])
    visitados = {INICIO}

    while cola:
        estado, camino = cola.popleft()

        if estado == META:
            return camino

        for nuevo in sucesores_mc(estado):
            if nuevo not in visitados:
                visitados.add(nuevo)
                cola.append((nuevo, camino + [nuevo]))

    return []

def dibujar_mc(camino):
    G = nx.Graph()

    estados = [
        (m, c, b)
        for m in range(4)
        for c in range(4)
        for b in (0, 1)
        if valido(m, c)
    ]

    for estado in estados:
        for nuevo in sucesores_mc(estado):
            G.add_edge(estado, nuevo)

    camino_aristas = (
        set(zip(camino, camino[1:]))
        | set(zip(camino[1:], camino))
    )

    colores = [
        "red" if (a, b) in camino_aristas else "lightgray"
        for a, b in G.edges()
    ]

    pos = nx.spring_layout(G, seed=7)

    plt.figure(figsize=(10, 7))

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color=colores,
        node_size=1300,
        font_size=7
    )

    plt.title("Espacio de estados - Misioneros y Canibales")
    plt.savefig("espacio_estados_mc.png", dpi=150, bbox_inches="tight")
    plt.show()

def ganador(tablero, jugador):
    lineas = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]

    return any(
        all(tablero[i] == jugador for i in linea)
        for linea in lineas
    )

def terminal(tablero):
    return (
        ganador(tablero, "X")
        or ganador(tablero, "O")
        or " " not in tablero
    )

def utilidad(tablero):
    if ganador(tablero, "X"):
        return 1

    if ganador(tablero, "O"):
        return -1

    return 0

def sucesores(tablero, jugador):
    for i in range(9):
        if tablero[i] == " ":
            nuevo = tablero[:]
            nuevo[i] = jugador
            yield i, nuevo

nodos = 0

def minimax_simple(tablero, maximo):
    global nodos
    nodos += 1

    if terminal(tablero):
        return utilidad(tablero)

    if maximo:
        return max(
            minimax_simple(hijo, False)
            for _, hijo in sucesores(tablero, "X")
        )

    return min(
        minimax_simple(hijo, True)
        for _, hijo in sucesores(tablero, "O")
    )

def minimax(tablero, alfa, beta, maximo):
    global nodos
    nodos += 1

    if terminal(tablero):
        return utilidad(tablero)

    if maximo:
        valor = -math.inf

        for _, hijo in sucesores(tablero, "X"):
            valor = max(
                valor,
                minimax(hijo, alfa, beta, False)
            )

            alfa = max(alfa, valor)

            if alfa >= beta:
                break

        return valor

    valor = math.inf

    for _, hijo in sucesores(tablero, "O"):
        valor = min(
            valor,
            minimax(hijo, alfa, beta, True)
        )

        beta = min(beta, valor)

        if alfa >= beta:
            break

    return valor

def mejor_movimiento(tablero):
    global nodos
    nodos = 0

    mejor = -math.inf
    posicion = -1

    for i, hijo in sucesores(tablero, "X"):
        valor = minimax(
            hijo,
            -math.inf,
            math.inf,
            False
        )

        if valor > mejor:
            mejor = valor
            posicion = i

    return posicion

def comparar():
    global nodos

    tablero = [" "] * 9

    nodos = 0
    valor1 = minimax_simple(tablero, True)
    n1 = nodos

    nodos = 0
    valor2 = minimax(
        tablero,
        -math.inf,
        math.inf,
        True
    )
    n2 = nodos

    reduccion = 100 * (1 - n2 / n1)

    print("\nCOMPARACION MINIMAX")
    print(f"{'Algoritmo':<25}{'Valor':>10}{'Nodos':>15}")
    print(f"{'Minimax':<25}{valor1:>10}{n1:>15}")
    print(f"{'Minimax alfa-beta':<25}{valor2:>10}{n2:>15}")
    print(f"\nReduccion: {reduccion:.2f}%")

def invencible():
    partidas = 0
    derrotas = 0

    def recorrer(tablero):
        nonlocal partidas, derrotas

        if terminal(tablero):
            partidas += 1

            if ganador(tablero, "O"):
                derrotas += 1

            return

        if tablero.count("X") == tablero.count("O"):
            for _, hijo in sucesores(tablero, "O"):
                recorrer(hijo)

        else:
            pos = mejor_movimiento(tablero)
            tablero[pos] = "X"
            recorrer(tablero)
            tablero[pos] = " "

    recorrer([" "] * 9)

    print("\nVERIFICACION")
    print("Partidas posibles:", partidas)
    print("Partidas ganadas por persona:", derrotas)

    if derrotas == 0:
        print("La computadora nunca pierde")

def imprimir_tablero(tablero):
    for i in range(0, 9, 3):
        print(
            f" {tablero[i]} | "
            f"{tablero[i + 1]} | "
            f"{tablero[i + 2]}"
        )

        if i < 6:
            print("---+---+---")

def jugar():
    tablero = [" "] * 9

    while not terminal(tablero):
        imprimir_tablero(tablero)

        try:
            pos = int(input("\nElige una casilla (0-8): "))
        except ValueError:
            continue

        if pos not in range(9) or tablero[pos] != " ":
            continue

        tablero[pos] = "O"

        if terminal(tablero):
            break

        pc = mejor_movimiento(tablero)
        tablero[pc] = "X"

        print("\nLa PC jugo en:", pc)

    print()
    imprimir_tablero(tablero)

    if ganador(tablero, "X"):
        print("\nGana la computadora")

    elif ganador(tablero, "O"):
        print("\nGanaste")

    else:
        print("\nEmpate")

def main():
    camino = resolver_mc()

    print("MISIONEROS Y CANIBALES")
    print("Cruces:", len(camino) - 1)

    for i, (m, c, bote) in enumerate(camino):
        lado = "Izquierda" if bote else "Derecha"

        print(
            f"{i}: {m} Misioneros, "
            f"{c} Canibales, "
            f"Bote {lado}"
        )

    dibujar_mc(camino)

    comparar()
    invencible()

    respuesta = input(
        "\nQuieres jugar contra la computadora? (s/n): "
    )

    if respuesta.lower() == "s":
        jugar()

if __name__ == "__main__":
    main()