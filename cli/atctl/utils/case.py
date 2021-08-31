import base64
import yaml
from loguru import logger
import json
from atctl.templates import case_template
from urllib.parse import urlparse
from haralyzer import HarParser
from yapf.yapflib.yapf_api import FormatCode

class Validator:
    def __init__(self, data:dict) -> None:
        self.data = data
    
    def haskey(self, mapper: dict, key: str) -> bool:
        if not mapper:
            return False
        if mapper.get(key, None) == None:
            return False
        return True    
    
    # 验证字段是否存在
    def fieldsExist(self,fields: list, mapper: dict) -> bool:
        for field in fields:
            if not self.haskey(mapper, field):
                logger.error(f"field [{field} not found in [{mapper}]]")
                return False
        return True
    
class YamlValidator(Validator):
    def __init__(self, data:dict) -> None:
        self.data = data
    
    def globalValidate(self, glo: dict) -> bool:
        if not self.fieldsExist(["host","name"], glo):
            return False
        if glo.get("retry",""):
            self.data['global']['retry'] = 2
        return True
    
    
    """
    验证dict key是否存在
    """
    def fieldsExist(self,fields: list, mapper: dict) -> bool:
        for field in fields:
            if not self.haskey(mapper, field):
                logger.error(f"field [{field} not found in [{mapper}]]")
                return False
            if type(mapper[field]) == str and mapper[field] == "":
                logger.error(f"field [{field}] value empty in [{mapper}]")
                return False
        return True
     
               
    """
    验证yaml request字段的合法性
    """
    def requestValidate(self,request: dict) -> bool:
        # 验证string类型字段
        baseFieldList = ["method","host","urlPath", "pre", "data", "header"]
        if not self.fieldsExist(baseFieldList, request):
            return False
        
        # 验证pre字段是否为list
        if type(request.get('pre')) != list:
            logger.error("step.pre type is not list")
            return False
        
        # 验证pre[i]中各字段
        for preStep in request.get('pre'):
            if not self.fieldsExist(["name","addTo","refer"],preStep):
                return False
            if not self.fieldsExist(["type","location"],preStep['addTo']):
                return False
            for r in preStep['refer']:
                if not self.fieldsExist(["name","field"],r):
                    return False    
        
        return True
       
     
    """
    验证yaml step字段的合法性
    """
    def stepValidate(self,step: dict) -> bool:
        if not self.haskey(step, "step"):
            logger.error(f"stepname required in {step}")
            return False
        step = step['step']
        if not self.haskey(step, "stepname"):
            logger.error(f"stepname required in {step}")
            return False
            
        if not self.haskey(step, "request"):
            logger.error("request field required")
            return False
        
        if not self.requestValidate(step.get("request")):
            return False
        return True
        
    
    def validate(self) -> bool:
        if not hasattr(self, "data"):
            logger.error("self not have data attr")
            return False
        
        if not self.haskey(self.data,"global"):
            logger.error("not set global")
            return False
        
        # check global field
        if not self.globalValidate(self.data.get("global")):
            return False
        
        if not self.haskey(self.data,"steps"):
            logger.error("not define steps field")
            return False
        
        if len(self.data.get("steps")) == 0:
            logger.error("steps not contains any step")
            return False
        
        for st in self.data.get("steps"):
            # validate step
            if not self.stepValidate(st):
                return False
        
        logger.error(self.data)
        
        all_steps = self.data.get('steps')
        step_name_list = []
        if len(all_steps) > 0:
            for st in all_steps:
                current_step_name = st.get('step').get('stepname')
                
                # 验证step_name 唯一性
                if current_step_name in step_name_list:
                    logger.error(f"stepname `{current_step_name}` redefined")
                    return False
                pre_steps = st.get('step').get('request').get('pre')
                if len(pre_steps) > 0:
                    for p in pre_steps:
                        p_name = p.get('name')
                        
                        # 验证step.request.pre引用的正确性
                        if p_name not in step_name_list:
                            logger.error(f"`{st.get('step').get('stepname')}` refer not exist step `{p_name}`")
                            return False
                
                step_name_list.append(current_step_name)
        return True


class HarValidator(Validator):
    
    def validate(self) -> bool:
        if not self.fieldsExist(['entries'], self.data):
            return False
        
        for d in self.data['entries']:
            if not self.fieldsExist(["request","response"], d):
                return False
            
            request_data = d['request']
            if not self.fieldsExist(["method", "url", "headers"], request_data):
                return False
            
            if request_data['method'] == "POST" and not self.fieldsExist(["postData"], request_data):
                return False
                        
            # 验证response  
            response_data = d['response']
            if not self.fieldsExist(["status", "content"], response_data):
                return False
            
            if not self.fieldsExist(["text", "encoding"], response_data['content']):
                return False
        return True

class CaseConvert:
    def __init__(self, source: str, output: str):
        self.source = source
        self.output = output
    
    def write_file(self,code: str, path: str) -> bool:
        data,ok = FormatCode(code,style_config='{based_on_style: pep8, indent_width: 4, split_before_logical_operator: true}')
        if ok:
            with open(path, 'w') as codefile:
                codefile.write(data)
                return True
    
    def run():
        pass

class YamlCase(CaseConvert):
    def __init__(self, source: str, output: str) -> None:
        super().__init__(source, output)
        self.validator = YamlValidator(self.load())
        self.output = self.format_output(output) 
    
    def format_output(self, output):
        if self.validator.validate():
            output.format(self.validator.data['global']['name'])
            return output
        return output
    
    def generate_step_param(self, steps: list) -> list:
        stepesParam = list()
        
        # 生个多个step参数
        for st in steps:
            s = st.get("step")
            setup_func = s.get('request').get('setup',None)
            teardown_func  = s.get('request').get('teardown_func',None)
            url = f"{s.get('request').get('host')}{s.get('request').get('urlPath')}"
            element = f"""(
                "{s.get("stepname")}",
                "{url}",
                "{s.get("request").get("method")}",
                {s.get("request").get("data")},
                {s.get("request").get("header")},
                {s.get("response")},
                {s.get("request").get("pre")},
                {s.get("retry")},
                {setup_func},
                {teardown_func}
              )
            """
            stepesParam.append(
                element
            )
        return stepesParam
    
    def generate_code(self) -> str:
        data = self.validator.data
        params = self.generate_step_param(data['steps'])
        length = len(data['steps'])
        stepsCode = ""
        for i in range(length):
            
            # 处理最后一个的step时，不添加「,」
            if i == length - 1:
                code = f"Step(*{params[i]})"
            else:
                code = f"Step(*{params[i]}),"
            stepsCode += code

        # 获取case 模板代码
        # 将stepsCode填充进模板中
        fileCode = case_template.code
        fileCode = fileCode.format(
            data.get('global').get('name'),
            stepsCode, 
            data.get('global').get('retry'),
            data.get('global').get('name'),
        )
        return fileCode
    
    def load(self) -> dict:
        with open(self.source,"rb") as stream:
            data = yaml.load(stream,Loader=yaml.CLoader)
            self.content = dict(data)
            return dict(data)
    
    def run(self):
        if self.validator.validate():
            # yaml 验证成功
            code = self.generate_code()
            self.write_file(code=code, path=self.output)
            logger.info(f"generate code `{self.output}` successfully")
            return
        # validate failed
        exit(1)

class HarCase(CaseConvert):
    def __init__(self, source: str, output: str):
        super().__init__(source, output)
        self.data = self.load(self.source)
        self.validator = HarValidator(self.data)
        self.default_retry = 5
        
    def load(self, sourcepath: str)-> dict:
        with open(sourcepath,'r') as harfile:
            try:
                content = HarParser(json.loads(harfile.read()))
            except Exception as e:
                logger.error(e)
                return
        return content.har_data
    
    def load_headers(self, header_list: list) -> dict:
        if type(header_list) != list:
            logger.error(f"convert headers failed! desire list but got {type(header_list)}")
            return None
        headers = {}
        for h in header_list:            
            if h.get("name",None) == None or h.get("value", None) == None:
                logger.error("not found header name or value")
                return None
            headers[h['name']] = h['value']
        return headers
    
    def load_postdata(self, data: str):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"load post data error for {e}")
            return None
        
    def load_response(self, data: str, encoding: str):
        if encoding == "base64":
            assert_resp_list = list()
            if data == "":
                return list()
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
                logger.error(e)
                return list()
        return list()
            
    def generate_params(self)-> list:
        step_params = []
        for entry in self.data['entries']:
            
            # 获取request metadata
            request, response = entry['request'], entry['response']
            req_url, req_method, headers = request['url'],request['method'], request['headers']
            step_name = urlparse(req_url).path
            
            req_headers = self.load_headers(headers)
            if not req_headers:
                return None
            req_post_data = None
            
            # 获取post data
            if req_method == "POST":
                if request['postData'].get('text') != "" and \
                        self.load_postdata(request['postData'].get('text')) != None:
                    req_post_data = self.load_postdata(request['postData'].get('text'))
            
            # 获取status code
            resp_code = response['status']
            
            # 设置desire status code 
            resp_body = [{"field": "code","assert": "eq","desire": resp_code}]
            
            # 把response的结果作为desire result添加到resp_body
            resp_body.extend(self.load_response(response['content'].get('text'),response['content'].get('encoding')))
            if not resp_body:
                logger.error("load response faild got None")
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
            # 处理最后一个step时，不添加「,」
            if i == length - 1:
                code = f"Step(*{steps[i]})"
            else:
                code = f"Step(*{steps[i]}),"
            stepsCode += code
 
        # 获取case 模板代码
        # 将stepsCode填充进模板中
        fileCode = case_template.code
        fileCode = fileCode.format(
            self.output.split("/")[-1].split(".")[0],
            stepsCode, 
            self.default_retry,
            self.output.split("/")[-1].split(".")[0],
        )
        if self.write_file(code=fileCode, path=self.output):
            logger.info("generate testfile successfully")
            return True
        logger.error("generate testfile failed")
        return False

    def run(self):
        if not self.validator.validate():
            exit(1)
        logger.info("validate successfully ")
        if not self.write_code():
            exit(1)




