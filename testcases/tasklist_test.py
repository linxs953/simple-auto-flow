import time
import sys
sys.path.append("..")
import pytest
from base.step import TestStep


class TestCommonService(TestStep):
    def setup_method(self, method):
        self.init_resource(
          request_url="https://zhidao.baidu.com/task/api/getmytasklist?popFlag=1&status=done&_=1623232353334",
          method="get",
          data=None,
          headers={"header":"xss"},
          desire_result={"code": 200}
        )
        print("init successfully")


    def teardown_method(self, method):
        time.sleep(1)
        print("teardown")

    # @pytest.mark.flaky(reruns=5)
    def test_common_service(self):
        self.runRequest()
        print(self.result)
        assert 10 == 10


if __name__ == '__main__':
    pytest.main(["-s","tasklist_test.py::test_xxx"])