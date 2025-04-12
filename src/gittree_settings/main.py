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
    gt.show("e2df98dbff9b42f4f6cede687daea3e7c77da46d")
    return 0

class GitTreeSettings:
    def __init__(self):
        self.head: Optional[str] = None
        self.objects: dict[str, Union[Commit, Tree, Blob]] = {}

    def commit(self, data: dict):
        """Convert a Python dictionary into git-like objects and store them."""
        # Create tree from data
        tree_hash = self._create_tree_from_dict(data)
        
        # Create a commit object
        commit_metadata = (("author", "gittree"), ("message", "Commit data"))
        commit = Commit(tree_sha=tree_hash, metadata=commit_metadata)
        
        # Generate SHA for commit
        commit_sha = self._generate_sha(f"commit:{commit}")
        
        # Store the commit object
        self.objects[commit_sha] = commit
        self.head = commit_sha
        
        return commit_sha

    def show(self, sha):
        print(self.objects[sha])
    
    def _create_tree_from_dict(self, data: dict, prefix: str = "") -> Tree:
        """Recursively create a tree structure from a dictionary."""
        # TODO: fix this
        objects = []
        
        for key, value in data.items():
            name = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                # Create a subtree for nested dictionaries
                subtree = self._create_tree_from_dict(value, f"{name}.")
                tree_sha = self._generate_sha(f"tree:{subtree}")
                
                self.objects[tree_sha] = subtree
                objects.append(TreeRecord(
                    type=ObjectType.tree,
                    name=name,
                    obj_sha=tree_sha
                ))
            else:
                # Create a blob for primitive values
                blob = Blob(value=value)
                blob_sha = self._generate_sha(f"blob:{value}")
                
                self.objects[blob_sha] = blob
                objects.append(TreeRecord(
                    type=ObjectType.blob,
                    name=name,
                    obj_sha=blob_sha
                ))
                
        tree = Tree(objects=tuple(objects)) if objects else None
        tree_hash = self._generate_sha(tree)
        self.objects[tree_hash] = tree
        return tree_hash
    
    def _generate_sha(self, content: Any) -> str:
        """Generate a SHA-like identifier for an object."""
        content_str = str(content)
        return hashlib.sha1(content_str.encode()).hexdigest()

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

@dataclass(frozen=True)
class Commit:
    tree_sha: Tree
    metadata: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Tree:
    objects: tuple[TreeRecord, ...]
    
    def __str__(self) -> str:
        return f"Tree({len(self.objects)} objects)"


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
