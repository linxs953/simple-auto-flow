import logging
import sys
import re

sys.path.append("")

from session import Request
from urllib.parse import urlparse
from utils.step import *
from main import setup

logging.basicConfig(level = logging.INFO)

class Step:
    def __init__(self, stepname: str,  request_url: str, method: str, data: dict, 
                      headers: str, desire_result: dict, pre: list, retry: int,
                      setupFunc:str, endFunc:str):
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
        self.retry = retry
        self.result = dict()

    def assert_result(self):
        for k,_ in self.desire_result.items():
            # todo: assert error
            if self.result.get(k,"") != "":
                try:
                    assert self.result[k] == self.desire_result.get(k)
                except AssertionError:
                    logging.error(f"Assert [{k}] field failed. desire got  `{self.result[k]}``  actually got  `{self.desire_result[k]}`` in [{self.method.upper()}] {self.request_url}")
                    exit(1)
        logging.info(f"assert Step `{self.name}` successfully")
    
    def get_url_path(self) -> str:
        parsed = urlparse(self.request_url)
        return parsed.path

    def setPre(self):
        for preStep in self.pre:
            if preStep.get("addTo","") != "" and preStep['addTo'].get("type","") == "Headers":
                if preStep.get("refer",None) != None and preStep.get("response",None) != None:
                    resp = preStep.get("response")
                    for data in preStep.get("refer"):
                        field_relation = data.get("field")
                        alias_name = preStep['addTo'].get("location")
                        token_type = resp.get("token_type","")
                        self.headers[alias_name] = f"{token_type} {extractField(field_refer=field_relation, body=resp)}"
            elif preStep['addTo'].get("type","") == "Body":
                if preStep.get("refer",None) != None and preStep.get("response",None) != None:
                    resp = preStep.get("response")
                    for key,value in self.data.items():
                        if type(value) == str and "$" in value:
                            data_refer_parts = value.split("$")
                            field_refer = searchInPreSteps(data_refer_parts[1],self.pre)
                            
                            if field_refer is None:
                                    # 找不到step，可能是引用了不存在的prestep，找不到key，与refer中无法匹配定义的字段
                                    # log: not found prestep / prestep.{key} / prestep.refer.name
                                    exit(1)
                            field_value = extractField(field_refer,resp)
                            if field_value is None:
                                # 根据引用关系无法在response中提取到具体的value
                                # log: not extract field value
                                exit(1)
                            self.data[key] = field_value
                        continue
                    
            elif preStep['addTo'].get("type","") in  ["Path","Query"]:
                # 处理type是Query / Path
                if preStep.get("refer",None) != None and preStep.get("response",None) != None:
                    resp = preStep.get('response')
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
                            field_value = extractField(field_refer,resp)
                            if field_value is None:
                                # 根据引用关系无法在response中提取到具体的value
                                # log: not extract field value
                                exit(1)
                            self.request_url = self.request_url.replace("{{","").replace("}}","").replace(refer_relation,field_value)
                                
                                
            
    def run(self):
        self.setPre()
        if self.setup is not None and callable(self.setup):
            print(f"running setup method `{self.setup.__name__}`")
            self.setup()
        self.runRequest()
        if self.end is not None and callable(self.end):
            print(f"running teardown method `{self.end.__name__}`")
            self.end()
        
    def runRequest(self):
        resp, exception = eval(f"self.session.{self.method}('{self.request_url}',{self.data},{self.desire_result['code']}, **{self.headers})")
        if exception is not None:
            logging.error(f"{self.method} {self.request_url} error, {exception}")
            logging.info(f"send request failed for {exception}")
            self.retry = self.retry - 1
            if self.retry >  0:
                self.runRequest()
            exit(1)
        logging.info(f"Run Step `{self.name}` Successfully")
        self.result = resp


if __name__ == '__main__':
      pass
      
