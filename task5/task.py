import json

import numpy as np

ranging = list[str | list[str]]


def flatten(v: ranging) -> list[str]:
    new_v: list[str] = []
    for item in v:
        if isinstance(item, str):
            new_v.append(item)
        else:
            new_v.extend(item)
    return sorted(new_v, key=lambda x: int(x))


def is_lower(v: ranging, a: str, b: str) -> bool:
    for item in v:
        if isinstance(item, str):
            if a == item:
                return True
            if b == item:
                return False
            continue

        if a in item:
            return b not in item
        if b in item:
            return a in item
        continue


def get_matrix(v: ranging) -> np.ndarray:
    flat_v = flatten(v)
    matrix = np.zeros(shape=(len(flat_v), len(flat_v)), dtype="int64")

    for i_x, i_v in enumerate(flat_v):
        for j_x, j_v in enumerate(flat_v):
            if i_v == j_v or not is_lower(v, i_v, j_v):
                matrix[i_x, j_x] = 1
                continue

    return matrix


def get_controversy_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    y_a_b = np.multiply(a, b)
    y_a_b_ = np.multiply(np.transpose(a), np.transpose(b))

    result = np.zeros(a.shape, dtype="int64")
    for idx in range(len(y_a_b)):
        for jdx in range(len(y_a_b[idx])):
            result[idx, jdx] = y_a_b[idx, jdx] or y_a_b_[idx, jdx]
    return result


def find_controversy_pairs(v: np.ndarray) -> list[tuple[str, str]]:
    res = []
    for idx, i in enumerate(v):
        for jdx, j in enumerate(i):
            if idx < jdx:
                continue
            if j == 0:
                res.append((str(jdx + 1), str(idx + 1)))

    return res


def expand_list(ranks: ranging) -> list[str]:
    expanded_ranks = []
    for element in ranks:
        if isinstance(element, list):
            expanded_ranks.extend(element)
        else:
            expanded_ranks.append(element)
    return sorted(expanded_ranks, key=lambda x: int(x))


def compile_ranging(controversy_pairs: list[tuple[str, str]], a: ranging, b: ranging) -> ranging:
    expanded_a = expand_list(a)
    expanded_b = expand_list(b)
    print(f"{expanded_a=}")
    print(f"{expanded_b=}")
    final_ranking = []

    added_items = set()

    for item in expanded_a + expanded_b:
        if item not in added_items:
            controversy_group = [item]
            for pair in controversy_pairs:
                if item in pair:
                    other_item = pair[0] if pair[1] == item else pair[1]
                    controversy_group.append(other_item)

            if len(controversy_group) > 1:
                final_ranking.append(controversy_group)
            else:
                final_ranking.append(item)

            added_items.update(controversy_group)

    return final_ranking
    # return ["1", "2", "3", "4", "5", "6", "7", ["8", "9"], "10"]


def task(a_: str, b_: str) -> ranging:
    a = get_matrix(json.loads(a_))
    b = get_matrix(json.loads(b_))
    controversy_matrix = get_controversy_matrix(a, b)

    controversy_pairs = find_controversy_pairs(controversy_matrix)
    print(f"{controversy_pairs=}")

    return compile_ranging(controversy_pairs, json.loads(a_), json.loads(b_))


if __name__ == "__main__":
    a = '["1", ["2", "3"], "4", ["5", "6", "7"], "8", "9", "10"]'
    b = '[["1", "2"], ["3", "4", "5"], "6", "7", "9", ["8", "10"]]'
    c = '["3", ["1", "4"], "2", "6", ["5", "7", "8"], ["9", "10"]]'

    assert ["1", "2", "3", "4", "5", "6", "7", ["8", "9"], "10"] == task(a, b)  # noqa: S101

    print(task(a, c))  # [["1", "3"], ["2", "4"], ]
    print(task(b, c))
