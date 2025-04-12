from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union, Optional

SAMPLE1 = {
    "a": 1,
    "b": 2,
}

SAMPLE2 = {
    "a": 1,
    "b": {"c": 2, "d": 3},
}


def main() -> int:
    gt = GitTreeSettings()
    gt.commit(SAMPLE1)
    gt.print_objects()
    gt.commit(SAMPLE2)
    gt.print_objects()
    return 0


def hash_object(obj: Any):
    """Generate a SHA-like identifier for an object."""
    return hashlib.sha1(repr(obj).encode()).hexdigest()


class GitTreeSettings:
    def __init__(self):
        self.head: Optional[str] = None
        self.objects: dict[str, Union[Commit, Tree, Blob]] = {}

    def commit(self, data: dict):
        """Convert a Python dictionary into git-like objects and store them."""
        # Create tree from data
        tree = self._create_tree_from_dict(data)
        tree_hash = hash_object(tree)
        self.objects[tree_hash] = tree

        # Create a commit object
        commit_metadata = (("author", "gittree"), ("message", "Commit data"))
        commit = Commit(tree_sha=tree_hash, metadata=commit_metadata)

        # Generate SHA for commit
        commit_sha = hash_object(commit)
        # commit_sha = str(hash(commit))

        # Store the commit object
        self.objects[commit_sha] = commit
        self.head = commit_sha

        return commit_sha

    def show(self, sha):
        _sha = sha
        if len(sha) < 40:
            _sha = [o for o in self.objects if o.startswith(sha)]
            _sha = _sha[0] if _sha else None

        if not _sha or _sha not in self.objects:
            raise KeyError(f"Object not found: {sha}")
        print(self.objects[_sha])

    def _create_tree_from_dict(self, data: dict, prefix: str = "") -> Tree:
        """Recursively create a tree structure from a dictionary."""
        objects = []

        for key, value in data.items():
            name = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                # Create a subtree for nested dictionaries
                subtree = self._create_tree_from_dict(value, f"{name}.")
                tree_sha = hash_object(f"tree:{subtree}")

                self.objects[tree_sha] = subtree
                objects.append(
                    TreeRecord(type=ObjectType.tree, name=name, obj_sha=tree_sha)
                )
            else:
                # Create a blob for primitive values
                blob = Blob(value=value)
                blob_sha = hash_object(f"blob:{value}")

                self.objects[blob_sha] = blob
                objects.append(
                    TreeRecord(type=ObjectType.blob, name=name, obj_sha=blob_sha)
                )

        return Tree(objects=tuple(objects)) if objects else None

    def print_objects(self):
        for sha, obj in self.objects.items():
            obj_type = obj.__class__.__name__.lower()
            print(f"{sha} {obj_type[:4]} {obj.dump()}")
        print()


class ObjectType(enum.StrEnum):
    commit = enum.auto()
    tree = enum.auto()
    blob = enum.auto()


class ObjectDumpPreset(enum.StrEnum):
    inline = enum.auto()
    expanded = enum.auto()


INLINE = ObjectDumpPreset.inline
EXPANDED = ObjectDumpPreset.expanded

TreeType = Union[ObjectType.tree, ObjectType.blob]
BlobType = Union[int, str, float, bool, None]


def _inline_dump(kv_pairs: list[tuple[str, Any]]):
    prepared = ["=".join((k, repr(v))) for k, v in kv_pairs]
    prepared = " ".join(prepared)
    return f"inline {prepared}"


@dataclass(frozen=True, order=True)
class Commit:
    tree_sha: Tree
    metadata: tuple[tuple[str, str], ...]
    previous: str = ""

    def dump(self, preset: ObjectDumpPreset = INLINE):
        extra = []
        if preset == INLINE:
            metadata = (("previous", self.previous[:7]),) + self.metadata
            display = _inline_dump(metadata)
        elif preset == EXPANDED:
            extra.append("extended")
            extra.append(f"tree={self.tree_sha[:7]}")
            for k, v in self.metadata:
                extra.append(f"{k}={v}")
            display = "\n".join(extra)
        else:
            raise RuntimeError("Shouldnt happen")
        return display


@dataclass(frozen=True)
class Tree:
    objects: tuple[TreeRecord, ...]

    def dump(self, preset: ObjectDumpPreset = INLINE):
        extra = []
        kv_pairs = None
        if preset == INLINE:
            kv_pairs = [("count", str(len(self.objects)))]
            display = _inline_dump(kv_pairs)
        if preset == EXPANDED:
            extra.append("extended")
            for record in self.objects:
                extra = []
                extra.append(f"{record.obj_sha[:7]} {record.type[:4]} {record.name}")
            display = "\n".join(extra)
        return display


@dataclass(frozen=True)
class TreeRecord:
    type: TreeType
    name: str
    obj_sha: str


@dataclass(frozen=True)
class Blob:
    value: BlobType

    def dump(self, preset: ObjectDumpPreset = INLINE):
        if preset == INLINE:
            kv_pairs = [("type", type(self.value)), ("content", self.value)]
            display = _inline_dump(kv_pairs)
        if preset == EXPANDED:
            display = f"expanded {type(self.value)} {self.value}"
        return display


if __name__ == "__main__":
    exit(main())
