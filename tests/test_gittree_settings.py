import pytest
from gittree_settings.main import GitTreeSettings, SAMPLE1, Commit, Tree, TreeRecord, Blob, ObjectType, hash_object

def test_imutability():
    ...
    

def test_object_hashing():
    """Test that GitTreeSettings initializes correctly."""
    b0 = Blob("value")
    b1 = Blob("value")
    t0 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    t1 = Tree((TreeRecord(ObjectType.blob, "foo", "b0"),))
    c0 = Commit("t0", (("a","a"),))
    c1 = Commit("t0", (("a","a"),))
    print()
    for o in [b0,b1,t0,t1,c0,c1]:
        print(o)
    for o in [b0,b1,t0,t1,c0,c1]:
        print(str(o))
    assert hash_object(b0) == hash_object(b1)
    assert hash_object(t0) == hash_object(t1)
    assert hash_object(c0) == hash_object(c1)

# @pytest.mark.parametrize()
def test_create_tree_deterministic():
    data0={"a": "a"}
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
