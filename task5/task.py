import numpy as np


def parse_clusters(input_: str) -> list[list[int]]:
    input_ = input_[1:-1]
    data_split = input_.split(",")
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


def get_matrix_from_expert(str_json: str) -> np.ndarray:
    matrix = []
    n = 0

    clusters = parse_clusters(str_json)
    for cluster in clusters:
        n += len(cluster)
    for _ in range(n):
        matrix.append([1] * n)

    worse = []
    for cluster in clusters:
        for worse_elem in worse:
            for elem in cluster:
                matrix[elem - 1][worse_elem - 1] = 0
        for elem in cluster:
            worse.append(int(elem))

    return np.array(matrix)


def compile_and_matrix(matrix1: np.ndarray, matrix2: np.ndarray) -> np.ndarray:
    rows = len(matrix1)
    cols = len(matrix1[0])
    matrix = []
    for _ in range(rows):
        matrix.append([0] * cols)

    for row in range(rows):
        for col in range(cols):
            matrix[row][col] = matrix1[row][col] * matrix2[row][col]

    return np.array(matrix)


def compile_or_matrix(matrix1: np.ndarray, matrix2: np.ndarray) -> list[list[int]]:
    rows = len(matrix1)
    cols = len(matrix1[0])
    matrix = []
    for _ in range(rows):
        matrix.append([0] * cols)

    for row in range(rows):
        for col in range(cols):
            matrix[row][col] = max(matrix1[row][col], matrix2[row][col])

    return matrix


def get_clusters(matrix: list[list[int]], est1: np.ndarray, est2: np.ndarray) -> list[int | list[int]]:  # noqa: C901
    clusters = {}

    rows = len(matrix)
    cols = len(matrix[0])
    exclude = []
    for row in range(rows):
        if row + 1 in exclude:
            continue
        clusters[row + 1] = [row + 1]
        for col in range(row + 1, cols):
            if matrix[row][col] == 0:
                clusters[row + 1].append(col + 1)
                exclude.append(col + 1)

    result = []
    for k in clusters:
        if not result:
            result.append(clusters[k])
            continue
        for i, elem in enumerate(result):
            if np.sum(est1[elem[0] - 1]) == np.sum(est1[k - 1]) and np.sum(est2[elem[0] - 1]) == np.sum(est2[k - 1]):
                for c in clusters[k]:
                    result[i].append(c)
                    break

            if np.sum(est1[elem[0] - 1]) < np.sum(est1[k - 1]) or np.sum(est2[elem[0] - 1]) < np.sum(est2[k - 1]):
                result = result[:i] + clusters[k] + result[i:]
                break
        result.append(clusters[k])

    final = []
    for r in result:
        if len(r) == 1:
            final.append(r[0])
        else:
            final.append(r)
    return final


def task(ranging1: str, ranging2: str) -> str:
    mx1 = get_matrix_from_expert(ranging1)
    print(f"{mx1}")
    mx2 = get_matrix_from_expert(ranging2)
    print(f"{mx2}")

    mx_and = compile_and_matrix(mx1, mx2)
    print(f"{mx_and}")
    mx_and_t = compile_and_matrix(np.transpose(mx1), np.transpose(mx2))
    print(f"{mx_and_t}")

    mx_or = compile_or_matrix(mx_and, mx_and_t)
    print(f"{mx_or}")
    clusters = get_clusters(mx_or, mx1, mx2)
    print(f"{clusters=}")
    return str(clusters)


if __name__ == "__main__":
    assert (  # noqa: S101
        task("[1,[2,3],4,[5,6,7],8,9,10]", "[[1,2],[3,4,5],6,7,9,[8,10]]") == "[1, 2, 3, 4, 5, 6, 7, [8, 9], 10]"
    )
    assert task("[2, 3, 1]", "[1, 2, 3]") == "[[1, 2, 3]]"  # noqa: S101
    assert task("[1, 2, 3]", "[1, 2, 3]") == "[1, 2, 3]"  # noqa: S101
