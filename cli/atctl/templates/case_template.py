code = """
from core.base.suit import Suit
from core.base.step import Step
import pytest
from main import *
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

step = """(
    "{}",
    "{}",
    "{}",
    {},
    {},
    {},
    {},
    {},
    {},
    {}
    )
"""