
from colorama import Fore, init
from sys import platform as sus_platform # какая платформа

# проверка на платформу
if sus_platform == 'win32': init() # инициализируем цвета для Windows