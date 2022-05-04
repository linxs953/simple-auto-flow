# simple auto-flow api testing scaffold

## Intro

一个用于API自动化测试的脚手架，使用Python编写


##  Why

###### 一开始其实选型HttpRunner用来做接口自动化，但在实践过程中发现有以下问题不能满需求

- 设置setup 和 teardown方法失效（缺少这个导致后面的流程无法开展）
- 单个用例的重试（目前httprunner未支持，pytest有插件）
- 在用例执行失败时，定义log输出信息，方便复现和debug（这个不是刚需，但是自己写可以完美支持）

###### 基于以上，需要一个简易的API测试脚手架，能够满足以下基础功能

- 通过yaml声明一条用例(Suit)
- 能够将yaml文件转换成python代码
- 支持`Step`间数据引用传递
- 支持`Step` 和 `Suit`级别的重试
## Quick Start

```shell
pip3 install simat-core
pip3 install atctl
atctl start-project [project_name]
```

## Guide
###### 1. 编写yaml

```yaml

global:
   host: "https://api.test.com"
   name: "Login"
   retry: 1
steps:
   - step:
      stepname: "getToken"
      request:
        pre: []
        method: "POST"
        host: "https://api.test.com"
        urlPath: "/gettoken"
        data: {
          "username":"[username]",
          "password":"[password]",
        }
        header:
          User-Agent: ""
      response: [
        {
          "field": "code",
          "assert": "eq",
          "desire": 200
        }
      ]
   - step:
      stepname: "getTaskList" 
      retry: 5
      request:
        pre: 
          - name: "getToken"
            response: "$suit.result['getToken']"
            addTo: 
              type: "Headers" # Headers / Body
              location: "Authorization" # data.dataList.taskId
            refer:
              - name: "token"
                field: "access_token"
        method: "get"
        host: "https://api.test.com"
        urlPath: "/search"
        data: None
        header: {
          "Content-Type": "application/json; charset=utf-8",
        }
      response: [
        {
          "field": "code",
          "assert": "eq",
          "desire": 200
        },
        {
          "field": "error",
          "assert": "include",
          "desire": "success"
        }
      ]
```

###### 2. 生成python代码

```python
python3 run setup.py [yaml_source_path] [python_output_path]
```


###### 3. 通过pytest执行生成的测试文件

```shell
pytest testcases/
```

## Overview 

#### 相关concept

- **Request**:    Request封装了http请求的常用方法，如`POST` , `GET`等，返回response.text
- **Step**:       一个Step描述的是一个API请求，用来管理Request对象，以及加上`retry`，`beforeRequest`, `afterRequest`等特性
- **Suit**:       一个Suit描述的是一条用例，由多个Step组成，存储Step执行后的结果，供其他Step使用。
<br>

![执行流程](img/执行流程图.png)

<br>
<br>

![运行原理](img/auto-flow-framework.png)

#### 模块设计

- cli模块
  - init
    - 初始化一个项目模块
  - code generate
    - 转换har文件成python code / yaml / json
- core模块
  - Suit
    - 管理一组Step对象，调用Step的`run`和`assert`方法，进行用例的执行和用例结果断言，并存储每个Step的结果
  - Step
    - 一条用例的抽象
    - 解析request中引用数据表达式，获取真实数据进行填充
      - 解析Body参数引用
      - 解析header引用
      - 解析url参数引用
      - 解析对response数据的引用
    - 包含一条用例的生命周期，`组装api请求数据`，`api请求pre-action`，`发起api调用`，`response结果断言`，`api请求after-action`
    - 用例重试
  - Runner
    - 封装http方法，发起api调用的模块


## Feature

- [x] 支持yaml格式
- [x] 能够转成python 测试代码
- [x] 当前Step可以引用所在Case的前置Step的数据
- [x] 支持har格式
- [ ] 支持全局变量，多Suit共享
- [ ] 支持报告
- [ ] 支持locust
- [ ] 支持其他协议的接口  


 
