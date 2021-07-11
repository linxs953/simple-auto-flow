

"""
通过refer_express去preSteps中寻找要extract的field
"""


import logging


def searchStepInPres(refer_express: str, preSteps: list):
    if "." not in refer_express:
        # log: refer format error
        return
    
    refer_express_parts = refer_express.split(".")
    step = ""
    field = ""
    
    # 拿到引用的preStep
    for index, st in enumerate(preSteps):
        if st.get("name") == refer_express_parts[0]:
            step = st
            break
        
        if index+1 == len(preSteps):
            # 这里其实不会出现pre step找不到的情况，在解析yaml的时候会验证引用是否合法有效，这里主要再做个保险
            #  log: not found step
            logging.error(f"not found step {refer_express_parts[0]}")
            return
    
    result = step
    for i in range(1,len(refer_express_parts)):
        try:
            if type(result) == list:
                for index_,f in enumerate(result):
                    if f.get('name') == refer_express_parts[i]:
                        field = f['field'] 
                        return field
                    if index_+1 == len(result):
                        # 这里出现的情况是：result是refer字段，然后无法匹配refer中定义的字段
                        # log: not found refer name
                        return
            else:
                result = step[refer_express_parts[i]]
        except KeyError as k:
            # 这里其实不是出现key找不到的情况，在解析yaml的时候会验证引用是否合法有效，这里主要再做个保险
            # log: not found key in xxx
            return



"""
通过field_refer去接口返回体中提取具体的字段值并返回
"""
def extractField(field_refer: str, body: dict):
    if "." not in field_refer:
        #  有可能字段名错误拿不到值，返回None
        field = body.get(field_refer,None)
        return field
    field_refer_parts = field_refer.split(".")
    length = len(field_refer_parts)
    field = body
    for key in range(length):
        try:
            refer_index = int(field_refer_parts[key])
            field = field[refer_index]
            continue
        except IndexError:
            # log: index out of range
            return
        except AttributeError:
            # log: None object can not any attr
            return
        except ValueError:
            # 要提取的数据一般不能为空，所以这里假定key正确时，获取的字段是不允许为空的，所以只有找不到key的时候返回None
            if field is None:
                # log: none type object
                return
            if type(field) == dict:
                field = field.get(field_refer_parts[key], None)
            else:
                # log: not dict, return None, for not found data by refer_expression
                return
        except Exception as e:
            logging.error(e)
            exit(1)
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

    field = searchInPreSteps("getToken.refer.token",preSteps)
    
    data = {
        "body":{
            "access_token": [
                {
                   "value":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1laWQiOiIxMzllNjBiZi00MDgyLTQ4ZTUtYWRiYi1kODZhNTZlMGU2ZGMiLCJ1bmlxdWVfbmFtZSI6IjEzOWU2MGJmLTQwODItNDhlNS1hZGJiLWQ4NmE1NmUwZTZkYyIsImdpdmVuX25hbWUiOiJ4aGEyMjA2NiIsImVtYWlsIjoieGhhMjIwNjZAdHVvZnMuY29tIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbW9iaWxlcGhvbmUiOiIiLCJyZWdpc3RlckRhdGUiOiIyMDIwLzgvMzEgMTI6MTc6MTAiLCJsYXN0UGFzc3dvcmRDaGFuZ2VkRGF0ZSI6IjE5NzAvMS8xIDg6MDA6MDAiLCJpc3MiOiJPY3RvcHVzLkF1dGgiLCJhdWQiOiJPY3RvcHVzLkFwaSIsImV4cCI6MTYyNDUwNDU3MiwibmJmIjoxNjI0NDE4MTcyfQ.3Y44E_9snrC2W8ikI3qhcgjgKt-BOXuInRfBglRAxrE"
                }
            ],
        },
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1laWQiOiIxMzllNjBiZi00MDgyLTQ4ZTUtYWRiYi1kODZhNTZlMGU2ZGMiLCJ1bmlxdWVfbmFtZSI6IjEzOWU2MGJmLTQwODItNDhlNS1hZGJiLWQ4NmE1NmUwZTZkYyIsImdpdmVuX25hbWUiOiJ4aGEyMjA2NiIsImVtYWlsIjoieGhhMjIwNjZAdHVvZnMuY29tIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbW9iaWxlcGhvbmUiOiIiLCJyZWdpc3RlckRhdGUiOiIyMDIwLzgvMzEgMTI6MTc6MTAiLCJsYXN0UGFzc3dvcmRDaGFuZ2VkRGF0ZSI6IjE5NzAvMS8xIDg6MDA6MDAiLCJpc3MiOiJPY3RvcHVzLkF1dGgiLCJhdWQiOiJPY3RvcHVzLkFwaSIsImV4cCI6MTYyNDUwNDU3MiwibmJmIjoxNjI0NDE4MTcyfQ.3Y44E_9snrC2W8ikI3qhcgjgKt-BOXuInRfBglRAxrE",
        "token_type": "bearer",
        "expires_in": 86399,
        "refresh_token": "9a11d2e7045c497c9cb4a1da27d9f2dc"
    }
    data = extractField("body.access_token.0.value",data)
