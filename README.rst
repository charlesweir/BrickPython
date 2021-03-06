.. README.rst project overview for PyPi
..
.. Check using rst2html.py README.rst README.html

===========
BrickPython
===========

.. image:: https://badge.fury.io/py/BrickPython.png
    :target: http://badge.fury.io/py/BrickPython

.. # image:: https://travis-ci.org/{{ cookiecutter.github_username }}/BrickPython.png?branch=master
        :target: https://travis-ci.org/{{ cookiecutter.github_username }}/BrickPython

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

* Implementation of PID algorithm to make an NXT motor into a servo-motor
* Simple objects representing Motor and different types of Sensor
* Implementation of Python coroutines and scheduler for Python 2.7
* Uses Brickpi.py from BrickPi_python
* Implementation of an NXT motor constant speed algorithm
* Full unit test suite
* Runs on other Linux environments (Mac etc) for unit tests and development.

Changes in v0.4
---------------

* Updated PID algorithm so it's independent of the work cycle time.
  BACKWARDS COMPATIBILITY WARNING: One parameter to the constructor of
  Motor.PIDSetting has changed.

* Added specialized sensor classes: UltrasonicSensor, TouchSensor, LightSensor

* Added useful script for cross-platform testing.
