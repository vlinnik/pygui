import logging,shutil,os
from importlib import resources

def createProject(dest: str):
    logging.info('Generating PYGUI project from DEFAULT template')
    data = resources.files('pygui.templates.default')

    shutil.copy(data.joinpath('gui.yaml'),f'{dest}/resources/gui.yaml')
    shutil.copy(data.joinpath('gui.py'),f'{dest}/__main__.py')
    shutil.copy(data.joinpath('example.ui'),f'{dest}/resources/ui/example.ui')    