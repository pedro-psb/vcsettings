import pytest
import multiprocessing
from gittree_settings.main import (
    GitTreeSettings,
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
    """Test that GitTreeSettings initializes correctly."""
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
    settings = GitTreeSettings()
    t0 = settings._create_tree_from_dict(data0)
    t1 = settings._create_tree_from_dict(data0)
    print()
    print(t0)
    print(repr(t0))
    print(hash_object(t0))
    assert t0 == t1
    assert hash_object(t0) == hash_object(t1)


def test_commit_and_show():
    """Test that we can commit data and show it."""
    settings = GitTreeSettings()
    assert settings.head is None

    settings.commit(SAMPLE1)
    assert settings.head is not None

    # Show the committed data
    data = settings.show(settings.head)
    assert data == SAMPLE1


def test_object_hashing_multiprocess():
    """Test that object hashing is consistent across different processes."""
    # Create pairs of identical objects
    b0 = Blob("value")
    b1 = Blob("value")
    t0 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    t1 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    c0 = Commit("t0", (("a", "a"),))
    c1 = Commit("t0", (("a", "a"),))

    # Create pairs of objects to test
    object_pairs = [(b0, b1), (t0, t1), (c0, c1)]
    
    # Function to return both hash and process ID
    def hash_with_pid(obj):
        import os
        return (hash_object(obj), os.getpid())
    
    # Use multiprocessing to hash each object in a separate process
    with multiprocessing.Pool(processes=2) as pool:
        for obj1, obj2 in object_pairs:
            # Hash each object in a separate process
            result1 = pool.apply(hash_with_pid, (obj1,))
            result2 = pool.apply(hash_with_pid, (obj2,))
            
            hash1, pid1 = result1
            hash2, pid2 = result2
            
            # Verify that the hashes are the same
            assert hash1 == hash2, f"Hashes don't match for {obj1} and {obj2}"
            
            # Verify that the objects were processed in different processes
            assert pid1 != pid2, f"Objects were processed in the same process: {pid1}"
            
            # Verify that neither process is the main process
            import os
            main_pid = os.getpid()
            assert pid1 != main_pid, f"Object 1 was processed in the main process"
            assert pid2 != main_pid, f"Object 2 was processed in the main process"

            # Print for debugging
            # print(f"\nObject type: {type(obj1).__name__}")
            # print(f"Object 1: {obj1}, Process: {pid1}")
            # print(f"Object 2: {obj2}, Process: {pid2}")
            # print(f"Hash 1: {hash1}")
            # print(f"Hash 2: {hash2}")
            # print(f"Main process: {main_pid}")
