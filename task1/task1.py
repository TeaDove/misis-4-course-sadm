import json
import sys
from typing import Any, Optional


class Node:
    def __init__(self, value: str, childred: list["Node"] | None = None, parent: Optional["Node"] = None) -> None:
        if childred is None:
            childred = []
        self.childred: list["Node"] = []
        self.value = value
        self.parent = parent

    def append(self, value: str) -> "Node":
        node = self.__class__(value, parent=self)
        self.childred.append(node)
        return node

    def __getitem__(self, idx: int) -> "Node":
        return self.childred[idx]

    def jsonable(self) -> dict[str, Any]:
        return {self.value: self._walk()}

    def _walk(self) -> dict[str, Any]:
        if len(self.childred) == 0:
            return {}

        path: dict[str, Any] = {}
        for child in self.childred:
            path[child.value] = child._walk()

        return path

    def __str__(self) -> str:
        return json.dumps(self.jsonable(), indent=4)

    def find(self, value: str) -> "Node":
        if self.value == value:
            return self

        for child in self.childred:
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
            node.childred.append(node.append_from_dict(value=key, dict_=child_dict, parent=node))

        return node

    @classmethod
    def read(cls, filename: str) -> "Node":
        with open(filename, "r") as f:
            dict_ = json.load(f)
        root_key = list(dict_.keys())[0]
        root = Node(root_key)
        for key, child_dict in dict_[root_key].items():
            root.childred.append(root.append_from_dict(value=key, dict_=child_dict, parent=root))
        return root

    def pprint(self) -> str:
        str_ = self.value
        for child in self.childred:
            str_ += f" {child.value}"
        if self.parent is not None:
            str_ += f" {self.parent.value}"
        str_ += "\n"

        for child in self.childred:
            str_ += child.pprint()

        return str_

    # @classmethod
    # def from_dict(cls, value: str, childred: , parent: Optional["Node"] = None) -> "Node":
    #     node = Node(parent=parent, value=list(dict_.keys())[0])
    #     for child_value in dict_.values():
    #         node.append(Node.from_dict(child_value))

    #     # 4: {1, 2, 3, 4}

    #     return node

    #     reader = list(csv.reader(csvfile, delimiter=","))
    #     root = Node(reader[0][0])
    #     for col in reader[0][1:]:
    #         root.append(col)

    #     for line in reader[1:]:
    #         node = root.find(line[0])
    #         if node is None:
    #             node = root.append(line[0])

    #         for col in reader[0][1:]:
    #             if node.parent is not None and node.parent.value == col:
    #                 continue

    #             node.append(col)
    # return root


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
    main()
