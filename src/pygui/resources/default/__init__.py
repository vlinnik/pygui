import logging,shutil,os
from importlib import resources

def createProject(dest: str):
    logging.info('Generating PYGUI project from DEFAULT template')
    data = resources.files('pygui.resources.default')

    shutil.copy(data.joinpath('example.ui'),f'{dest}/ui/example.ui')    
    shutil.copy(data.joinpath('project.yaml'),f'{dest}/project.yaml')
    shutil.copy(data.joinpath('default.py'),f'{dest}/__main__.py')
