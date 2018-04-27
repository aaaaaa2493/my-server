from sys import executable
from os.path import dirname
from shutil import copyfile
copyfile(f'poker/lib/card.py', f'{dirname(executable)}/site-packages/pokereval/card.py')