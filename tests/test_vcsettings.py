import pytest
import os
import multiprocessing
from gittree_settings.main import (
    Repository,
    SAMPLE1,
    Commit,
    Tree,
    TreeRecord,
    Blob,
    ObjectType,
    hash_object,
)


def test_imutability(): ...


def test_object_hashing():
    """Test that Repository initializes correctly."""
    b0 = Blob("value")
    b1 = Blob("value")
    t0 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    t1 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    c0 = Commit("t0", (("a", "a"),))
    c1 = Commit("t0", (("a", "a"),))
    print()
    for o in [b0, b1, t0, t1, c0, c1]:
        print(o)
    for o in [b0, b1, t0, t1, c0, c1]:
        print(str(o))
    assert hash_object(b0) == hash_object(b1)
    assert hash_object(t0) == hash_object(t1)
    assert hash_object(c0) == hash_object(c1)


# @pytest.mark.parametrize()
def test_create_tree_deterministic():
    data0 = {"a": "a"}
    settings = Repository()
    t0 = settings._create_tree_from_dict(data0)
    t1 = settings._create_tree_from_dict(data0)
    assert t0 == t1
    assert hash_object(t0) == hash_object(t1)


def test_commit_and_show():
    """Test that we can commit data and show it."""
    settings = Repository()
    assert settings.head is None

    settings.commit(SAMPLE1)
    assert settings.head is not None

    # Show the committed data
    data = settings.show(settings.head)
    assert data == SAMPLE1


def hash_in_process(obj):
    def _hash_in_process(obj, conn):
        result = hash_object(obj)
        conn.send(result)
        conn.close()

    parent_conn, child_conn = multiprocessing.Pipe()
    process = multiprocessing.Process(target=_hash_in_process, args=(obj, child_conn))
    process.start()
    hash2 = parent_conn.recv()
    parent_conn.close()
    process.join()
    return hash2, process


def test_object_hashing_multiprocess():
    """Test that object hashing is consistent across different processes."""
    # TODO: this doesnt work, need to make it fail first with bad hashing then make it green

    # Create pairs of identical objects
    b0 = Blob("value")
    b1 = Blob("value")
    t0 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    t1 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    c0 = Commit("t0", (("a", "a"),))
    c1 = Commit("t0", (("a", "a"),))

    # Create pairs of objects to test
    object_pairs = [(b0, b1), (t0, t1), (c0, c1)]

    # Function to hash an object and return the result
    for obj1, obj2 in object_pairs:
        hash1 = hash_object(obj1)
        hash2, process = hash_in_process(obj2)
        assert (
            process.exitcode == 0
        ), f"Child process failed with exit code {process.exitcode}"
        assert hash1 == hash2, f"Hashes don't match for {obj1} and {obj2}"

        # Print for debugging (uncomment if needed)
        # print(f"\nObject type: {type(obj1).__name__}")
        # print(f"Parent process (obj1): {os.getpid()}, Hash: {hash1}")
        # print(f"Child process (obj2): {process.pid}, Hash: {hash2}")
