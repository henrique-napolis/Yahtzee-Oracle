import numpy as np
from math import factorial


def multiconjuntos(n_dados):
    """Todas as contagens (arrays de 6) cuja soma é n_dados."""
    resultado = []

    def construir(face, restantes, atual):
        if face == 5:                      # última face recebe o que sobrou
            resultado.append(tuple(atual + [restantes]))
            return
        for c in range(restantes + 1):     # quantos dados nesta face
            construir(face + 1, restantes - c, atual + [c])

    construir(0, n_dados, [])
    return resultado


def prob_rolagem(counts):
    """Probabilidade de rolar exatamente essa contagem com sum(counts) dados."""
    k = sum(counts)
    formas = factorial(k)
    for c in counts:
        formas //= factorial(c)
    return formas / 6 ** k


def construir_tabelas():
    """Constrói tabelas de transição e guarda para todas as mãos possíveis."""
    maos = multiconjuntos(5)
    guardas = [g for n in range(6) for g in multiconjuntos(n)]

    idx_mao = {m: i for i, m in enumerate(maos)}
    idx_guarda = {g: i for i, g in enumerate(guardas)}

    # transicao[g, m] = P(terminar na mão m | guardei g e rolei o resto)
    transicao = np.zeros((len(guardas), len(maos)))
    for gi, g in enumerate(guardas):
        k = 5 - sum(g)                         # dados que voltam pra mesa
        for r in multiconjuntos(k):
            mao = tuple(a + b for a, b in zip(g, r))
            transicao[gi, idx_mao[mao]] += prob_rolagem(r)

    # guardas_de[m] = índices das guardas possíveis a partir da mão m
    MAX_SUB = 32
    guardas_de = np.full((len(maos), MAX_SUB), -1, dtype=np.int64)
    n_guardas_de = np.zeros(len(maos), dtype=np.int64)
    for mi, m in enumerate(maos):
        for gi, g in enumerate(guardas):
            if all(g[f] <= m[f] for f in range(6)):
                guardas_de[mi, n_guardas_de[mi]] = gi
                n_guardas_de[mi] += 1

    maos_arr = np.array(maos, dtype=np.int64)
    guardas_arr = np.array(guardas, dtype=np.int64)
    prob_inicial = np.array([prob_rolagem(m) for m in maos])

    return (maos_arr, guardas_arr, idx_mao, idx_guarda,
            transicao, guardas_de, n_guardas_de, prob_inicial)