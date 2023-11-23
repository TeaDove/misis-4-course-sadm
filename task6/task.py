import json
import math


def row_mean_difference_squared(row: list[int], mean: float) -> float:
    return (sum(v for v in row) - mean) ** 2


def calculate_candlle_coefficient(rank_matrix: list[list[int]], num_of_ratings: int) -> float:
    mean = (num_of_ratings + 1) / (2 * num_of_ratings)
    print(f"{mean=}")

    sum_ = 0
    for rating in range(1, num_of_ratings + 1):
        sum_ += math.pow(num_of_ratings * rating - mean, 2)

    variance_max = sum_ / num_of_ratings - 1
    print(f"{variance_max=}")

    variance = 0
    for row in rank_matrix:
        variance += row_mean_difference_squared(row, mean)

    variance = variance / (num_of_ratings - 1)

    return variance / variance_max


def task(*args: str) -> float:
    args_parsed = [json.loads(arg) for arg in args]

    num_of_experts, num_of_ratings = len(args), len(args_parsed[0])

    available_keys = sorted((x for x in args_parsed[0]))
    print(f"{num_of_experts=}, {num_of_ratings=}, {available_keys=}")

    ranked_ratings = []
    for i in range(num_of_experts):
        row = []
        for j in range(num_of_ratings):
            row.append(args_parsed[i].index(available_keys[j]) + 1)
        ranked_ratings.append(row)

    print(f"{ranked_ratings=}")
    return calculate_candlle_coefficient(ranked_ratings, num_of_ratings)


if __name__ == "__main__":
    # print(
    #     task(
    #         "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
    #         "[1, 2,3,4,5,6,7,9,8, 10]",
    #         "[3,1,4,2,6,5,7,8,9,10]",
    #     )
    # )
    print(
        task(
            "[2, 3, 1]",
            "[1, 2, 3]",
            "[3, 1, 2]",
        )
    )
