# localSchedule

python code that creates a schedule, currently made to control a portuguese attorney schedule

## Getting Started

The overall system is made up of several files. The main one is the _frontend_ and will be the one called in order to run the application. The folder icons contains all the icons used in the project.

### Prerequisites

The Project is configured with python 3.9.7 (which is only compatible with pyside6 >= 6.2.2.1)

To confirm that you have them installed and which versions they are, run in the terminal:

```s
python3 -version
pip install pyside6
```

## Execution

Run application:

```s
python3 frontend.py
```

In order to make the application persistent the variable _PATHFILEDIR_ must be changed to a permanent location

## Built With

- [pyside6](https://doc.qt.io/qtforpython/PySide6/QtWidgets/index.html) - Frontend framework;
