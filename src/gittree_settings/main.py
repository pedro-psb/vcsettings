from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Union

SAMPLE1={
    "a": 1,
    "b": 2,
}

SAMPLE2={
    "a": 1,
    "b": {"c": 2, "d": 3},
}

def main() -> int:
    gt = GitTreeSettings()
    gt.commit(SAMPLE1)
    gt.print_objects()
    return 0

class GitTreeSettings:
    def __init__(self):
        self.head = None
        self.objects: dict[str, Object] = {}

    def commit(self, data: dict):
        ...

    def print_objects(self):
        for sha, value in self.objects.items():
            print(sha, value)

class ObjectType(enum.IntEnum):
    commit = enum.auto()
    tree = enum.auto()
    blob = enum.auto()

BlobType = Union[int, str, float, bool, None]

@dataclass
class Commit:
    tree: Tree
    metadata: tuple[tuple(str, str), ...]


@dataclass
class Tree:
    objects: list[Object]


@dataclass
class Object:
    sha: str
    type: ObjectType
    name: str

    
@dataclass
class Blob:
    value: BlobType


if __name__ == "__name__":
    exit(main())
