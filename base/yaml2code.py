"""
1. 根据路径解析一个或多个yaml

2. 生成Step对象

3. 生成python code 继承于Suit对象
    -  生成setup和teardown方法
    -  自动在测试方法上方添加注解rerun failed case
"""

import yaml
import logging
import sys
sys.path.append("")
from config import case_template
from yapf.yapflib.yapf_api import FormatCode



class YamlValidator:
    def __init__(self, data:dict) -> None:
        self.data = data
    
    def haskey(self, mapper: dict, key: str) -> bool:
        if mapper.get(key, None) == None:
            return False
        return True
            
    
    def globalValidate(self, glo: dict) -> bool:
        if not self.fieldsExist(["host","name"], glo):
            return False
        if glo.get("retry",""):
            self.data['global']['retry'] = 2
        return True
    
    # 验证字段是否存在
    def fieldsExist(self,fields: list, mapper: dict) -> bool:
        for field in fields:
            if not self.haskey(mapper, field):
                logging.error(f"field [{field} not found in [{mapper}]]")
                return False
            if type(mapper[field]) == str and mapper[field] == "":
                logging.error(f"field [{field}] value empty in [{mapper}]")
                return False
        return True
                
    
    def requestValidate(self,request: dict) -> bool:
        # 验证string类型字段
        baseFieldList = ["method","host","urlPath", "pre", "data", "header"]
        if not self.fieldsExist(baseFieldList, request):
            return False
        
        # 验证pre字段是否为list
        if type(request.get('pre')) != list:
            logging.error("step.pre type is not list")
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
        
    
    
    def stepValidate(self,step: dict) -> bool:
        if not self.haskey(step, "step"):
            logging.error(f"stepname required in {step}")
            return False
        step = step['step']
        if not self.haskey(step, "stepname"):
            logging.error(f"stepname required in {step}")
            return False
            
        if not self.haskey(step, "request"):
            logging.error("request field required")
            return False
        
        if not self.requestValidate(step.get("request")):
            return False
        return True
        
    
    def validate(self) -> bool:
        if not hasattr(self, "data"):
            logging.error("self not have data attr")
            return False
        
        if not self.haskey(self.data,"global"):
            logging.error("not set global")
            return False
        
        # check global field
        if not self.globalValidate(self.data.get("global")):
            return False
        
        if not self.haskey(self.data,"steps"):
            logging.error("not define steps field")
            return False
        
        if len(self.data.get("steps")) == 0:
            logging.error("steps not contains any step")
            return False
        
        for st in self.data.get("steps"):
            # validate step
            if not self.stepValidate(st):
                return False
        
        return True
    


class YamlCase:
    def __init__(self, source: str, output: str) -> None:
        self.source = source
        self.validator = YamlValidator(self.load())
        self.output = self.formatOutput(output) 
    
    def formatOutput(self, output):
        if self.validator.validate():
            output.format(self.validator.data['global']['name'])
            return output
        return output
    
    def generateStepParam(self, steps: list) -> list:
        stepesParam = list()
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
        params = self.generateStepParam(data['steps'])
        length = len(data['steps'])
        stepsCode = ""
        for i in range(length):
            if i == length - 1:
                code = f"Step(*{params[i]})"
            else:
                code = f"Step(*{params[i]}),"
            stepsCode += code
 
        fileCode = case_template.code
        fileCode = fileCode.format(
            data.get('global').get('name'),
            stepsCode, 
            data.get('global').get('retry'),
            data.get('global').get('name'),
        )
        return fileCode
    
    def write_file(self,code: str, path: str) -> bool:
        data,ok = FormatCode(code,style_config='{based_on_style: pep8, indent_width: 4, split_before_logical_operator: true}')
        if ok:
            with open(path, 'w') as codefile:
                codefile.write(data)
    

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
            logging.info(f"generate code `{self.output}` successfully")
    