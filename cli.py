import numpy as np

from pontuacao import NOMES, N_CATEGORIAS, BONUS_LIMIAR, BONUS_VALOR
from dice import construir_tabelas
from solver import (valores_finais, recuar_rolagem, tabela_pontos, para_esparsa, N_UPPER)


def ler_mao(prompt):
    """Lê '13346' ou '1 3 3 4 6' e devolve a contagem por face."""
    while True:
        txt = input(prompt).replace(" ", "").replace(",", "")
        if len(txt) == 5 and all(ch in "123456" for ch in txt):
            counts = [0] * 6
            for ch in txt:
                counts[int(ch) - 1] += 1
            return tuple(counts)
        print("  Digite 5 dados de 1 a 6, ex: 13346")


def dados(counts):
    """Contagem por face de volta para lista legível: (1,0,2,...) -> '1 3 3'."""
    return " ".join(str(f + 1) for f in range(6) for _ in range(counts[f])) or "nada"


def avaliar_categorias(m, mask, upper, V, pontos):
    """Lista (valor_total, categoria, pontos_agora, novo_upper), melhor primeiro."""
    opcoes = []
    for c in range(N_CATEGORIAS):
        if mask >> c & 1:
            continue
        ganho = int(pontos[m, c])
        novo_upper = upper
        if c < 6:
            novo_upper = min(upper + ganho, BONUS_LIMIAR)
            if upper < BONUS_LIMIAR and novo_upper >= BONUS_LIMIAR:
                ganho += BONUS_VALOR
        valor = ganho + V[(mask | (1 << c)) * N_UPPER + novo_upper]
        opcoes.append((valor, c, ganho, novo_upper))
    opcoes.sort(reverse=True)
    return opcoes


def avaliar_guardas(m, K, guardas, guardas_de, n_guardas_de):
    """Lista (valor_esperado, guarda), melhor primeiro."""
    opcoes = [(K[g], g) for g in guardas_de[m, :n_guardas_de[m]]]
    opcoes.sort(reverse=True)
    return opcoes

def turno(mask, upper, V, t):
    (maos, guardas, idx_mao, _, pontos, ptr, col, val,
     guardas_de, n_guardas_de) = t

    E3 = valores_finais(mask, upper, V, pontos)
    K2, E2 = recuar_rolagem(E3, ptr, col, val, guardas_de, n_guardas_de)
    K1, _ = recuar_rolagem(E2, ptr, col, val, guardas_de, n_guardas_de)

    m = idx_mao[ler_mao("Rolagem 1: ")]
    for rolagem, K in ((1, K1), (2, K2)):
        opcoes = avaliar_guardas(m, K, guardas, guardas_de, n_guardas_de)
        valor, g = opcoes[0]
        guarda = tuple(guardas[g])
        if guarda == tuple(maos[m]):
            print(f"  -> Pare de rolar (valor esperado {valor:.2f})")
            break
        rolar = tuple(a - b for a, b in zip(maos[m], guarda))
        print(f"  -> Segure: {dados(guarda)} | Role: {dados(rolar)} "
              f"(valor esperado {valor:.2f})")
        for v, g2 in opcoes[1:3]:
            print(f"     alternativa: segurar {dados(tuple(guardas[g2]))} ({v:.2f})")
        m = idx_mao[ler_mao(f"Rolagem {rolagem + 1}: ")]

    opcoes = avaliar_categorias(m, mask, upper, V, pontos)
    for i, (v, c, ganho, _) in enumerate(opcoes[:4]):
        marca = "->" if i == 0 else "  "
        print(f"  {marca} {NOMES[c]:<16} +{ganho:<3} (valor esperado {v:.2f})")

    escolha = input("Categoria [Enter = sugerida]: ").strip().lower()
    for v, c, ganho, novo_upper in opcoes:
        if escolha and NOMES[c].lower().startswith(escolha):
            return c, ganho, novo_upper
    _, c, ganho, novo_upper = opcoes[0]
    return c, ganho, novo_upper


def main():
    V = np.load("V.npy")
    (maos, guardas, idx_mao, idx_guarda, transicao,
     guardas_de, n_guardas_de, prob_inicial) = construir_tabelas()
    pontos = tabela_pontos(maos)
    ptr, col, val = para_esparsa(transicao)
    t = (maos, guardas, idx_mao, idx_guarda, pontos, ptr, col, val,
         guardas_de, n_guardas_de)

    mask, upper, total = 0, 0, 0
    for n in range(N_CATEGORIAS):
        esperado = total + V[mask * N_UPPER + upper]
        print(f"\n=== Turno {n + 1} | Pontos: {total} | "
              f"Superior: {upper}/63 | Final esperado: {esperado:.1f} ===")
        c, ganho, upper = turno(mask, upper, V, t)
        mask |= 1 << c
        total += ganho
        print(f"  Marcado {NOMES[c]}: +{ganho}")
    print(f"\nFim de jogo: {total} pontos")


if __name__ == "__main__":
    main()