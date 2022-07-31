import os

from .replacement import *
from .cabinet import *
from .homework import *
from .lesson import *
from .news import *
from .user import *
from .school import *

# Creating authentication folders if there are none
folders_to_create = ["codes", "tokens", "tokens/access", "tokens/refresh"]

for folder in folders_to_create:
    if os.path.exists(folder) != True:
        os.mkdir(folder)
