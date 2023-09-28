import json
import sys
from typing import Any, Optional


class Node:
    def __init__(self, value: str, childred: dict[str, "Node"] | None = None, parent: Optional["Node"] = None) -> None:
        if childred is None:
            childred = {}
        self.childred: dict[str, "Node"] = childred
        self.value = value
        self.parent = parent

    def append(self, value: str) -> "Node":
        node = self.__class__(value, parent=self)
        self.childred[value] = node
        return node

    def __getitem__(self, value: str) -> "Node":
        return self.childred[value]

    def jsonable(self) -> dict[str, Any]:
        return {self.value: self._walk()}

    def _walk(self) -> dict[str, Any]:
        if len(self.childred) == 0:
            return {}

        path: dict[str, Any] = {}
        for key, child in self.childred.items():
            path[key] = child._walk()

        return path

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


def main() -> None:
    root = Node.read(sys.argv[1])

    # print(root)
    print(root.pprint())


if __name__ == "__main__":
    example()
