"""Simple test to verify pytest is working"""


def test_simple():
    """Simple test"""
    assert True


class TestSimple:
    """Simple test class"""
    def __getstate__(self):
        """Ermöglicht Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Ermöglicht Pickle-Deserialisierung für Session State"""
        self.__dict__.update(state)
    

    def test_method(self):
        """Simple test method"""
        assert True
