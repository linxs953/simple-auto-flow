from aifc import Error
import logging
import sys

sys.path.append(".")

from core.base.session import Request
from urllib.parse import urlparse
from core.utils.step import *

logging.basicConfig(level = logging.INFO)

class RetryExcceedError(Error):
    pass

class SetPreStepError(Error):
    pass

class Step:
    def __init__(self, stepname: str,  request_url: str, method: str, data: dict, 
                      headers: dict, desire_result: list, pre: list, retry: int,
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

    def assert_operations(self, desire, symbol, current)-> bool:
        if type(desire) != type(current):
            logging.error("desire value type not equal to current type")
            return False
        if symbol == "gt":
            return current > desire
        if symbol == "lt":
            return current < desire
        if symbol == "include":
            if type(desire) != str:
                logging.error("assert symbol set [include],data type unsuppport except str")
                return False
            return desire in current
        if symbol == "eq":
            return current == desire

    def assert_result(self) -> bool:
        for result in self.desire_result:
            assert_ops = result.get("assert")
            field = result.get("field")
            desire = result.get("desire")
            try:
                assert self.assert_operations(desire, assert_ops,self.result[field]) == True
            except AssertionError:
                logging.error(f"Assert Error {type(self.result[field])}, {type(desire)}, {assert_ops}")
                return False
        logging.info(f"assert Step `{self.name}` successfully")
        return True
    
    def get_url_path(self) -> str:
        parsed = urlparse(self.request_url)
        return parsed.path
    
    def getReferData(self,expression: str, pres: list, resp_data: dict):
        field_refer = searchStepInPres(expression,pres)
        if field_refer is None:
                # 找不到step，可能是引用了不存在的prestep，找不到key，与refer中无法匹配定义的字段
                # log: not found prestep / prestep.{key} / prestep.refer.name
                return None, False
        field_value = extractField(field_refer,resp_data)
        if field_value is None:
            # 根据引用关系无法在response中提取到具体的value
            # log: not extract field value
            return None, False
        return field_value,True
    
    def setPre(self) -> bool:
        for preStep in self.pre:
            if preStep.get("refer",None) == None:
                logging.error("preStep miss `refer` field")
                return False
                
            if  preStep.get("response",None) == None:
                logging.error("preStep miss `response` field")
                return False
                
            resp = preStep.get("response")
            if preStep.get("addTo","") != "" and preStep['addTo'].get("type","") == "Headers":
                for data in preStep.get("refer"):
                    field_relation = data.get("field")
                    alias_name = preStep['addTo'].get("location")
                    token_type = resp.get("token_type","")
                    self.headers[alias_name] = f"{token_type} {extractField(field_refer=field_relation, body=resp)}"
            elif preStep['addTo'].get("type","") == "Body":
                for key,value in self.data.items():
                    if type(value) == str and "$" in value:
                        data_refer_parts = value.split("$")
                        value, ok = self.getReferData(data_refer_parts[1],self.pre,resp)
                        if not ok:
                            return False
                        self.data[key] = value
                    continue
                    
            elif preStep['addTo'].get("type","") in  ["Path","Query"]:
                # 处理type是Query / Path
                if "$" in self.request_url:
                    url_parts = str(self.request_url).split("/")
                    refer_relation = None
                    for part in url_parts:
                        if "$" in part:
                            refer_relation = part.split("$")[1]
                            break
                    if refer_relation != "":
                        value, ok = self.getReferData(refer_relation, self.pre, resp)
                        if not ok:
                            return False
                        # 提取的数据是int类型字段时，临时转成string
                        self.request_url = str(self.request_url).replace("$","",-1).replace(refer_relation,f"{value}",-1)
        return True              
                                
            
    def run(self) -> Error:
        if not self.setPre():
            # 设置preStep失败，中断执行
            return SetPreStepError
        if self.setup is not None and callable(self.setup):
            print(f"running setup method `{self.setup.__name__}`")
            self.setup()
        run_status = self.runRequest()
        if run_status:
            return run_status
        if self.end is not None and callable(self.end):
            print(f"running teardown method `{self.end.__name__}`")
            self.end()
        
    def runRequest(self) -> Error:
        resp, exception = eval(f"self.session.{self.method}('{self.request_url}',{self.data},{self.desire_result[0].get('desire')}, **{self.headers})")
        if exception is not None:
            logging.error(f"{self.method} {self.request_url} error, {exception}")
            logging.info(f"send request failed for {exception}")
            self.retry = self.retry - 1
            if self.retry >  0:
                self.runRequest()
            logging.error("Step exceed max retry times")
            return RetryExcceedError
        logging.info(f"Run Step `{self.name}` Successfully")
        self.result = resp


if __name__ == '__main__':
      pass
      
