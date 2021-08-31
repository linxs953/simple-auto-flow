from loguru import logger
import os


"""
判断path是否是一个目录
"""
def is_dir(path):
    if not os.path.exists(path):
        logger.error(f"{path} not exists")
        return False
    
    return os.path.isdir(path)

"""
判断file是否是一个文件
"""
def is_file(path):
    if not os.path.exists(path):
        logger.error(f"{path} not exists")
        return False
    
    return os.path.isfile(path)


"""
将相对路径转换成绝对路径
    1. 如果传入的base不为空，绝对路径={base}/{path}
    2. 如果没有传base，绝对路径={current_pwd}/{pwd}
"""
def convert_relative_path(path,base=None)-> str:
    pwd = os.getcwd()
    if base is not None:
        pwd = base
    pwd_parts = pwd.split("/")
    levels = path.split("/")[0]
    
    # path前面最多只有1个「.」符号
    if len(levels) <= 1:
        # 只有一个「.」的情况
        if path.split("/")[0] == ".":
            abs_path = path.replace(".", pwd)
            return abs_path
        
        # 没有「.」的情况
        abs_path = f"{pwd}{path}"        
        return abs_path
    
    # path前面有2个以上的「.」符号
    # 如果只有一个「.」就显示当前路径
    # 如果有两个「.」就显示base的上一级路径
    end_index = len(pwd_parts) - len(levels) + 1
    if end_index >= len(pwd_parts):
        logger.error("convert relative to absolute path error for base path index outof range")
        return
    
    # 根据「.」的数量，组装pwd_parts成一个path，替换掉原有的「.」
    abs_path = path.replace(levels, '/'.join(pwd_parts[:end_index]), -1)
    return abs_path
        