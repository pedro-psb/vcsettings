import pytest
from gittree_settings.main import GitTreeSettings, SAMPLE1

def test_gittree_settings_init():
    """Test that GitTreeSettings initializes correctly."""
    settings = GitTreeSettings()
    assert settings.head is None

def test_commit_and_show():
    """Test that we can commit data and show it."""
    settings = GitTreeSettings()
    settings.commit(SAMPLE1)
    assert settings.head is not None
    
    # Show the committed data
    data = settings.show(settings.head)
    assert data == SAMPLE1
