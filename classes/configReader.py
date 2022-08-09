import sys

sys.path.append("..")

try:
    from config import Config
except ModuleNotFoundError:
    from classes.simpleConfig import Config