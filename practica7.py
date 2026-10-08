import random
import math
import matplotlib.pyplot as plt

estados = [
    "CDMX", "Edomex", "Morelos", "Puebla", "Tlaxcala",
    "Hidalgo", "Queretaro", "Guerrero", "Michoacan"
]

fronteras = [
    ("CDMX", "Edomex"),
    ("CDMX", "Morelos"),
    ("Edomex", "Morelos"),
    ("Edomex", "Puebla"),
    ("Edomex", "Tlaxcala"),
    ("Edomex", "Hidalgo"),
    ("Edomex", "Queretaro"),
    ("Edomex", "Michoacan"),
    ("Edomex", "Guerrero"),
    ("Morelos", "Puebla"),
    ("Morelos", "Guerrero"),
    ("Puebla", "Tlaxcala"),
    ("Puebla", "Hidalgo"),
    ("Puebla", "Guerrero"),
    ("Tlaxcala", "Hidalgo"),
    ("Hidalgo", "Queretaro"),
    ("Queretaro", "Michoacan"),
    ("Michoacan", "Guerrero")
]

vecinos = {e: set() for e in estados}

for a, b in fronteras:
    vecinos[a].add(b)
    vecinos[b].add(a)


def backtracking(asignacion, dominios):
    if len(asignacion) == len(estados):
        return asignacion.copy()

    libres = [e for e in estados if e not in asignacion]

    estado = min(
        libres,
        key=lambda e: (
            len(dominios[e]),
            -sum(v not in asignacion for v in vecinos[e])
        )
    )

    valores = sorted(
        dominios[estado],
        key=lambda color: sum(
            color in dominios[v]
            for v in vecinos[estado]
            if v not in asignacion
        )
    )

    for color in valores:
        nuevos = {
            e: dominios[e][:]
            for e in estados
        }

        nuevos[estado] = [color]
        valido = True

        for v in vecinos[estado]:
            if v not in asignacion:
                nuevos[v] = [
                    c for c in nuevos[v]
                    if c != color
                ]

                if not nuevos[v]:
                    valido = False
                    break

        if valido:
            asignacion[estado] = color
            resultado = backtracking(asignacion, nuevos)

            if resultado:
                return resultado

            del asignacion[estado]

    return None


def resolver_csp(n):
    colores = list(range(1, n + 1))
    dominios = {e: colores[:] for e in estados}
    return backtracking({}, dominios)


N = 15
EVAL = 30000


def generar_ciudades():
    random.seed(42)

    return [
        (
            random.uniform(0, 100),
            random.uniform(0, 100)
        )
        for _ in range(N)
    ]


def distancia(a, b):
    return math.hypot(
        a[0] - b[0],
        a[1] - b[1]
    )


def costo(ruta, puntos):
    return sum(
        distancia(
            puntos[ruta[i]],
            puntos[ruta[(i + 1) % N]]
        )
        for i in range(N)
    )


def crear_poblacion(tam):
    poblacion = []

    for _ in range(tam):
        ruta = list(range(N))
        random.shuffle(ruta)
        poblacion.append(ruta)

    return poblacion


def torneo(poblacion, puntos):
    candidatos = random.sample(poblacion, 3)

    return min(
        candidatos,
        key=lambda r: costo(r, puntos)
    )


def ox(padre1, padre2):
    i, j = sorted(random.sample(range(N), 2))

    hijo = [-1] * N
    hijo[i:j + 1] = padre1[i:j + 1]

    faltan = [
        x for x in padre2[j + 1:] + padre2[:j + 1]
        if x not in hijo
    ]

    posiciones = (
        list(range(j + 1, N))
        + list(range(0, i))
    )

    for pos, valor in zip(posiciones, faltan):
        hijo[pos] = valor

    return hijo


def mutar(ruta, prob):
    if random.random() < prob:
        i, j = sorted(random.sample(range(N), 2))
        ruta[i:j + 1] = reversed(ruta[i:j + 1])


def genetico(puntos, tam, prob):
    poblacion = crear_poblacion(tam)

    mejor = min(
        poblacion,
        key=lambda r: costo(r, puntos)
    )[:]

    evaluaciones = tam
    historia = [
        (evaluaciones, costo(mejor, puntos))
    ]

    while evaluaciones < EVAL:
        poblacion.sort(
            key=lambda r: costo(r, puntos)
        )

        nueva = [poblacion[0][:]]

        while len(nueva) < tam and evaluaciones < EVAL:
            p1 = torneo(poblacion, puntos)
            p2 = torneo(poblacion, puntos)

            hijo = ox(p1, p2)
            mutar(hijo, prob)

            nueva.append(hijo)
            evaluaciones += 1

            if costo(hijo, puntos) < costo(mejor, puntos):
                mejor = hijo[:]

        poblacion = nueva

        historia.append(
            (
                evaluaciones,
                costo(mejor, puntos)
            )
        )

    return mejor, costo(mejor, puntos), historia


def aleatoria(puntos):
    mejor = None
    mejor_costo = float("inf")
    historia = []

    for _ in range(EVAL):
        ruta = list(range(N))
        random.shuffle(ruta)

        c = costo(ruta, puntos)

        if c < mejor_costo:
            mejor = ruta[:]
            mejor_costo = c

        historia.append(mejor_costo)

    return mejor, mejor_costo, historia


def graficas(ruta, puntos, historia, historia_aleatoria):
    plt.figure(figsize=(9, 5))

    plt.plot(
        [e for e, _ in historia],
        [c for _, c in historia],
        label="Genetico"
    )

    paso = max(1, len(historia_aleatoria) // 500)

    plt.plot(
        range(0, len(historia_aleatoria), paso),
        historia_aleatoria[::paso],
        label="Aleatoria"
    )

    plt.xlabel("Evaluaciones")
    plt.ylabel("Distancia")
    plt.title("Convergencia")
    plt.legend()
    plt.grid()

    plt.savefig(
        "convergencia.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.show()

    ruta_cerrada = ruta + [ruta[0]]

    x = [puntos[i][0] for i in ruta_cerrada]
    y = [puntos[i][1] for i in ruta_cerrada]

    plt.figure(figsize=(7, 7))
    plt.plot(x, y, "o-")

    for i, punto in enumerate(puntos):
        plt.text(
            punto[0],
            punto[1],
            str(i)
        )

    plt.title("Mejor ruta")
    plt.grid()

    plt.savefig(
        "mejor_ruta.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.show()


def main():
    print("CSP")
    

    solucion3 = resolver_csp(3)
    solucion4 = resolver_csp(4)

    print("3 colores:", solucion3)
    print("4 colores:", solucion4)

    if solucion3 is None:
        print(
            "Con 3 colores no hay solucion porque "
            "Edomex, Morelos, Puebla y Guerrero forman K4"
        )

    puntos = generar_ciudades()
    resultados = []

    print("\nALGORITMO GENETICO")
   

    for tam, prob in [
        (30, 0.1),
        (30, 0.3),
        (60, 0.1),
        (60, 0.3)
    ]:
        random.seed(42)

        ruta, c, historia = genetico(
            puntos,
            tam,
            prob
        )

        resultados.append(
            (
                c,
                ruta,
                historia,
                tam,
                prob
            )
        )

    print(
        f"{'Poblacion':<15}"
        f"{'Mutacion':<15}"
        f"{'Distancia':>15}"
    )


    for c, ruta, historia, tam, prob in resultados:
        print(
            f"{tam:<15}"
            f"{prob:<15}"
            f"{c:>15.2f}"
        )

    mejor = min(
        resultados,
        key=lambda x: x[0]
    )

    random.seed(42)

    ruta_aleatoria, costo_aleatorio, historia_aleatoria = aleatoria(
        puntos
    )

    print("\nCOMPARACION")
    print(f"{'Metodo':<20}{'Distancia':>15}")
    print(f"{'Genetico':<20}{mejor[0]:>15.2f}")
    print(f"{'Aleatoria':<20}{costo_aleatorio:>15.2f}")

    print("\nMejor poblacion:", mejor[3])
    print("Mejor mutacion:", mejor[4])

    graficas(
        mejor[1],
        puntos,
        mejor[2],
        historia_aleatoria
    )


if __name__ == "__main__":
    main()