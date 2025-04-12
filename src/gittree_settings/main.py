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

class GitTreeSettings:
    def __init__(self):
        self.head: Optional[str] = None
        self.objects: dict[str, Union[Commit, Tree, Blob]] = {}

    def commit(self, data: dict):
        """Convert a Python dictionary into git-like objects and store them."""
        # Create tree from data
        tree = self._create_tree_from_dict(data)
        
        # Create a commit object
        commit_metadata = (("author", "gittree"), ("message", "Commit data"))
        commit = Commit(tree=tree, metadata=commit_metadata)
        
        # Generate SHA for commit
        commit_sha = self._generate_sha(f"commit:{commit}")
        
        # Store the commit object
        self.objects[commit_sha] = commit
        self.head = commit_sha
        
        return commit_sha
    
    def _create_tree_from_dict(self, data: dict, prefix: str = "") -> Tree:
        """Recursively create a tree structure from a dictionary."""
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
                    sha=tree_sha
                ))
            else:
                # Create a blob for primitive values
                blob = Blob(value=value)
                blob_sha = self._generate_sha(f"blob:{value}")
                
                self.objects[blob_sha] = blob
                objects.append(TreeRecord(
                    type=ObjectType.blob,
                    name=name,
                    sha=blob_sha
                ))
                
        return Tree(objects=tuple(objects))
    
    def _generate_sha(self, content: Any) -> str:
        """Generate a SHA-like identifier for an object."""
        content_str = str(content)
        return hashlib.sha1(content_str.encode()).hexdigest()

    def print_objects(self):
        for sha, obj in self.objects.items():
            if isinstance(obj, Commit):
                obj_type = "commit"
            elif isinstance(obj, Tree):
                obj_type = "tree"
            elif isinstance(obj, Blob):
                obj_type = "blob"
            else:
                obj_type = "unknown"
            print(f"{sha} {obj_type[:4]} {obj}")

class ObjectType(enum.IntEnum):
    commit = enum.auto()
    tree = enum.auto()
    blob = enum.auto()

BlobType = Union[int, str, float, bool, None]

@dataclass(frozen=True)
class Commit:
    tree: Tree
    metadata: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Tree:
    objects: tuple[TreeRecord, ...]
    
    def __str__(self) -> str:
        return f"Tree({len(self.objects)} objects)"


@dataclass(frozen=True)
class TreeRecord:
    type: ObjectType
    name: str
    sha: str


@dataclass(frozen=True)
class Blob:
    value: BlobType
    
    def __str__(self) -> str:
        return f"{type(self.value)} {self.value}"


if __name__ == "__main__":
    exit(main())
