# VCSettings - Versioned Controled Settings

A version controlled settings framework using git fundamental concepts and stuctures.

## Vision

* The **working tree** is a mutable and long living dictionary that is updated by the framework.
* **Branches** are used to separate user environments (dev, prod, ...) and internal data
  such as raw data from loaders.
* Running a **loader** means getting the parsed data from it's source and commiting it to a unique branch.
* **Merge** is handled by explicitly creating merge commits from any two commit/branches. Let's not open the rebase box.
* **Merge conflicts** are resolved via composable merge resolvers functions or classes.
* **Validation** can be done transparently for any given commit
* **Dynamic values** and key/value **transformations** are handled outside the framework. Once evaluated they are commited as usual.

## Sample Usage

Setting up uv is left as an exercise to the reader.

This first example shows how the 'working tree' concept is used to store settings.
Then, 'checkout' is used for updating that working tree using a 'tree' from a 'commit'.
Finally, commits are merged using dynaconf's `object_merge`.

```python
> uv run python
Python 3.12.9 (main, Mar 17 2025, 21:01:58) [Clang 20.1.0 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from vcsettings.main import *
>>> repo = Repository()
>>> settings = repo.work_tree
>>> settings
{}
>>> sha1=repo.commit(SAMPLES.listy
>>> sha2=repo.commit(SAMPLES.listy_merge_unique)
>>> settings
{}
>>> repo.checkout(sha1)
>>> settings
{'a': 1, 'b': 2, 'c': [1, 2]}
>>> repo.checkout(sha2)
>>> settings
{'a': 1, 'b': {'c': 2, 'd': 3}, 'c': [2, 3, 4, 'dynaconf_merge_unique']}
>>> merge_commit = repo.merge_commits(sha2, sha1)
>>> repo.checkout(merge_commit)
>>> settings
{'a': 1, 'b': {'c': 2, 'd': 3}, 'c': [1, 2, 3, 4]}
```

Here it's the underlying graph storage of commit, tree and blobs.
This is similar to how objects are stored in `.git/objects`, but its all in-memory.

```python
>>> repo.print_objects(EXPANDED)
efd2377fc06a3e71982c4509688042b050604a8b blob expanded <class 'int'> 1
feee4791e1142dfecf70432b456cbbc3399aa2db blob expanded <class 'int'> 2
8e2bcbc69932e6eb8504a9e6e2265afc8e81142e tree extended
    type=list
    efd2377 blob 0
    feee479 blob 1
566b5c9da6b32ac2caeb642da015e06765008db7 tree extended
    type=dict
    efd2377 blob a
    feee479 blob b
    8e2bcbc tree c
8120973c02fb47feb7df85853e7f663fd91d557d comm extended
    tree=566b5c9
    previous=0000000
    loader=library
    message=Some message
5c2604ebffb607e78d0a0b8c7e3d351a4482e004 blob expanded <class 'int'> 3
8575c664795f0d7ba492eb38e9c9adf1fdcb01fb tree extended
    type=dict
    feee479 blob c
    5c2604e blob d
399e80341b1cb4b2bd53eedcf64b41d9849f4ddf blob expanded <class 'int'> 4
b6882400d23a192532232705d361c5eb1b995888 blob expanded <class 'str'> dynaconf_merge_unique
5ea577d67c7e7601d8282452e1b498ce64f7daac tree extended
    type=list
    feee479 blob 0
    5c2604e blob 1
    399e803 blob 2
    b688240 blob 3
6d16188af74c4600727ad7f4057d0572758711ee tree extended
    type=dict
    efd2377 blob a
    8575c66 tree b
    5ea577d tree c
486f118871bc24749fb96e039b5a2a2f74aa0266 comm extended
    tree=6d16188
    previous=0000000
    loader=library
    message=Some message
228e851e1336e14b863e3b6b571e831aad894911 tree extended
    type=list
    efd2377 blob 0
    feee479 blob 1
    5c2604e blob 2
    399e803 blob 3
eac9679972637a6409b08c3d6f38bd739ef6d0d2 tree extended
    type=dict
    efd2377 blob a
    8575c66 tree b
    228e851 tree c
49aee6a6e70a203b3cfab88ff4b3c54cfead76d5 comm extended
    tree=eac9679
    previous=486f118
    loader=library
    message=Some message
```
