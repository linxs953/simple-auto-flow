"""
1. 根据路径解析一个或多个har文件

2. 生成Step对象

3. 生成python code 继承于Suit对象
    -  生成setup和teardown方法
    -  自动在测试方法上方添加注解rerun failed case
"""
import base64
import logging
from urllib.parse import urlparse
from haralyzer import HarParser
import json
import sys
sys.path.append("")
from config import case_template
from yapf.yapflib.yapf_api import FormatCode





class HarValidator:
    def __init__(self, data: dict) -> None:
        self.data = data
    
    
    
    def validate(self) -> bool:
        if not self.fieldExist(['entries'], self.data):
            return False
        
        for d in self.data['entries']:
            if not self.fieldExist(["request","response"], d):
                return False
            
            request_data = d['request']
            if not self.fieldExist(["method", "url", "headers"], request_data):
                return False
            
            if request_data['method'] == "POST" and not self.fieldExist(["postData"], request_data):
                return False
                        
            # 验证response  
            response_data = d['response']
            if not self.fieldExist(["status", "content"], response_data):
                return False
            
            if not self.fieldExist(["text", "encoding"], response_data['content']):
                return False
        return True
            
    
    def fieldExist(self, fieldList: list, target: dict) -> bool:
        for field in fieldList:
            if target.get(field, None) == None:
                logging.error(f"field [{field}] not found in target")
                return False
        return True

class HarCase:
    def __init__(self, source: str, output: str):
        self.data = self.load(source)
        self.validator = HarValidator(self.data)
        self.default_retry = 5
        self.output = output
        
    
    def load(self, sourcepath: str)-> dict:
        with open(sourcepath,'r') as harfile:
            content = HarParser(json.loads(harfile.read()))
        return content.har_data
    
    
    def load_headers(self, header_list: list) -> dict:
        if type(header_list) != list:
            logging.error(f"convert headers failed! desire list but got {type(header_list)}")
            return None
        headers = {}
        for h in header_list:            
            if h.get("name",None) == None or h.get("value", None) == None:
                logging.error("not found header name or value")
                return None
            headers[h['name']] = h['value']
        return headers
    
    
    def load_postdata(self, data: str):
        print(data)
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            logging.error(f"load post data error for {e}")
            return None
        
        
    def load_response(self, data: str, encoding: str):
        if encoding == "base64":
            assert_resp_list = list()
            try:
                resp_body = json.loads(base64.b64decode(data))
                for k,v in resp_body.items():
                    single_field = dict()
                    single_field["field"] = k
                    single_field["desire"] = v
                    single_field['assert'] = "eq"
                    assert_resp_list.append(single_field)
                return assert_resp_list
            except json.JSONDecodeError as e:
                logging.error(e)
                return None
        return None
            
    
    def generate_params(self)-> list:
        step_params = []
        for entry in self.data['entries']:
            request, response = entry['request'], entry['response']
            req_url, req_method, headers = request['url'],request['method'], request['headers']
            step_name = urlparse(req_url).path
            req_headers = self.load_headers(headers)
            if not req_headers:
                return None
            req_post_data = None
            if req_method == "POST":
                if request['postData'].get('text') != "" and \
                        self.load_postdata(request['postData'].get('text')) != None:
                    req_post_data = self.load_postdata(request['postData'].get('text'))
            resp_code = response['status']
            resp_body = [{"field": "code","assert": "eq","desire": resp_code}]
            resp_body.extend(self.load_response(response['content'].get('text'),response['content'].get('encoding')))
            if not resp_body:
                logging.error("load response faild got None")
                return None
            element = case_template.step.format(step_name,req_url,req_method,req_post_data,
                                      req_headers,resp_body,[],self.default_retry,None,None)
            step_params.append(element)
        return step_params
        
        

    def write_code(self) -> bool:
        steps = self.generate_params()
        if not steps:
            return False
        length = len(steps)
        stepsCode = ""
        for i in range(length):
            if i == length - 1:
                code = f"Step(*{steps[i]})"
            else:
                code = f"Step(*{steps[i]}),"
            stepsCode += code
 
        fileCode = case_template.code
        fileCode = fileCode.format(
            self.output.split("/")[-1].split(".")[0],
            stepsCode, 
            self.default_retry,
            self.output.split("/")[-1].split(".")[0],
        )
        if self.write_file(code=fileCode, path=self.output):
            logging.info("generate testfile successfully")
            return True
        logging.info("generate testfile failed")
        return False
    
    def write_file(self,code: str, path: str) -> bool:
        data,ok = FormatCode(code,style_config='{based_on_style: pep8, indent_width: 4, split_before_logical_operator: true}')
        if ok:
            with open(path, 'w') as codefile:
                codefile.write(data)
            return True
        return False

    
    def run(self):
        if not self.validator.validate():
            exit(1)
        logging.info("validate successfully ")
        if not self.write_code():
            exit(1)
            




if __name__ == '__main__':
    har = HarCase("./har/test.har","./test.py")
    har.run()