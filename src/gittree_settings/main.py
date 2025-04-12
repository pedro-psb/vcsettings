from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union, Optional

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
                objects.append(TreeRecord(
                    type=ObjectType.tree,
                    name=name,
                    obj_sha=tree_sha
                ))
            else:
                # Create a blob for primitive values
                blob = Blob(value=value)
                blob_sha = hash_object(f"blob:{value}")
                
                self.objects[blob_sha] = blob
                objects.append(TreeRecord(
                    type=ObjectType.blob,
                    name=name,
                    obj_sha=blob_sha
                ))
                
        return Tree(objects=tuple(objects)) if objects else None
    
    def print_objects(self):
        print("== PRINT-OBJECTS ==")
        INDENT=" " * 4
        for sha, obj in self.objects.items():
            display = ""
            extra = []
            if isinstance(obj, Commit):
                obj_type = "commit"
                extra.append(f"tree={obj.tree_sha[:7]}")
                for k,v in obj.metadata:
                    extra.append(f"{k}={v}")
            elif isinstance(obj, Tree):
                obj_type = "tree"
                for record in obj.objects:
                    extra.append(f"{record.obj_sha[:7]} {record.type[:4]} {record.name}")
            elif isinstance(obj, Blob):
                obj_type = "blob"
                display = obj
            else:
                obj_type = "unknown"
            print(f"{sha} {obj_type[:4]} {display}")
            for line in extra:
                print(f"{INDENT}{line}")
        print()

class ObjectType(enum.StrEnum):
    commit = enum.auto()
    tree = enum.auto()
    blob = enum.auto()

TreeType = Union[ObjectType.tree, ObjectType.blob]
BlobType = Union[int, str, float, bool, None]

@dataclass(frozen=True, order=True)
class Commit:
    tree_sha: Tree
    metadata: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Tree:
    objects: tuple[TreeRecord, ...]


@dataclass(frozen=True)
class TreeRecord:
    type: TreeType
    name: str
    obj_sha: str


@dataclass(frozen=True)
class Blob:
    value: BlobType
    
    def __str__(self) -> str:
        return f"{type(self.value)} {self.value}"


if __name__ == "__main__":
    exit(main())
