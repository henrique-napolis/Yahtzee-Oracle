import time
import numpy as np

from pontuacao import pontuar, njit, N_CATEGORIAS, BONUS_LIMIAR, BONUS_VALOR
from dice import construir_tabelas

from pathlib import Path

ARQUIVO_V = Path(__file__).resolve().parent / "V.npy"

N_UPPER = 64
MASK_CHEIA = (1 << N_CATEGORIAS) - 1
N_ESTADOS = (1 << N_CATEGORIAS) * N_UPPER
NEG = -1e18


def tabela_pontos(maos):
    """pontos[m, c] = pontuação da mão m na categoria c."""
    pontos = np.zeros((len(maos), N_CATEGORIAS), dtype=np.int64)
    for m in range(len(maos)):
        for c in range(N_CATEGORIAS):
            pontos[m, c] = pontuar(maos[m], c)
    return pontos


def para_esparsa(transicao):
    """Converte a matriz densa guarda x mão para CSR."""
    ptr = [0]
    col, val = [], []
    for g in range(transicao.shape[0]):
        for m in np.nonzero(transicao[g])[0]:
            col.append(m)
            val.append(transicao[g, m])
        ptr.append(len(col))
    return (np.array(ptr, dtype=np.int64),
            np.array(col, dtype=np.int64),
            np.array(val, dtype=np.float64))


def tabela_alcancavel():
    """alc[upper_mask, u]: dá pra ter soma superior u com essas categorias marcadas?"""
    alc = np.zeros((64, N_UPPER), dtype=np.bool_)
    for upper_mask in range(64):
        somas = {0}
        for f in range(6):
            if upper_mask >> f & 1:
                somas = {min(s + (f + 1) * k, BONUS_LIMIAR)
                         for s in somas for k in range(6)}
        for s in somas:
            alc[upper_mask, s] = True
    return alc

@njit(cache=True)
def valores_finais(mask, upper, V, pontos):
    """E3[m]: melhor valor ao terminar o turno com a mão m (escolhendo a categoria)."""
    n_maos = pontos.shape[0]
    E = np.full(n_maos, NEG)
    for m in range(n_maos):
        for c in range(N_CATEGORIAS):
            if mask >> c & 1:
                continue                       # categoria já usada
            ganho = pontos[m, c]
            novo_upper = upper
            if c < 6:
                novo_upper = min(upper + pontos[m, c], BONUS_LIMIAR)
                if upper < BONUS_LIMIAR and novo_upper >= BONUS_LIMIAR:
                    ganho += BONUS_VALOR       # cruzou o 63 agora
            v = ganho + V[(mask | (1 << c)) * N_UPPER + novo_upper]
            if v > E[m]:
                E[m] = v
    return E


@njit(cache=True)
def recuar_rolagem(E, ptr, col, val, guardas_de, n_guardas_de):
    """Dado o valor de cada mão DEPOIS de uma rolagem, devolve:
       K[g]: valor esperado de segurar g e rolar o resto
       E_antes[m]: valor da mão m ANTES dessa rolagem (escolhendo a melhor guarda)"""
    n_guardas = ptr.shape[0] - 1
    K = np.zeros(n_guardas)
    for g in range(n_guardas):
        s = 0.0
        for j in range(ptr[g], ptr[g + 1]):
            s += val[j] * E[col[j]]
        K[g] = s

    n_maos = E.shape[0]
    E_antes = np.empty(n_maos)
    for m in range(n_maos):
        melhor = NEG
        for i in range(n_guardas_de[m]):
            k = K[guardas_de[m, i]]
            if k > melhor:
                melhor = k
        E_antes[m] = melhor
    return K, E_antes


@njit(cache=True)
def valor_estado(mask, upper, V, pontos, ptr, col, val,
                 guardas_de, n_guardas_de, prob_inicial):
    E3 = valores_finais(mask, upper, V, pontos)
    _, E2 = recuar_rolagem(E3, ptr, col, val, guardas_de, n_guardas_de)
    _, E1 = recuar_rolagem(E2, ptr, col, val, guardas_de, n_guardas_de)
    return np.dot(prob_inicial, E1)


@njit(cache=True)
def resolver(V, pontos, ptr, col, val, guardas_de, n_guardas_de,
             prob_inicial, alc):
    for mask in range(MASK_CHEIA - 1, -1, -1):  # MASK_CHEIA fica em 0
        upper_mask = mask & 63
        for u in range(N_UPPER):
            if alc[upper_mask, u]:
                V[mask * N_UPPER + u] = valor_estado(
                    mask, u, V, pontos, ptr, col, val,
                    guardas_de, n_guardas_de, prob_inicial)


def main():
    (maos, guardas, idx_mao, idx_guarda, transicao,
     guardas_de, n_guardas_de, prob_inicial) = construir_tabelas()
    pontos = tabela_pontos(maos)
    ptr, col, val = para_esparsa(transicao)
    alc = tabela_alcancavel()

    V = np.zeros(N_ESTADOS)
    t0 = time.perf_counter()
    resolver(V, pontos, ptr, col, val, guardas_de, n_guardas_de,
             prob_inicial, alc)
    print(f"Resolvido em {time.perf_counter() - t0:.1f}s")
    print(f"Valor esperado do jogo: {V[0]:.4f}")
    np.save(ARQUIVO_V, V)


if __name__ == "__main__":
    main()
