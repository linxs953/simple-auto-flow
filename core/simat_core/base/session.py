from core.simat_core.base.errors import StatusCodeInvalidException
import json
from loguru import logger
import httpx

req_timeout = 10


class Request:
    def __init__(self):
        self.client = httpx.Client(verify=False)
        self.client.timeout = req_timeout

    def set_headers(self, **headers):
        if headers is not None:
            for k, v in headers.items():
                self.client.headers[k] = v

    def POST(self, url: str, data: dict, code: int, **headers) -> (dict, Exception):
        self.set_headers(**headers)
        resp_metadata = dict(url=url,headers=headers,method="POST",data=data,code=code)
        try:
            resp = self.client.post(url=url, data=data, headers=self.client.headers)
            if resp.status_code != code:
                resp_metadata['code'] = resp.status_code
                return resp_metadata, \
                  StatusCodeInvalidException(f"Got invalid status code {resp.status_code}, expected {code}")
            if resp.text == "":
                resp_metadata['code'] = resp.status_code
                return resp_metadata, None
            resp_data = json.loads(resp.text)
            resp_data['code'] = resp.status_code
            return dict(resp_data), None
        except httpx.TimeoutException as timeout:
            resp_metadata['code'] = -1
            logger.error(f"Runner send POST request timeout for {str(timeout)}")
            return resp_metadata, timeout
        except Exception as e:
            resp_metadata['code'] = -1
            logger.error(f"Runner send POST request occur error for {str(e)}")
            return resp_metadata, e

    def GET(self, url: str, params, code: int,data=None,**headers) -> (dict, Exception):
        self.set_headers(**headers)
        resp_metadata =  dict(url=url,headers=headers,method="GET",data=data)
        try:
            resp = self.client.get(url, params=params)
            if resp.status_code != code:
                # 返回的状态码不对
                resp_metadata['code'] = resp.status_code
                return resp_metadata, \
                  StatusCodeInvalidException(f"Got invalid status code {resp.status_code}, {code}")
            if resp.text == "":
                resp_metadata['code'] = resp.status_code
                return resp_metadata, None
            resp_data = json.loads(resp.text)
            resp_data['code'] = resp.status_code
            return dict(resp_data), None
        except httpx.TimeoutException as timeout:
            resp_metadata['code'] = -1
            logger.error(f"Runner send GET request timeout for {str(timeout)}")
            return resp_metadata, timeout
        except Exception as hxe:
            logger.error(f"Runner send GET request failed for {str(hxe)}")
            return resp_metadata, hxe

    def Delete(self, url):
        # todo
        pass

    def Option(self, url):
        # todo
        pass
