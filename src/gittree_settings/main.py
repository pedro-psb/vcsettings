from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

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
        """Convert a Python dictionary into git-like objects and store them."""
        # Create tree from data
        tree = self._create_tree_from_dict(data)
        
        # Create a commit object
        commit_metadata = (("author", "gittree"), ("message", "Commit data"))
        commit = Commit(tree=tree, metadata=commit_metadata)
        
        # Generate SHA for commit
        commit_sha = self._generate_sha(f"commit:{commit}")
        
        # Store the commit object
        commit_obj = Object(
            sha=commit_sha,
            type=ObjectType.commit,
            name="HEAD",
            content=commit
        )
        self.objects[commit_sha] = commit_obj
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
                
                tree_obj = Object(
                    sha=tree_sha,
                    type=ObjectType.tree,
                    name=name,
                    content=subtree
                )
                self.objects[tree_sha] = tree_obj
                objects.append(tree_obj)
            else:
                # Create a blob for primitive values
                blob = Blob(value=value)
                blob_sha = self._generate_sha(f"blob:{value}")
                
                blob_obj = Object(
                    sha=blob_sha,
                    type=ObjectType.blob,
                    name=name,
                    content=blob
                )
                self.objects[blob_sha] = blob_obj
                objects.append(blob_obj)
                
        return Tree(objects=objects)
    
    def _generate_sha(self, content: Any) -> str:
        """Generate a SHA-like identifier for an object."""
        content_str = str(content)
        return hashlib.sha1(content_str.encode()).hexdigest()

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
    metadata: tuple[tuple[str, str], ...]


@dataclass
class Tree:
    objects: list[Object]
    
    def __str__(self) -> str:
        return f"Tree({len(self.objects)} objects)"


@dataclass
class Object:
    sha: str
    type: ObjectType
    name: str
    content: Union[Tree, Blob]
    
    def __str__(self) -> str:
        return f"Object({self.name}, {self.type.name}, {self.sha[:7]})"

    
@dataclass
class Blob:
    value: BlobType
    
    def __str__(self) -> str:
        return f"Blob({self.value})"


if __name__ == "__main__":
    exit(main())
