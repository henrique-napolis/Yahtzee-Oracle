# Yahtzee Solver

Projeto de estudo. Resolve Yahtzee de forma ótima (maximizando a pontuação esperada) e usa o resultado como um conselheiro via terminal: você joga, digita os dados, e ele diz o que segurar e onde marcar.


## O que é

O jogo é modelado como um Processo de Decisão de Markov (MDP) finito:

- **Estado entre turnos:** categorias já usadas (bitmask de 13 bits) + soma da seção superior truncada em 63. São 8192 × 64 = 524.288 estados.
- **Dentro do turno:** mãos representadas por contagem por face, o que reduz 7776 rolagens ordenadas para 252 mãos e 462 guardas possíveis.
- **Solução:** programação dinâmica de trás pra frente. Marcar uma categoria liga um bit, então percorrer `mask` em ordem decrescente garante que todo estado futuro já foi calculado.

O bônus superior (35 pontos ao atingir 63) é tratado como recompensa imediata no momento em que a soma cruza 63.

Valor esperado do jogo ótimo: **245,87** pontos.

### Regras simuladas

- Regras padrão de Yahtzee, 13 categorias, 3 rolagens por turno.
- Sem bônus de Yahtzee múltiplo e sem regra de joker.
- Cinco dados iguais não contam como Full house.

## Estrutura

| Arquivo | Função |
|---|---|
| `pontuacao.py` | Categorias e regra de pontuação de uma mão |
| `dice.py` | Enumera mãos e guardas, calcula probabilidades de transição |
| `solver.py` | Resolve o MDP e salva a tabela de valores em `V.npy` |
| `cli.py` | Conselheiro interativo no terminal |

## Como rodar

Requisitos: Python 3 e NumPy. Numba é opcional (sem ele o código roda, só bem mais devagar).

```
pip install numpy numba
```

Gere a tabela de valores (uma vez só, ~10s com Numba):

```
python solver.py
```

Depois, jogue com o conselheiro:

```
python cli.py
```

### Usando o CLI

- Digite os 5 dados da mesa em qualquer ordem: `13346`, `1 3 3 4 6` ou `6,3,1,4,3`.
- Nas rolagens 2 e 3, digite todos os 5 dados (os segurados + os que acabaram de cair).
- Na escolha da categoria, Ente* aceita a sugestão, ou digite o começo do nome (`full`, `chance`, `six`...) para escolher outra.

O CLI mostra também as alternativas e o valor esperado de cada uma, então dá pra ver quando uma decisão importa muito e quando tanto faz.