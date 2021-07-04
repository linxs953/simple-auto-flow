import sys

sys.path.append(".")
from core.base.suit import Suit
from core.base.step import Step
import pytest
from main import *


class TestLogin(Suit):
    def setup_method(self, method):
        self.init_resource([])
        self.steps = [
            Step(*("getToken", "https://api.test.com/gettoken", "POST", {
                'username': '[username]',
                'password': '[password]'
            }, {
                'User-Agent': ''
            }, [{
                'field': 'code',
                'assert': 'eq',
                'desire': 200
            }], [], None, None, None)),
            Step(*("getTaskList", "https://api.test.com/search", "get", None, {
                'Content-Type': 'application/json; charset=utf-8'
            }, [{
                'field': 'code',
                'assert': 'eq',
                'desire': 200
            }, {
                'field': 'error',
                'assert': 'include',
                'desire': 'success'
            }], [{
                'name': 'getToken',
                'response': "$suit.result['getToken']",
                'addTo': {
                    'type': 'Headers',
                    'location': 'Authorization'
                },
                'refer': [{
                    'name': 'token',
                    'field': 'access_token'
                }]
            }], 5, None, None))
        ]

    def teardown_method(self, method):
        pass

    @pytest.mark.flaky(reruns=2)
    def test_Login(self):
        self.run()
