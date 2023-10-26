import math
from itertools import product
from typing import Any, Iterable

import numpy as np


def get_p_sum(dice_values: list[int]) -> dict[int, float]:
    count = len(dice_values) * len(dice_values)
    p: dict[int, float] = {}

    for x, y in product(dice_values, dice_values):
        sum_ = x + y

        if sum_ in p:
            p[sum_] += 1
        else:
            p[sum_] = 1

    for key, value in p.items():
        p[key] = value / count

    return p


def get_p_prod(dice_values: list[int]) -> dict[int, float]:
    count = len(dice_values) * len(dice_values)
    p: dict[int, float] = {}

    for x, y in product(dice_values, dice_values):
        prod_ = x * y

        if prod_ in p:
            p[prod_] += 1
        else:
            p[prod_] = 1

    for key, value in p.items():
        p[key] = value / count

    return p


def pprint(prods: Iterable[int], sums: Iterable[int], matrix: np.ndarray) -> None:
    try:
        from tabulate import tabulate
    except ImportError:
        print("pip install tabulate")
        return

    sums = sorted(sums)
    prods = sorted(prods)

    list_: list[list[Any]] = np.transpose(matrix).tolist()
    for idx, row in enumerate(list_):
        for jdx, v in enumerate(row):
            list_[idx][jdx] = round(v, 3)

    for idx, row in enumerate(list_):
        row.insert(0, sums[idx])

    list_.insert(0, [" ", *prods])
    print(tabulate(list_))


def get_count_matrix(  # noqa: CCR001
    dice_values: list[int], sums_to_n: dict[int, int], prods_to_n: dict[int, int]
) -> np.ndarray:
    matrix = np.ndarray((len(prods_to_n), len(sums_to_n)), dtype="int")

    prod_to_dices: dict[int, list[tuple[int, int]]] = {}  # noqa: TAE002
    dice_to_sums: dict[tuple[int, int], int] = {}
    for x, y in product(dice_values, dice_values):
        dices = (x, y)
        sum_ = x + y
        prod_ = x * y
        dice_to_sums[dices] = sum_

        if prod_ in prod_to_dices:
            prod_to_dices[prod_].append(dices)
        else:
            prod_to_dices[prod_] = [dices]

    matrix = np.zeros((len(prods_to_n), len(sums_to_n)))

    for prod_, dices in prod_to_dices.items():
        for dice in dices:
            if dice in dice_to_sums:
                matrix[prods_to_n[prod_]][sums_to_n[dice_to_sums[dice]]] += 1

    return matrix


def entropy_i(p: float) -> float:
    if p <= 0:
        return 0
    return p * math.log(p, 2)


def entropy(ps: dict[int, float]) -> dict[int, float]:
    entr: dict[int, float] = {}
    for key, p in ps.items():
        entr[key] = entropy_i(p)

    return entr


# H(A*B)
# H(A)
# H(B)
# Ha(B)
# I


def get_prob_matrix(count_matrix: np.ndarray) -> np.ndarray:
    count_matrix_tr = np.transpose(count_matrix)
    matrix = np.zeros(count_matrix_tr.shape)
    for i, row in enumerate(count_matrix_tr):
        sum_ = sum(row)
        for j, col in enumerate(row):
            matrix[i, j] = col / sum_

    return matrix


def get_sums_and_prods(dice_values: list[int]) -> tuple[set[int], set[int]]:
    prods_: set[int] = set()
    sums_: set[int] = set()

    for x, y in product(dice_values, dice_values):
        prods_.add(x * y)
        sums_.add(x + y)

    return sums_, prods_


def get_h_a_b(matrix: np.ndarray, p_i: list[float]) -> float:
    h = 0
    for idx, row in enumerate(matrix):
        entropy = 0
        for col in row:
            if col in {0, 1}:
                continue
            entropy += entropy_i(col)
        entropy *= p_i[idx]
        h += entropy
    return -h


def task() -> list[float]:
    dice_values = [1, 2, 3, 4, 5, 6]
    sums, prods = get_sums_and_prods(dice_values)
    prods_to_n: dict[int, int] = {key: i for i, key in enumerate(sorted(prods))}
    sums_to_n: dict[int, int] = {value: i for i, value in enumerate(sorted(sums))}

    # P(A)
    p_sum = get_p_sum(dice_values)
    # print(f"{p_sum=}\n")
    # H(Ai)
    h_sum_i = entropy(p_sum)
    # print(f"{h_sum_i=}\n")
    # H(A)
    h_sum = -sum((i for i in h_sum_i.values()))
    # print(f"{h_sum=}\n")
    # P(B)
    p_prod = get_p_prod(dice_values)
    # print(f"{p_prod=}\n")
    # H(B)
    h_prod = -sum((i for i in entropy(p_prod).values()))
    # print(f"{h_prod=}\n")

    count_matrix = get_count_matrix(dice_values, sums_to_n, prods_to_n)
    # print("count_matrix")
    # pprint(prods, sums, count_matrix)

    prob_matrix = get_prob_matrix(count_matrix)
    # print("prob_matrix")
    # pprint(prods, sums, np.transpose(prob_matrix))

    h_a_b = get_h_a_b(prob_matrix, [p_sum[key] for key in sorted(p_sum.keys())])

    return [h_sum + h_a_b, h_sum, h_prod, h_a_b, h_prod - h_a_b]


if __name__ == "__main__":
    print(task())
