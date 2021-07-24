import logging
import os


def is_dir(path):
    if not os.path.exists(path):
        logging.error(f"{path} not exists")
        return False
    
    return os.path.isdir(path)

def is_file(path):
    if not os.path.exists(path):
        logging.error(f"{path} not exists")
        return False
    
    return os.path.isfile(path)

def convert_relative_path(path,base=None)-> str:
    pwd = os.getcwd()
    if base is not None:
        pwd = base
    pwd_parts = pwd.split("/")
    levels = path.split("/")[0]
    if len(levels) <= 1:
        if path.split("/")[0] == ".":
            abs_path = path.replace(".", pwd)
            return abs_path
        abs_path = f"{pwd}{path}"        
        return abs_path
    end_index = len(pwd_parts) - len(levels) + 1
    if end_index >= len(pwd_parts):
        logging.error("convert relative to absolute path error")
        return
    abs_path = path.replace(levels, '/'.join(pwd_parts[:end_index]), -1)
    return abs_path
        