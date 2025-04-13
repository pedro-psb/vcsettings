# VCSettings - Versioned Controled Settings

A version controlled settings framework using git fundamental concepts and stuctures.

## Vision

* The working tree is a mutable and long living dictionary that is updated by the framework.
* Branches are used to separate user environments (dev, prod, ...) and internal data
  such as raw data from loaders.
* Running a loader means getting the parsed data from it's source and commiting it to a unique branch.
* Merge is handled by explicitly creating merge commits from any two commit/branches. Let's not open the rebase box.
* Merge conflicts are resolved via composable merge resolvers functions or classes.
* Validation can be done transparently for any given commit
* Dynamic values and key/value transformations are handled outside the framework. Once evaluated they are commited as usual.

## Sample Usage

Setting up uv is left as an exercise to the reader.

This first example shows how the 'working tree' concept is used to store settings.
Then, 'checkout' is used for updating that working tree using a 'tree' from a 'commit'.

```python
> uv run python
Python 3.12.9 (main, Mar 17 2025, 21:01:58) [Clang 20.1.0 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from vcsettings.main import *
>>> repo = Repository()
>>> settings = repo.work_tree
>>> settings
{}
>>> sha1=repo.commit(SAMPLES.nested)
>>> sha2=repo.commit(SAMPLES.simple)
>>> settings
{}
>>> repo.checkout(sha1)
>>> settings
{'a': 1, 'b': {'c': 2, 'd': 3}}
>>> repo.checkout(sha2)
>>> settings
{'a': 1, 'b': 2}
```

Here it's the underlying graph storage of commit, tree and blobs.
This is similar to how objects are stored in `.git/objects`, but its all in-memory.

```python
>>> repo.print_objects(EXPANDED)
efd2377fc06a3e71982c4509688042b050604a8b blob expanded <class 'int'> 1
feee4791e1142dfecf70432b456cbbc3399aa2db blob expanded <class 'int'> 2
5c2604ebffb607e78d0a0b8c7e3d351a4482e004 blob expanded <class 'int'> 3
b402c7e9709509de958212c89122596bcb656dc0 tree extended
    feee479 blob c
    5c2604e blob d
6af5c9498513efef1a44b911491935e2b825e1d4 tree extended
    efd2377 blob a
    b402c7e tree b
9d37dc5b45382e7597de103bdae3b9a552494361 comm extended
    tree=6af5c94
    loader=library
    message=Some message
4c078019fd58417a0204ebd2e4a310cc5784194c tree extended
    efd2377 blob a
    feee479 blob b
4b0ef1d0398fa791a2b19150383df6286cffd5c0 comm extended
    tree=4c07801
    loader=library
    message=Some message

```
