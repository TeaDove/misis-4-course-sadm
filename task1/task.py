import csv
import sys


def main() -> None:
    filename = sys.argv[1]
    col = int(sys.argv[2])
    row = int(sys.argv[3])

    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        print(list(reader)[col][row])


if __name__ == "__main__":
    main()
