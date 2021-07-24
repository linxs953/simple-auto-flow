import click
from atctl.utils.case import HarCase, YamlCase
from atctl.common import *
from atctl.templates.project import projectTemplate
from atctl.utils.template import Template

@click.group()
def atctl():
    pass

@atctl.command()
@click.option("-s", help="yaml / har file path")
@click.option("-o", help="file store path after convert")
@click.option("-yaml", is_flag=True, help="convert yaml file", default=False)
@click.option("-har", is_flag=True, help="convert har file", default=False)
def convert(s, o, yaml, har):
    if s == "" or o == "":
        logging.error("source file path and output file path can not be empty")
        exit(1)
    
    if yaml and har:
        logging.error("-y and -har is alternative")
        exit(1)
    
    if not yaml and not har:
        logging.error("not assgin file type , such -y or -har")
        exit(1)
    
    if yaml:
        file_type = "yaml"
    if har:
        file_type = "har"
    
    if not s.startswith(".") and not s.startswith("/"):
        s = f"/{s}"
    if not o.startswith(".") and not o.startswith("/"):
        o = f"/{o}"
    
    output_full_path = convert_relative_path(o)
    source_full_path = convert_relative_path(s)

    if not os.path.exists(output_full_path) \
            or not os.path.exists(source_full_path):
        logging.error("source file or output file path not exist")   
        exit(1)
    
    if not os.path.isdir(output_full_path):
        logging.error("output path must be dir")
        exit(1)
    
    if is_file(source_full_path):
        if source_full_path.split('.')[1] != file_type:
            logging.error(f"file type -> {source_full_path.split('.')[1]} but assign -{file_type}") 
            exit(1)
        output_file_path = f"{output_full_path}{source_full_path.split('/')[-1].replace(file_type,'py',-1)}"
        if yaml:
            case = YamlCase(source_full_path, output_file_path)

        if har:
            case = HarCase(source_full_path, output_file_path)
        
        case.run()
        return
    
    #  list all yaml file and covert it to python case
    for p in os.listdir(source_full_path):
        file_full_path = f"{source_full_path}{p}"
        output_file_path = f"{output_full_path}{p.replace(file_type,'py',-1)}"
        if har:
            if "har" not  in p:
                continue
            case = HarCase(file_full_path, output_file_path)
        if yaml:
            if "yaml" not in p:
                continue
            case = YamlCase(file_full_path, output_file_path)
        case.run()
    return

@atctl.command()
@click.argument("projectname", required=False, default=None)
def start_project(projectname):
    click.echo("start new project")
    '''
    todo：project.yaml 验证
    1. 读取project.yaml，获取项目结构信息
    2. 通过relativePath创建目录和文件
    '''

    template = Template(projectTemplate)
    if not template.init(projectname):
        exit(1)
        