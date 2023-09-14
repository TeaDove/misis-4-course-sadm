import sys

import pandas as pd


def main() -> None:
    file = sys.argv[1]
    col = int(sys.argv[2])
    row = int(sys.argv[3])

    df = pd.read_csv(file, header=None)
    print(df.iloc[col][row])


if __name__ == "__main__":
    main()
