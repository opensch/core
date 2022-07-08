import os

from .school import *

from .cabinet import *
from .homework import *
from .lesson import *
from .news import *
from .user import *

from .timetable.replacements import *
from .timetable.timetable import *

from .surveys.survey import *
from .surveys.vote import *

# Creating authentication folders if there are none
folders_to_create = ["codes", "tokens", "tokens/access", "tokens/refresh"]

for folder in folders_to_create:
    if os.path.exists(folder) != True:
        os.mkdir(folder)
