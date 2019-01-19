# To fix py.test import issues
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

def test_api():
    """
    A simple test to assert what the mathematicians have access to.
    """
    from rakan import BaseRakan

    assert hasattr(BaseRakan, "save")
    assert hasattr(BaseRakan, "read_nx")
    assert hasattr(BaseRakan, "step")
    assert hasattr(BaseRakan, "walk")