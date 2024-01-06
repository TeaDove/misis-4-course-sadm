import numpy as np


def extract_clusters(data_string: str) -> list[list[int]]:
    data_string = data_string[1:-1]
    data_split = data_string.split(",")
    clusters = []
    in_cluster = False
    for substring in data_split:
        current_cluster = in_cluster
        if "[" in substring:
            substring = substring[1:]
            in_cluster = True
        if "]" in substring:
            substring = substring[:-1]
            in_cluster = False

        if not current_cluster:
            clusters.append([int(substring)])
        else:
            clusters[-1].append(int(substring))
    return clusters


def generate_matrix_from_expert(data_str: str) -> np.ndarray:
    matrix = []
    n = 0

    clusters = extract_clusters(data_str)
    print(f"{data_str=}")
    print(f"{clusters=}")
    for cluster in clusters:
        n += len(cluster)

    for _ in range(n):
        matrix.append([1] * n)

    exclusion_list = []
    for cluster in clusters:
        for excluded_elem in exclusion_list:
            for elem in cluster:
                matrix[elem - 1][excluded_elem - 1] = 0

        for elem in cluster:
            exclusion_list.append(int(elem))

    return np.array(matrix)


def calculate_kendall_similarity(experts: list[np.ndarray]) -> float:
    m = len(experts)
    n = len(experts[0])

    rank_matrix: list[list[int]] = [[0 for _ in range(len(experts))] for _ in range(len(experts[0]))]

    for i, expert in enumerate(experts):
        for j, obj in enumerate(expert):
            rank_matrix[j][i] = len(obj) - np.sum(obj) + 1

    H = 0
    for i in range(m):
        d: dict[int, int] = {}
        for obj in rank_matrix:
            if d.get(obj[i]) is None:
                d[obj[i]] = 0
            d[obj[i]] = d[obj[i]] + 1

        for k in d:
            H += d[k] ** 3 - d[k]

        for j, obj in enumerate(rank_matrix):
            rank_matrix[j][i] = rank_matrix[j][i] + (d[obj[i]] - 1) / 2

    x_mean = np.sum(rank_matrix) / n

    s = 0
    for obj_ranks in rank_matrix:
        xi = np.sum(obj_ranks)
        s += (xi - x_mean) ** 2

    d_max = (m * m * (n**3 - n) - m * H) / 12

    return s / d_max


def task(*rangins: str) -> float:
    print(f"{rangins=}")
    matrixes = [generate_matrix_from_expert(ranging) for ranging in rangins]
    similarity = calculate_kendall_similarity(matrixes)
    print(f"{similarity=}\n\n")
    return similarity


if __name__ == "__main__":
    assert task("[1,[2,3],4,[5,6,7],8,9,10]", "[[1,2],[3,4,5],6,7,9,[8,10]]") == 0.9623824451410659  # noqa: S101
    assert task("[2, 3, 1]", "[1, 2, 3]") == 0.25  # noqa: S101
    assert task("[1, 2, 3]", "[1, 2, 3]") == 1.0  # noqa: S101
    assert task("[1, 2, 3]", "[1, 2, 3]", "[1, 2, 3]") == 1.0  # noqa: S101
