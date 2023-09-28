import json
from dataclasses import asdict, dataclass
from typing import Any, Callable, Optional


@dataclass
class Relation:
    direct_management: int
    direct_subordination: int
    indirect_management: int
    indirect_subordination: int
    subordination: int


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

    def append(self, value: str) -> "Node":
        node = self.__class__(value, parent=self)
        self.childred[value] = node
        return node

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


def task(input_: str) -> str:
    rows = [row.split(",") for row in input_.splitlines()]
    root = Node(rows[0][0])
    for row in rows:
        root.find(row[0]).append(row[1])

    root.set_relations()

    nodes: list[Node] = []
    root.dfs(lambda node: nodes.append(node))
    str_ = ""
    for node in sorted(nodes, key=lambda node: node.value):
        str_ += f"{node.relation.direct_management},{node.relation.direct_subordination},{node.relation.indirect_management},{node.relation.indirect_subordination},{node.relation.subordination}\n"

    return str_.strip()


if __name__ == "__main__":
    print(task("1,2\n2,3\n2,4\n3,5\n3,6"))
