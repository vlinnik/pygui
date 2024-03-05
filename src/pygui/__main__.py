import logging,os,importlib,shutil,re
import argparse,importlib.resources as resources

logging.info(f'PYGUI project generator')

parser = argparse.ArgumentParser(
                    prog='PYGUI Project generator tool',
                    description='Генерирует скелет проекта по шаблонам',
                    epilog='Пример: python -m pygui --template default')

parser.add_argument('destination',action='store',default='./',help='Путь где создать проект')
parser.add_argument('-t','--template',choices=['default'],default='default',help='Какой шаблон приложения использовать')
#parser.add_argument('-d','--destination',action='store',default='./',help='Путь где создать проект')
parser.add_argument('-p','--package',action='store',required=True,help='Имя проекта')
parser.add_argument('-u','--user',action='store',default='<your_name>')
parser.add_argument('-m','--mail',action='store',default='<your@mail>')
parser.add_argument('-l','--homepage',action='store',default='<project homepage>')

args = parser.parse_args()

template = importlib.__import__(f'pygui.resources.{args.template}',fromlist=['createProject'])

package_dir = f'{args.destination}/src/{args.package}/' 
project_dir = f'{args.destination}/' 
os.makedirs(f'{package_dir}/resources/ui',exist_ok = True )

data = resources.files('pygui.resources')
for f in ['LICENCE','README.md']:
    shutil.copy(data.joinpath(f),f'{project_dir}/{f}')
shutil.copy(data.joinpath('default.scada'),f'{package_dir}/resources/default.scada')

with open(f'{project_dir}/pyproject.toml','w') as output:
    content = data.joinpath('pyproject.toml').read_text()
    var = re.compile(r'\${([^}]+)}')
    env=vars(args)

    for m in re.findall(var,content):
        what = '\${' + f'{m}' + '}'
        content = re.sub(what,env[m] if m in env else f'<{m} not set>',content)
    output.write(content)

template.createProject(package_dir)