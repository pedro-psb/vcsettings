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
    import os
    
    # Create pairs of identical objects
    b0 = Blob("value")
    b1 = Blob("value")
    t0 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    t1 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    c0 = Commit("t0", (("a", "a"),))
    c1 = Commit("t0", (("a", "a"),))

    # Create pairs of objects to test
    object_pairs = [(b0, b1), (t0, t1), (c0, c1)]
    
    main_pid = os.getpid()
    
    for obj1, obj2 in object_pairs:
        # Hash the first object in the current process
        hash1 = hash_object(obj1)
        
        # Create a pipe for communication between processes
        read_fd, write_fd = os.pipe()
        
        # Fork a child process to hash the second object
        pid = os.fork()
        
        if pid == 0:  # Child process
            try:
                # Close the read end in the child
                os.close(read_fd)
                
                # Hash the object and write the result to the pipe
                child_hash = hash_object(obj2)
                os.write(write_fd, child_hash.encode('utf-8'))
                
                # Exit the child process
                os._exit(0)
            except Exception as e:
                print(f"Child process error: {e}")
                os._exit(1)
        else:  # Parent process
            # Close the write end in the parent
            os.close(write_fd)
            
            # Read the hash from the child process
            hash2 = os.read(read_fd, 1024).decode('utf-8')
            os.close(read_fd)
            
            # Wait for the child to finish
            _, status = os.waitpid(pid, 0)
            assert status == 0, f"Child process failed with status {status}"
            
            # Verify that the hashes are the same
            assert hash1 == hash2, f"Hashes don't match for {obj1} and {obj2}"
            
            # Print for debugging (uncomment if needed)
            # print(f"\nObject type: {type(obj1).__name__}")
            # print(f"Parent process (obj1): {main_pid}, Hash: {hash1}")
            # print(f"Child process (obj2): {pid}, Hash: {hash2}")
