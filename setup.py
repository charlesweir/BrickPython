#!/usr/bin/python
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)

# import setuptools
#
# setuptools.setup(
# 	name="BrickPython",
# 	description="Python structure for the BrickPi",
# 	author="Charles and James Weir",
# 	url="http://www.charlesweir.com/",
# 	py_modules=['BrickPython'],
# 	test_suite='test'
# 	#install_requires=open('requirements.txt').readlines(),
# )

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import codecs
import os
import sys
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README.rst')

setup(
    name='BrickPython',
    version=find_version('BrickPython', '__init__.py'),
#     url='http://github.com/jeffknupp/sandman/',
    license='Apache Software License',
    author='Charles Weir',
    tests_require=['pytest'],
    install_requires=[],
#     cmdclass={'test': PyTest},
    author_email='charles@penrillian.com',
    description='Python interface for the BrickPi using Objects and Coroutines',
    long_description=long_description,
    entry_points={
        },
    packages=['BrickPython', 'ExamplePrograms','test'],
    include_package_data=True,
    platforms='any',
    test_suite='test',
    zip_safe=False,
#     package_data={'BrickPython': ['templates/**', 'static/*/*']},
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
#        'Environment :: Raspberry Pi',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
        ],
    extras_require={
        'testing': ['pytest', 'mock'],
      },
	#install_requires=open('requirements.txt').readlines()  # It doesn't need it for Mac.
)