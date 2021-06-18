import logging
import sys
sys.path.append("..")

import pytest
from base.session import SRequest
from urllib.parse import urlparse

from base.suit import Suit


class Step:
    def init_resource(self, request_url: str, method: str, data: dict, headers: str, desire_result: dict, pre: dict):
        self.session = SRequest()
        self.method = str(method).upper()
        self.request_url = request_url
        self.headers = headers
        self.data = data
        self.desire_result = desire_result
        self.pre = pre
        self.result = dict()

    def assert_result(self, current, desire):
        for k,v in desire:
            assert current[k] == desire.get(k)
    
    def get_url_path(self) -> str:
        parsed = urlparse(self.request_url)
        return parsed.path

    def setPre(self):
        if self.pre:
            if self.pre.get("addTo","empty") == "Headers":
                headers = self.pre.get("data",dict())
                for k,_ in headers.items:
                    self.headers[k] = headers[k]
                return
            data = self.pre.get("data",dict())
            for k,_ in data.items:
                self.data[k] = data[k]
            
        
    def runRequest(self):
        if self.pre is not None:
            self.setPre()
        print(f"self.session.{self.method}({self.request_url},{self.data},{self.desire_result['code']},{self.headers})")
        resp, exception = eval(f"self.session.{self.method}('{self.request_url}',{self.data},{self.desire_result['code']}, **{self.headers})")
        print(exception)
        if exception is not None:
            logging.error(f"{self.method} {self.request_url} error, {exception}")
            exit(1)
        self.result = resp


if __name__ == '__main__':
      pytest.main()
