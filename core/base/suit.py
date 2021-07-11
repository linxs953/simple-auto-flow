import typing
import sys
sys.path.append(".")

from core.base.step import Step


class Suit:
    def init_resource(self, steps: typing.List[Step]):
        self.step_result = dict()
        self.steps = steps
        self.result = dict()


    
    def run(self):
        for step in self.steps:
            # 动态执行preStep中的$a.b.c()
            for p in step.pre:
                p['response'] = eval(f"{p['response'].replace('$suit','self')}")
            # 执行step
            step_status = step.run()
            if step_status:
                exit(1)
            # 验证response
            if not step.assert_result():
                #  某个step断言失败，直接break
                break
            # 验证成功，将step的结果写入到suit.result
            self.result[step.name] = step.result


if __name__ == '__main__':
    pass
    