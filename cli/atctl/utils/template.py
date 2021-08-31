

import base64
from loguru import logger
import os
import binascii
import yaml



class Template:
    def __init__(self, source: str) -> None:
        self.data = yaml.load(source, Loader=yaml.CLoader)
    
    def init(self, rootName=None):
        root_dir_name = self.data.get('rootName')
        if rootName is not None:
            root_dir_name = rootName
        root_dir_path = f"{os.getcwd()}/{root_dir_name}"
        filename_list = self.data.get('fileList')
        sub_dirs = self.data.get('subDir')
        if not self.generate_dir(root_dir_path):
            return False
        if len(filename_list) > 0:
            for fileobj in filename_list:
                filename = fileobj.get('name')
                content = fileobj.get('content')
                file_path = f"{root_dir_path}/{filename}"
                if not self.generate_file(file_path, content):
                    return False
        if len(sub_dirs) > 0:
            for sub in sub_dirs:
                sub_dir_path = f"{root_dir_path}/{sub.get('relativePath')}"
                if not self.generate_dir(sub_dir_path):
                    return False
                file_list = sub.get('fileList')
                if len(file_list) > 0:
                    for file_obj in file_list:
                        file_path = f"{sub_dir_path}/{file_obj.get('name')}"
                        content = file_obj.get('content')
                        if not self.generate_file(file_path, content):
                            return False
        return True
                        
    
    def generate_dir(self, dir_path)-> bool:
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"mkdir {dir_path} failed")
            logger.error(e)
            return False
    
    def generate_file(self, path, content)-> bool:
        try:
            if content is None:
                file_data = ""
            else:
                file_data = base64.b64decode(content).decode('utf-8')
            with open(path, 'w') as file:
                file.write(file_data)
            return True
        except binascii.Error  as e:
            logger.error(f"decode file content failed")
            logger.error(e)
            return False
        
    
    