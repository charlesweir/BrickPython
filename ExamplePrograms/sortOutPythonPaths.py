'''
Horrible bit of munging to persuade Python to look for modules on directories above us.
Only necessary when not installed as a package.

See the (last) Sept 10 2012 comment on http://as.ynchrono.us/2007/12/filesystem-structure-of-python-project_21.html 
@author: charles
'''

import sys, os
path = os.path.abspath(sys.argv[0])
while os.path.dirname(path) != path:
    if os.path.exists(os.path.join(path, 'BrickPython', '__init__.py')):
        sys.path.insert(0, path)
        break
    path = os.path.dirname(path)