from __future__ import annotations

import enum
import hashlib
import json
from dynaconf.utils import object_merge
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union, Optional


class RepositoryState(enum.StrEnum):
    detached = enum.auto()
    dirty = enum.auto()


class TreeType(enum.StrEnum):
    dict = enum.auto()
    list = enum.auto()


class ObjectDumpPreset(enum.StrEnum):
    inline = enum.auto()
    expanded = enum.auto()


INLINE = ObjectDumpPreset.inline
EXPANDED = ObjectDumpPreset.expanded


class SAMPLES:
    listy = {"a": 1, "b": 2, "c": [1, 2]}
    listy_merge_unique = {
        "a": 1,
        "b": {"c": 2, "d": 3},
        "c": [2, 3, 4, "dynaconf_merge_unique"],
    }


def main() -> int:
    gt = Repository()
    sha1 = gt.commit(SAMPLES.listy)
    gt.print_objects()

    sha2 = gt.commit(SAMPLES.listy_merge_unique)
    gt.print_objects(EXPANDED)

    print("CHECKOUT")
    settings = gt.work_tree
    print(settings)

    gt.checkout(sha1)
    print(settings)

    gt.checkout(sha2)
    print(settings)

    sha3 = gt.merge_commits(sha2, sha1)
    gt.checkout(sha3)
    print(settings)
    gt.print_objects(EXPANDED)

    return 0


def iter_tree(container):
    if isinstance(container, list):
        return enumerate(container)
    else:
        return container.items()


def hash_object(obj: Any):
    """Generate a SHA-like identifier for an object."""
    return hashlib.sha1(repr(obj).encode()).hexdigest()


class ObjectType(enum.StrEnum):
    commit = enum.auto()
    tree = enum.auto()
    blob = enum.auto()


TreeObjectType = Union[ObjectType.tree, ObjectType.blob]
BlobType = Union[int, str, float, bool, None]


class Repository:
    def __init__(self):
        # hope we don't git some data that gives the hash of 000...
        self.SENTINEL_COMMIT = "0" * 40
        self.work_tree = {}
        self.head: str = "ref: heads/main"
        self.refs = {"heads/main": self.SENTINEL_COMMIT}
        self.objects: dict[str, Union[Commit, Tree, Blob]] = {
            self.SENTINEL_COMMIT: Tree(objects=tuple(), type=TreeType.dict)
        }
        self.checkout_cache = {}

    # Porcelain
    # =========

    def commit(self, data: dict, previous=None):
        """Convert a Python dictionary into git-like objects and store them."""
        previous = previous if previous else self.resolve_refs(self.head)

        # Create tree from data
        tree_hash = self.create_tree(data)

        # Create a commit object
        commit_metadata = (("loader", "library"), ("message", "Some message"))
        commit = Commit(tree_sha=tree_hash, metadata=commit_metadata, previous=previous)
        commit_sha = self.save_obj(commit)
        self.update_refs(self.dereference_head(), commit_sha)
        return commit_sha

    def checkout(self, refs: str, optimization=None):
        commit_sha = self.resolve_refs(refs)
        commit_obj = self.get_object(commit_sha)
        resolved = commit_obj.resolve(self.get_object)
        self.checkout_cache[commit_sha] = resolved
        remove = self.work_tree.keys() - resolved.keys()
        for k in remove:
            del self.work_tree[k]
        for k, v in resolved.items():
            self.work_tree[k] = v
        self.update_refs(self.dereference_head(), commit_sha)

    def show(self, sha):
        print(self.get_object(sha))

    # Plumbing
    # ========

    @property
    def detached_state(self):
        return not self.head.startswith("ref:")

    def dereference_head(self):
        if self.detached_state:
            raise RuntimeError()
        ref = self.head.split("ref:")[-1].strip()
        return ref

    def update_refs(self, ref: str, commit_sha: str):
        if commit_sha.startswith("ref:"):
            raise RuntimeError("Must not be a refs ptr")
        self.refs[ref] = commit_sha

    def merge_commits(self, base_ref: str, other_ref: str):
        base_commit = self.get_object(base_ref)
        other_commit = self.get_object(other_ref)
        base_data = base_commit.resolve(self.get_object)
        other_data = other_commit.resolve(self.get_object)
        object_merge(other_data, base_data)
        return self.commit(base_data, previous=base_ref)

    def save_obj(self, obj):
        if not obj:
            raise RuntimeError("Object can't be empty")
        sha = hash_object(obj)
        self.objects[sha] = obj
        return sha

    def get_object(self, refs: str):
        sha = self.resolve_refs(refs)
        if not sha or sha not in self.objects:
            raise KeyError(f"Object not found: {sha}")
        return self.objects[sha]

    def expand_sha(self, sha: str):
        if not sha:
            return None
        is_partial = len(sha) < 40
        if not is_partial and len(sha) == 40:
            return sha
        # TODO: can use binary search if objects sha's are sorted
        # Maybe making the 4e/3c7... nested list can make it very efficient
        # The nice thing is that it works for both full and partial shas
        _sha = [o for o in self.objects if o.startswith(sha)]
        return _sha[0] if _sha else None

    def resolve_refs(self, refs: str) -> str:
        # try to resolve: HEAD -> refs
        is_refs_ptr = refs.startswith("ref:")
        if is_refs_ptr:
            ref = refs.split("ref:")[-1].strip()
        else:
            ref = refs
        # try to resolve: refs -> sha
        sha = self.refs.get(ref, ref)
        # try to resolve what we got left
        return self.expand_sha(sha)

    def cache_object_checkout(self, sha: str, data: Any):
        self.checkout_cache[sha] = data

    def create_tree(self, data: dict):
        def _create_tree_from_dict(data: dict | list) -> Tree:
            """Recursively create a tree structure from a dictionary or list."""
            if not data:
                raise ValueError("Non empty data must be provided")
            tree_objects = []
            tree_type = TreeType.list if isinstance(data, list) else TreeType.dict
            for key, value in iter_tree(data):
                name = key
                if isinstance(value, dict):
                    subtree = _create_tree_from_dict(value)
                    tree_sha = self.save_obj(subtree)
                    tree_objects.append(
                        TreeRecord(type=ObjectType.tree, name=name, obj_sha=tree_sha)
                    )
                elif isinstance(value, list):
                    subtree = _create_tree_from_dict(value)
                    tree_sha = self.save_obj(subtree)
                    tree_objects.append(
                        TreeRecord(type=ObjectType.tree, name=name, obj_sha=tree_sha)
                    )
                else:
                    blob = Blob(value=value)
                    blob_sha = self.save_obj(blob)
                    tree_objects.append(
                        TreeRecord(type=ObjectType.blob, name=name, obj_sha=blob_sha)
                    )
            tree = Tree(objects=tuple(tree_objects), type=tree_type)
            return tree

        tree = _create_tree_from_dict(data)
        tree_hash = self.save_obj(tree)
        return tree_hash

    def print_objects(self, preset: ObjectDumpPreset = INLINE):
        for sha, obj in self.objects.items():
            obj_type = obj.__class__.__name__.lower()
            print(f"{sha} {obj_type[:4]} {obj.dump(preset)}")
        print()


def _inline_dump(kv_pairs: list[tuple[str, Any]]):
    prepared = ["=".join((k, repr(v))) for k, v in kv_pairs]
    prepared = " ".join(prepared)
    return f"inline {prepared}"


@dataclass(frozen=True, order=True)
class Commit:
    tree_sha: Tree
    metadata: tuple[tuple[str, str], ...]
    previous: str = ""

    def resolve(self, get_obj):
        tree = get_obj(self.tree_sha)
        return tree.resolve(get_obj)

    def dump(self, preset: ObjectDumpPreset = INLINE):
        extra = []
        if preset == INLINE:
            metadata = (("previous", self.previous[:7]),) + self.metadata
            display = _inline_dump(metadata)
        elif preset == EXPANDED:
            extra.append("extended")
            s = " " * 4
            extra.append(f"{s}tree={self.tree_sha[:7]}")
            extra.append(f"{s}previous={self.previous[:7]}")
            for k, v in self.metadata:
                extra.append(f"{s}{k}={v}")
            display = "\n".join(extra)
        else:
            raise RuntimeError("Shouldnt happen")
        return display


@dataclass(frozen=True)
class Tree:
    objects: tuple[TreeRecord, ...]
    type: TreeType

    def resolve(self, get_obj):
        objects = [(rec.name, get_obj(rec.obj_sha)) for rec in self.objects]
        if self.type == TreeType.dict:
            data = {k: v.resolve(get_obj) for k, v in objects}
        else:
            data = [v.resolve(get_obj) for _, v in objects]
        return data

    def dump(self, preset: ObjectDumpPreset = INLINE):
        extra = []
        kv_pairs = None
        if preset == INLINE:
            kv_pairs = [("type", self.type.name), ("count", str(len(self.objects)))]
            display = _inline_dump(kv_pairs)
        if preset == EXPANDED:
            extra.append("extended")
            s = " " * 4
            extra.append(f"{s}type={self.type}")
            for record in self.objects:
                extra.append(f"{s}{record.obj_sha[:7]} {record.type[:4]} {record.name}")
            display = "\n".join(extra)
        return display


@dataclass(frozen=True)
class TreeRecord:
    type: TreeObjectType
    name: str
    obj_sha: str


@dataclass(frozen=True)
class Blob:
    value: BlobType

    def resolve(self, get_obj):
        return self.value

    def dump(self, preset: ObjectDumpPreset = INLINE):
        if preset == INLINE:
            kv_pairs = [("type", type(self.value)), ("content", self.value)]
            display = _inline_dump(kv_pairs)
        if preset == EXPANDED:
            display = f"expanded {type(self.value)} {self.value}"
        return display


if __name__ == "__main__":
    exit(main())
