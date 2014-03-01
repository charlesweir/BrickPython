===========
BrickPython
===========

.. # image:: https://badge.fury.io/py/{{ cookiecutter.repo_name }}.png
    :target: http://badge.fury.io/py/{{ cookiecutter.repo_name }}

.. # image:: https://travis-ci.org/{{ cookiecutter.github_username }}/{{ cookiecutter.repo_name }}.png?branch=master
        :target: https://travis-ci.org/{{ cookiecutter.github_username }}/{{ cookiecutter.repo_name }}

.. image:: https://pypip.in/d/BrickPython/badge.png
        :target: https://crate.io/packages/BrickPython?version=latest


BrickPython provides an easy Python programming environment for the `BrickPi <http://www.dexterindustries.com/BrickPi/>`_,
making Lego NXT motors behave as servo motors.
The framework provides coroutines to give you always-responsive programs, and objects to help you partition programs.

* Free software: MIT license
* Documentation: https://pythonhosted.org/BrickPython/index.html
* Source code: https://github.com/charlesweir/BrickPython

Features
--------

* Simple objects representing Motor and Sensor
* Implementation of Python coroutines and scheduler for Python 2.7
* Uses Brickpi.py from BrickPi_python
* Implementation of PID algorithm to make NXT motor be a servo-motor
* Implementation of motor constant speed algorithm
* Full unit test suite
* Runs on other Linux environments (Mac etc) for unit tests and development.


.. TODO: Links to Coroutine presentation.
   TODO: Better motivation.
   TODO: Discussion of OS X environment

