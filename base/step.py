import logging
from msilib.schema import Error
import sys
from time import sleep
import re
sys.path.append("..")

import pytest
from base.session import Request
from urllib.parse import urlparse
from utils.step import *
from base.suit import Suit


class Step:
    def init_resource(self, stepname: str,  request_url: str, method: str, data: dict, 
                      headers: str, desire_result: dict, pre: list, 
                      setupFunc: function, endFunc: function=None):
        self.session = Request()
        self.name = stepname
        self.method = str(method).upper()
        self.request_url = request_url
        self.headers = headers
        self.data = data
        self.desire_result = desire_result
        self.pre = pre
        self.setup = setupFunc
        self.end = endFunc
        self.result = dict()

    def assert_result(self, current, desire):
        for k,_ in desire:
            # todo: assert error
            assert current[k] == desire.get(k)
    
    def get_url_path(self) -> str:
        parsed = urlparse(self.request_url)
        return parsed.path

    def setPre(self, parent: Suit):
        for _,preStep in self.pre:
            if preStep:
                if preStep.get("addTo","empty") == "Headers":
                    # 处理type是Headers
                    headers = preStep.get("data",dict())
                    for k,_ in headers.items:
                        self.headers[k] = headers[k]
                elif preStep.get("addTo","empty") == "Data":
                    # 处理type是Data
                    data = preStep.get("data",dict())
                    for k,_ in data.items:
                        self.data[k] = data[k]
                else:
                    # 处理type是Query / Path
                    addTo = preStep.get("addTo","empty")
                    if addTo != "empty" and addTo["type"] in ["Path","Query"]:
                        if "{{" in self.request_url and "}}" in self.request_url:
                            refer_regex = "\{\{(.*)\}\}"
                            regex_obj = re.search(refer_regex,self.request_url)
                            refer_relation = regex_obj.group(1)
                            if refer_relation != "":
                                field_refer = searchInPreSteps(refer_relation, self.pre)
                                if field_refer is None:
                                    # 找不到step，可能是引用了不存在的prestep，找不到key，与refer中无法匹配定义的字段
                                    # log: not found prestep / prestep.{key} / prestep.refer.name
                                    exit(1)
                                field_value = extractField(field_refer,parent.result.get(self.name))
                                if field_value is None:
                                    # 根据引用关系无法在response中提取到具体的value
                                    # log: not extract field value
                                    exit(1)
                                self.request_url = self.request_url.replace("{{","").replace("}}","").replace(refer_relation,field_value)
                                
                                
            
    def run(self, parent: Suit):
        if self.pre is not None:
            self.setPre(parent)
        if self.setup is not None:
            self.setup()
        self.runRequest()
        if self.end is not None:
            self.end()
        
    def runRequest(self):
        print(f"self.session.{self.method}({self.request_url},{self.data},{self.desire_result['code']},{self.headers})")
        resp, exception = eval(f"self.session.{self.method}('{self.request_url}',{self.data},{self.desire_result['code']}, **{self.headers})")
        print(exception)
        if exception is not None:
            logging.error(f"{self.method} {self.request_url} error, {exception}")
            exit(1)
        self.result = resp


if __name__ == '__main__':
      pytest.main()
