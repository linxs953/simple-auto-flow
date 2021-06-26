import json
import logging

import httpx

req_timeout = 10


class StatusCodeInvalidException(Exception):
    pass


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
        try:
            resp = self.client.post(url=url, data=data, headers=self.client.headers)
            if resp.status_code != code:
                return \
                  dict(), \
                  StatusCodeInvalidException(f"Got invalid status code {resp.status_code}, expected {code}")
            if resp.text == "":
                return dict(), None
            resp_data = json.loads(resp.text)
            resp_data['code'] = resp.status_code
            return dict(resp_data), None
        except httpx.TimeoutException as timeout:
            logging.error(timeout)
            return dict(), timeout
        except Exception as e:
            logging.error(e)
            return dict(), e

    def GET(self, url: str, params, code: int, **headers) -> (dict, Exception):
        self.set_headers(**headers)
        try:
            resp = self.client.get(url, params=params)
            if resp.status_code != code:
                # 返回的状态码不对
                return \
                  dict(), \
                  StatusCodeInvalidException(f"Got invalid status code {resp.status_code}, {code}")
            if resp.text == "":
                return dict(), None
            resp_data = json.loads(resp.text)
            resp_data['code'] = resp.status_code
            return dict(resp_data), None
        except StatusCodeInvalidException as sce:
            logging.error(sce)
            return dict(), sce

    def Delete(self, url):
        # todo
        pass

    def Option(self, url):
        # todo
        pass
