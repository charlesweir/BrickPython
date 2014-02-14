#!/usr/bin/python
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)

import setuptools

setuptools.setup(
	name="BrickPython",
	description="Python structure for the BrickPi",
	author="Charles and James Weir",
	url="http://www.charlesweir.com/",
	py_modules=['BrickPython'],
	test_suite='test'
	#install_requires=open('requirements.txt').readlines(),
)
