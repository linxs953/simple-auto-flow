from loguru import logger
from simat_core.base.errors import RetryExcceedError
from simat_core.base.errors import FieldNotFoundInResp, KeyNotFound, ListEmpty, NotAttribute, SetPreStepError, TypeInvalidInGetData
from simat_core.base.session import Request
from urllib.parse import urlparse
from simat_core.utils.step import *

# 分割线
splitline = "-"*50 + "request metadata" + "-"*50

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


    """
        设置断言类型
    """
    def assert_operations(self, desire, symbol, current)-> bool:
        if type(desire) != type(current):
            logger.error("Assert Error: desire value type not equal to current type")
            return False
        if symbol == "gt":
            return current > desire
        if symbol == "lt":
            return current < desire
        if symbol == "ge":
            return current >= desire
        if symbol == "include":
            if type(desire) != str:
                logger.error("Assert Error: operation set include, but desire type not str")
                return False
            return desire in current
        if symbol == "eq":
            return current == desire



    """
        返回list指定index下的元素
    """
    def get_data_from_array(self, arr: list, index:str):
        if type(arr) != list:
            logger.error(f"data type get  -> [{type(arr)}], desire to <class.list>")
            return TypeInvalidInGetData()
        if len(arr) == 0:
            logger.error(f"list lenght get 0")
            return ListEmpty()
        if len(arr) <= index:
            return IndexError()
        index = int(index)
        return arr[index]
    
    
    """
        判断字符串是否为数字字符串
    """
    def is_number(self, key: str)-> bool:
        try:
            key = int(key)
            return True
        except ValueError:
            return False

    """
        获取dict指定key的内容
    """
    def get_data_from_dict(self,map: dict, key: str):
        if type(map) != dict:
            logger.error(f"data type get  -> [{type(map)}], desire to <class.dict>")
            return TypeInvalidInGetData()
        if map.get(key, None) == None:
            return KeyNotFound()
        return map.get(key)
    
    """
        通过expression从response json中获取值
    """
    def get_fielddata(self, expression: str):
        if "." not in expression:
            if self.result.get(expression,None) == None:
                logger.error(f"`{expression}` not  found  in step `{self.name}` response")
                return "", FieldNotFoundInResp()
            
            # expression只有一层，说明是字段名，直接返回
            return self.result.get(expression), None
        
        # expression是多层引用
        level_parts = expression.split(".")
        resp_data = self.result
        for level in level_parts:
            
            # 当前resp_data不是对象类型
            if type(resp_data) == str or type(resp_data) == int:
                logger.error(f"{type(resp_data)} have not attribute {level}")
                return "",NotAttribute()
            
            if self.is_number(level):
                # 当前的level是数字
                current_level_data = self.get_data_from_array(resp_data, level)
            else:
                # 当前level 不是数字
                current_level_data = self.get_data_from_dict(resp_data, level)
            
            # 通过level去获取对象数据时，出现异常
            if  isinstance(current_level_data, Exception):
                logger.error(f"get data by `{level}` falid.")
                return "", current_level_data
            resp_data = current_level_data
        return resp_data, None
    
    
    """
        断言response，与desire state对比
    """
    def assert_result(self) -> bool:
        for result in self.desire_result:
            assert_ops = result.get("assert")
            field_name = result.get("field")
            desire_result = result.get("desire")
            actual_result,err = self.get_fielddata(field_name)
            if isinstance(err,Exception):
                return False
            try:
                assert self.assert_operations(desire_result, assert_ops,actual_result) == True
            except AssertionError:
                logger.error(f"Assert Error: {field_name} should  {assert_ops} to  {desire_result}, but got {actual_result}")
                return False
        logger.info(f"assert Step `{self.name}` successfully")
        return True
    
    def get_url_path(self) -> str:
        parsed = urlparse(self.request_url)
        return parsed.path
    
    
    """
    通过refer expression获取引用的数据
    """
    def getReferData(self,expression: str, pres: list, resp_data: dict):
        field_refer = searchStepInPres(expression,pres)
        if field_refer is None:
            # 找不到step，可能是引用了不存在的prestep，找不到key，与refer中无法匹配定义的字段
            return None, False
        field_value = extractField(field_refer,resp_data)
        if field_value is None:
            # 根据引用关系无法在response中提取到具体的value
            return None, False
        return field_value,True
    
    def setPre(self) -> bool:
        for preStep in self.pre:
            # 验证preStep对象，判断是否有refer字段
            if preStep.get("refer",None) == None:
                logger.error("preStep object miss `refer` field")
                return False
            
            # 验证preStep对象，判断是否有response字段
            if  preStep.get("response",None) == None:
                logger.error("preStep object  miss `response` field")
                return False
                
            resp = preStep.get("response")
            
            if preStep.get("addTo","") != "" and preStep['addTo'].get("type","") == "Headers":
                # 处理addTo==Headers的情况
                for data in preStep.get("refer"):
                    field_relation = data.get("field")
                    alias_name = preStep['addTo'].get("location")
                    token_type = resp.get("token_type","")
                    self.headers[alias_name] = f"{token_type} {extractField(field_refer=field_relation, body=resp)}"
            
            elif preStep['addTo'].get("type","") == "Body":
                # 处理addTo==Body的情况
                for key,value in self.data.items():
                    
                    # 遍历request.data，找到value包含$符号的item
                    # 通过$后面的表达式，去获取表达式引用的真实数据
                    # $getTaskList.refer.taskId
                    if type(value) == str and "$" in value:
                        data_refer_parts = value.split("$")
                        value, ok = self.getReferData(data_refer_parts[1],self.pre,resp)
                        if not ok:
                            return False
                        self.data[key] = value
                    continue
            
            # 处理type是Query / Path
            elif preStep['addTo'].get("type","") in  ["Path","Query"]:
                if "$" in self.request_url:
                    url_parts = str(self.request_url).split("/")
                    refer_relation = None
                    for part in url_parts:
                        # 获取$后面的refer expression
                        if "$" in part:
                            refer_relation = part.split("$")[1]
                            break
                    if refer_relation != None:
                        value, ok = self.getReferData(refer_relation, self.pre, resp)
                        if not ok:
                            return False
                        
                        # 提取的数据是int类型字段时，临时转成string
                        # 替换url的refer expression
                        self.request_url = str(self.request_url).replace("$","",-1).replace(refer_relation,f"{value}",-1)
        return True              
                                
            
    def run(self) -> Exception:
        if not self.setPre():
            # 设置preStep失败，中断执行
            return SetPreStepError
        
        # 有设置setup方法，执行setup方法
        if self.setup is not None and callable(self.setup):
            logger.info(f"running setup method `{self.setup.__name__}`")
            self.setup()
        
        run_status = self.runRequest()
        
        # runner运行case失败，把error返回
        if run_status is not None:
            if self.retry > 0:
                self.retry = self.retry - 1
                self.run()
            logger.error("Step exceed max retry times")
        
        # 有设置teardown方法，执行teardown方法
        if self.end is not None and callable(self.end):
            logger.info(f"running teardown method `{self.end.__name__}`")
            self.end()
        
        return run_status
        
    def runRequest(self) -> Exception:
        if type(self.data) == str:
            # 兼容/POST接口 data必须是字符串（此处强转string）
            resp, exception = eval(f"self.session.{self.method}('{self.request_url}',\"\"\"{self.data}\"\"\",{self.desire_result[0].get('desire')}, **{self.headers})")
        else:
            resp, exception = eval(f"self.session.{self.method}('{self.request_url}',{self.data},{self.desire_result[0].get('desire')}, **{self.headers})")
        # runner执行失败，进行重试
        if exception is not None:
            resp_content = resp.get('resp',None)
            logger.info(
                "/{} {} failed\n{}\nmethod: {}\n\nurl: {}\n\ncode: {}\n\nbody: {}\n\nheaders: {}\n\nresponse: {}\n{}\n".format(
                    str(resp['method']).upper(),
                    urlparse(resp['url']).path,
                    splitline,
                    resp['method'],
                    resp['url'],
                    resp['code'],
                    str(resp['data']),
                    str(resp['headers']),
                    resp_content,
                    splitline
                )
            )
            return exception
            # self.retry = self.retry - 1
            # if self.retry >  0:
            #     self.runRequest()
            # logger.error("Step exceed max retry times")
            # return RetryExcceedError
        logger.info(f"Run Step `{self.name}` Successfully")
        self.result = resp


if __name__ == '__main__':
      pass
      
