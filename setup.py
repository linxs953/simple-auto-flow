import sys
from base.yaml2code import *
import os
import logging


logging.basicConfig(level = logging.INFO)

base_dir = os.getcwd()

def run(path: list, output: str):
    # 获取path下所有以yaml开头的文件
    if not os.path.exists(path) or not os.path.exists(output):
        logging.error(f"path `{path}` or `{output}` not exists")        
        exit(1)
    
    if not path.endswith("/"):
        path = path + "/"
    
    if not output.endswith("/"):
        output = output + "/"
    
    fileList = os.listdir(path)
    for filename in fileList:
        fileFullPath = f"{path}{filename}"
        # 如果文件不存在
        if not os.path.exists(fileFullPath):
            exit(1)
        # 筛选所有以test_开头的yaml文件
        if "." in filename and filename.split(".")[1] == "yaml" and "test_" in filename.split(".")[0]:
            case = YamlCase(source=fileFullPath,output=f"{output}{filename.replace('yaml','py',-1)}")
            case.run()
    



if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("required arg for sourcefile path and outputfile path")
        exit(1)
    run(f"{base_dir}/{sys.argv[1]}",f"{base_dir}/{sys.argv[2]}")