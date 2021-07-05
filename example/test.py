import sys

sys.path.append(".")
from core.base.suit import Suit
from core.base.step import Step
import pytest
from main import *


class Testtest(Suit):
    def setup_method(self, method):
        self.init_resource([])
        self.steps = [
            Step(*(
                "/mm/sub",
                "https://p71-caldav.icloud.com.cn/mm/sub?token=034eacf766cb5df27a4894d5a22e2f00b5cd56a5cd7c9ac0308f4b77996a933f&key=16114739156",
                "POST", None, {
                    'Host': 'p71-caldav.icloud.com.cn',
                    'User-Agent': 'macOS/11.5 (20G5023d) CalendarAgent/954',
                    'X-Apple-I-MD-LU':
                    '9D338A57912A28E4227D2E35E66736D3B8F49CD3ACE692432707D8BC7B1D428D',
                    'X-Apple-Client-Info':
                    '<MacBookPro15,3> <macOS;11.5;20G5023d> <com.apple.coredav/1.0.1 (com.apple.CalendarAgent/8.0)>',
                    'X-Mme-Device-Id': '66D18D91-605C-56FC-A867-1129BB7F93D2',
                    'X-MMe-Client-Info':
                    '<MacBookPro15,3> <macOS;11.5;20G5023d> <com.apple.AuthKit/1 (com.apple.CalendarAgent/954)>',
                    'Content-Length': '0',
                    'X-Apple-I-TimeZone': 'GMT+8',
                    'Connection': 'keep-alive',
                    'X-Apple-I-Client-Time': '2021-07-05T15:07:06Z',
                    'Authorization':
                    'X-MobileMe-AuthToken MTYxMTQ3MzkxNTY6RUFBVEFBQUFCTHdJQUFBQUFHQTY4WFVSRG1kekxtbGpiRzkxWkM1aGRYUm92UURMWEVGampBejR1VTFzaDBQbkZKTFlZTG1qbG5OakN2UWpGaDJqa1pZMFBwT1ArejcvSHVUU04vYThrS3hhcjdGV0tVZFlONkt6dVZDall6anRQbDgxVU9nelZPVGt3WTdOZ1lPcmdkWk5oTUJuMGxyWFZYZDhZTXJxK1NYd3VlS2hKRXJ1dXFGQkZENUtKa042V1FYUG1keW40UT09',
                    'Accept-Language': 'zh-cn',
                    'X-Apple-I-MD-RINFO': '17106176',
                    'X-Apple-DAV-Pushtoken':
                    '034eacf766cb5df27a4894d5a22e2f00b5cd56a5cd7c9ac0308f4b77996a933f',
                    'Accept': '*/*',
                    'Content-Type': 'text/xml',
                    'X-Apple-I-MD-M':
                    'eT5DRoVGtuZ7LzziTQB71ID5dccoryKjVAQ/9L3u0VNnPSwKDoZFeCMQ+osZgN2S0SLkiT7cr6prMEPw',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'X-Apple-I-Locale': 'zh_CN',
                    'X-Apple-I-MD': 'AAAABQAAABB1hqtnQftig5rMAvmAwsY5AAAAAQ=='
                }, [{
                    'field': 'code',
                    'assert': 'eq',
                    'desire': 200
                }], [], 5, None, None))
        ]

    def teardown_method(self, method):
        pass

    @pytest.mark.flaky(reruns=5)
    def test_test(self):
        self.run()
