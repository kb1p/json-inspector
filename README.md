# JSON inspector
A tool for convenient JSON files overview

## Overview
This tool allows to view JSON file structure as a tree.
Allows modification of properties / array element values without changing of the containers' structure.
Convenient for navigation in files containing large arrays of objects referencing each other by index,
which is a common case for 3D models in glTF 2.0 format.

## Requirements
* Python 2.7 or 3.x
* Qt 5
* PyQt5

## Running
1. Install Qt5 & PyQt5. For Ubuntu this can be done as follows:  
`$ sudo apt install qt5-default python-pyqt5`
2. Run main.py:  
`$ python main.py`


