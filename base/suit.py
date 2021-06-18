import pytest
from base.step import Step, TestStep


class Suit:
    def __init__(self, filepath: str):
        self.step_result = dict()
        # step:
        self.steps = self.generate(filepath=filepath)
        self.result = list()


    def generate(self, filepath: str) ->list(Step):
        return list(Step)
    
    def run(self):
        for step in self.steps:
            # 初始化step资源
            step.init_resource()
            # 执行step
            step.runRequest()
            # 验证response
            step.assert_result()
            # 验证成功，将step的结果写入到suit.result
            self.result[step.get_url_path()] = self.result.append(step.result)
            