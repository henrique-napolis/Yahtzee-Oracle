import numpy as np

try:
    from numba import njit
except ImportError:            # roda sem Numba, só mais devagar
    def njit(*args, **kwargs):
        def wrap(f):
            return f
        return wrap if not args or not callable(args[0]) else args[0]

# Índices das categorias
ONES, TWOS, THREES, FOURS, FIVES, SIXES = 0, 1, 2, 3, 4, 5
THREE_KIND, FOUR_KIND, FULL_HOUSE = 6, 7, 8
SMALL_STRAIGHT, LARGE_STRAIGHT, CHANCE, YAHTZEE = 9, 10, 11, 12
N_CATEGORIAS = 13

NOMES = ["Ones", "Twos", "Threes", "Fours", "Fives", "Sixes",
         "Three of a kind", "Four of a kind", "Full house",
         "Small straight", "Large straight", "Chance", "Yahtzee"]

BONUS_LIMIAR = 63
BONUS_VALOR = 35


@njit(cache=True)
def maior_sequencia(counts):
    """Tamanho da maior sequência de faces consecutivas presentes."""
    melhor = 0
    atual = 0
    for f in range(6):
        if counts[f] > 0:
            atual += 1
            if atual > melhor:
                melhor = atual
        else:
            atual = 0
    return melhor


@njit(cache=True)
def pontuar(counts, cat):
    """Pontos ao marcar a mão `counts` (array de 6 contagens) na categoria `cat`."""
    if cat < 6:
        return counts[cat] * (cat + 1)

    soma = 0
    max_c = 0
    tem_3 = False
    tem_2 = False
    for f in range(6):
        c = counts[f]
        soma += c * (f + 1)
        if c > max_c:
            max_c = c
        if c == 3:
            tem_3 = True
        elif c == 2:
            tem_2 = True

    if cat == THREE_KIND:
        return soma if max_c >= 3 else 0
    if cat == FOUR_KIND:
        return soma if max_c >= 4 else 0
    if cat == FULL_HOUSE:
        return 25 if (tem_3 and tem_2) else 0
    if cat == SMALL_STRAIGHT:
        return 30 if maior_sequencia(counts) >= 4 else 0
    if cat == LARGE_STRAIGHT:
        return 40 if maior_sequencia(counts) == 5 else 0
    if cat == CHANCE:
        return soma
    if cat == YAHTZEE:
        return 50 if max_c == 5 else 0
    return 0
    