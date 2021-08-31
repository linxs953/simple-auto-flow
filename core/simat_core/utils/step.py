from loguru import logger

"""
通过refer_express去preSteps中寻找要提取extract的field-expression
"""

def searchStepInPres(refer_express: str, preSteps: list):
    # 验证引用的格式，必须包含.字符
    if "." not in refer_express:
        logger.error("refer-prestep expression format error")
        return
    
    refer_express_parts = refer_express.split(".")
    step = ""
    field = ""
    
    # 获取引用的每个「关键字」
    # 遍历preStep对象，拿到关键字引用的preStep对象
    for index, st in enumerate(preSteps):
        if st.get("name") == refer_express_parts[0]:
            step = st
            break
        
        # 列表最后一个元素，找不到关键字引用preStep对象，直接return
        if index+1 == len(preSteps):
            # 这里其实不会出现pre step找不到的情况，在解析yaml的时候会验证引用是否合法有效，这里主要再做个保险
            #  log: not found step
            logger.error(f"not found step `{refer_express_parts[0]}`")
            return
    
    result = step
    
    # 遍历关键字列表，根据每个关键字去step里面的值
    # result此时拿到的是preStep对象
    for i in range(1,len(refer_express_parts)):
        try:
            if type(result) == list:
                for index_,ele in enumerate(result):
                    # 处理refer数组
                    # 如果当前type(result)==list && reuslt == step.refer
                    #   - 判断express(getToken.refer.token)引用的字段名token在refer中是否可以找到，找到就return
                    if ele.get('name', None) == refer_express_parts[i]:
                        field = ele['field'] 
                        return field
                    if index_+1 == len(result):
                        # 这里出现的情况是：
                        #   - result此时是refer对象，然后无法匹配refer中定义的字段
                        #   - 在steps中找不到expression中引用的步骤（不太可能出现，在yaml初始化的时候会去检查）
                        logger.error("not found refered-field named {} pre-step.refer", refer_express_parts[i])
                        return
            else:
                result = step[refer_express_parts[i]]
        except KeyError as k:
            # 这里其实不是出现key找不到的情况，在解析yaml的时候会验证引用是否合法有效，这里主要再做个保险
            logger.error("key `{}` not found in map `{}`", refer_express_parts[i], step)
            return



"""
通过field_refer去接口返回体中提取具体的字段值并返回
"""

def extractField(field_refer: str, body: dict):
    if "." not in field_refer:
        #  有可能字段名错误拿不到值，这里如果字段名错误默认返回None
        field = body.get(field_refer,None)
        return field
    
    # refer expression 转换成列表
    field_refer_parts = field_refer.split(".")
    length = len(field_refer_parts)
    
    # field：引用表达式所要提取的字段的值
    field = body
    
    # 这里处理一下list index和dict key的提取操作
    for key in range(length):
        try:
            # 当前field_refer_parts[key]是数字，field=field[refer_index]
            refer_index = int(field_refer_parts[key])
            field = field[refer_index]
            continue
        
        except IndexError:
            logger.error("`{}` index out of range in `{}`",refer_index, field)
            return
        
        except AttributeError:
            logger.error("there are no attributes in `{}` object ", field)
            return
        
        except ValueError:
            # 要提取的数据一般不能为空，所以这里假定key正确时，获取的字段是不允许为空的，所以只有找不到key的时候返回None
            if field is None:
                logger.error("extract field can not be None")
                return
            
            # 如果field_refer_parts[key]不是数字，而是一个dict key
            if type(field) == dict:
                field = field.get(field_refer_parts[key], None)
            else:
                logger.error("extract field type not dict or list")
                return
        
        except Exception as e:
            logger.error(f"extract field data from refer expression failed for  {str(e)}")
            return
        
    return field
    
        


if __name__ == '__main__':
    preSteps = [
        {
            "name": "getToken",
            "addTo": {
                "type": "Headers",
                "location": "Authorization"
            },
            "refer": [
                {
                    "name": "token",
                    "field": "assess_token"
                }
            ]
        },
    ]

    field = searchStepInPres("getToken.refer.token",preSteps)
    
    data = {}
    data = extractField("body.access_token.0.value",data)