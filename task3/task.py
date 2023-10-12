import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Callable, Optional


@dataclass
class Relation:
    direct_management: int
    direct_subordination: int
    indirect_management: int
    indirect_subordination: int
    subordination: int

    def to_row(self) -> list[int]:
        return [
            self.direct_management,
            self.direct_subordination,
            self.indirect_management,
            self.indirect_subordination,
            self.subordination,
        ]


class Node:
    def __init__(self, value: str, childred: dict[str, "Node"] | None = None, parent: Optional["Node"] = None) -> None:
        if childred is None:
            childred = {}
        self.childred: dict[str, "Node"] = childred
        self.value = value
        self.parent = parent

        self.relation = Relation(
            direct_subordination=0,
            direct_management=0,
            indirect_management=0,
            indirect_subordination=0,
            subordination=0,
        )
        self.n = 0

    def append(self, value: str) -> "Node":
        node = self.__class__(value, parent=self)
        self.childred[value] = node
        return node

    def set_n(self) -> None:
        self.n = 0

        def add_n(node: "Node") -> None:
            self.n += 1

        def set_n(node: "Node") -> None:
            node.n = self.n

        self.dfs(add_n)
        self.dfs(set_n)

    def __getitem__(self, value: str) -> "Node":
        return self.childred[value]

    def jsonable(self) -> dict[str, Any]:
        return {self.value: {"relation": asdict(self.relation), "childer": self._walk()}}

    def _walk(self) -> dict[str, Any]:
        if len(self.childred) == 0:
            return {}

        path: dict[str, Any] = {}
        for key, child in self.childred.items():
            path[key] = {"relation": asdict(child.relation), "childer": child._walk()}

        return path

    def dfs(self, func: Callable[["Node"], None]) -> None:
        func(self)

        if len(self.childred) == 0:
            return None

        for child in self.childred.values():
            child.dfs(func)

    def __str__(self) -> str:
        return json.dumps(self.jsonable(), indent=4)

    def find(self, value: str) -> "Node":
        if self.value == value:
            return self

        for child in self.childred.values():
            if child.value == value:
                return child
            try:
                child_find = child.find(value)
            except KeyError:
                ...
            else:
                return child_find

        raise KeyError(f"Child with value: {value} not found")

    def append_from_dict(self, value: str, dict_: dict[str, Any], parent: Optional["Node"] = None) -> "Node":
        node = Node(value=value, parent=parent)
        for key, child_dict in dict_.items():
            node.childred[key] = node.append_from_dict(value=key, dict_=child_dict, parent=node)

        return node

    @classmethod
    def read(cls, filename: str) -> "Node":
        with open(filename, "r") as f:
            dict_ = json.load(f)
        root_key = list(dict_.keys())[0]
        root = Node(root_key)
        for key, child_dict in dict_[root_key].items():
            root.childred[key] = root.append_from_dict(value=key, dict_=child_dict, parent=root)
        return root

    def pprint(self) -> str:
        str_ = self.value
        for child in self.childred.values():
            str_ += f" {child.value}"
        if self.parent is not None:
            str_ += f" {self.parent.value}"
        str_ += "\n"

        for child in self.childred.values():
            str_ += child.pprint()

        return str_

    def _set_inderect(self, node: "Node") -> None:
        self.relation.indirect_management += 1
        node.relation.indirect_subordination += 1

    def set_relations(self) -> None:
        for child in self.childred.values():
            self.relation.direct_management += 1
            child.relation.direct_subordination += 1
            child.relation.subordination = len(self.childred.values()) - 1

            for grandchild in child.childred.values():
                grandchild.dfs(self._set_inderect)
            child.set_relations()

    @classmethod
    def from_str(cls, input_: str) -> "Node":
        rows = [row.split(",") for row in input_.splitlines()]
        root = cls(rows[0][0])
        for row in rows:
            root.find(row[0]).append(row[1])

        root.set_relations()
        root.set_n()

        return root

    def self_entropy(self) -> float:
        entropy = 0.0
        for l_i_j in self.relation.to_row():
            p = l_i_j / (self.n - 1)
            if p <= 0:
                continue

            log_ = math.log(p, 2)
            entropy += p * log_

        return -entropy

    def full_entropy(self) -> float:
        entropy = 0.0

        def add_entrypy(node: "Node") -> None:
            nonlocal entropy
            entropy += node.self_entropy()

        self.dfs(add_entrypy)

        return entropy

    def to_csv(self) -> str:
        nodes: list[Node] = []
        self.dfs(lambda node: nodes.append(node))
        str_ = ""
        for node in sorted(nodes, key=lambda node: node.value):
            str_ += f"{node.relation.direct_management},{node.relation.direct_subordination},{node.relation.indirect_management},{node.relation.indirect_subordination},{node.relation.subordination}\n"

        return str_.strip()


def matrix_from_csv(input_: str) -> list[list[int]]:
    matrix: list[list[int]] = []
    for row in input_.splitlines():
        matrix_row: list[int] = []
        for col in row.split(","):
            matrix_row.append(int(col))
        matrix.append(matrix_row)

    return matrix


def full_entrypy_from_csv(input_: str) -> float:
    matrix = matrix_from_csv(input_)
    n = len(matrix)

    full_entrypy = 0.0
    for row in matrix:
        entropy = 0.0
        for rel in row:
            p = rel / (n - 1)
            if p <= 0:
                continue

            log_ = math.log(p, 2)
            entropy += p * log_

        full_entrypy += -entropy

    return full_entrypy


def example() -> None:
    root = Node("1")
    root.append("2")
    root.find("2").append("3")
    root.find("2").append("4")
    root.find("4").append("5")
    root.find("4").append("6")
    root.find("5").append("7")
    root.find("5").append("8")

    print(root)
    print(root.pprint())


# TODO revork to from_csv
def task(input_: str) -> float:
    return full_entrypy_from_csv(input_)


if __name__ == "__main__":
    # print(task("1,0,4,0,0\n2,1,2,0,0\n2,1,0,1,1\n0,1,0,1,1\n0,1,0,2,1\n0,1,0,2,1"))
    print(
        task(
            "0,1,3,0,0,0,1\n0,0,1,0,0,1,0\n0,0,2,0,0,1,0\n1,0,0,0,1,0,0\n0,0,1,0,0,1,0\n0,1,0,0,0,0,1\n1,0,0,0,1,0,0\n0,1,1,1,0,0,1\n0,0,1,0,0,0,1\n1,0,0,0,1,0,0\n0,0,1,0,0,1,0"
        )
    )
