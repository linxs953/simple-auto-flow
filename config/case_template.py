code = """
import sys
sys.path.append(".")
from base.suit import Suit
from base.step import Step
import pytest
class Test{}(Suit):
    def setup_method(self, method):
        self.init_resource([])
        self.steps = [
            {}
        ]
    
    def teardown_method(self, method):
        pass
    
    @pytest.mark.flaky(reruns={})
    def test_{}(self):
        self.run()
"""