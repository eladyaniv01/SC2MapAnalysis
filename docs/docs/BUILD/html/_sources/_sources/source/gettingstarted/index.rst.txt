Getting Started
===============

Installation
############

**you will need to have** `64 bit python <https://www.python.org/downloads/>`_ **installed**

Step 1 - Download and Install
-----------------------------

    *Inside* your bots virtual environment,

    clone the repo into its own directory,

    somewhere outside your bot folders:

    .. code-block:: bash

        git clone https://github.com/eladyaniv01/SC2MapAnalysis.git

        cd SC2MapAnalysis

    And then:

    .. code-block:: bash

        pip install .


    - or if you want to contribute, or run tests locally

    .. code-block:: bash

        pip install -e .[dev]


    - or just with

    .. code-block:: bash

        pip install -r requirements.txt

Step 2 - Folder Structure
-------------------------

    All that is left now, is to grab the ``MapAnalyzer`` folder, and place it in your bot root directory

    Roughly like so:

    | MyBot
    | ├── MapAnalyzer
    | │   ├── ... dependencies for MapAnalyzer
    | │   ├── ...
    | │ ... your bot files and folders here


    In the folder structure above:

    - ``MyBot`` is the folder of your bot
    - ``MapAnalyzer`` is the directory from this repo (MapAnalyzer dir) that you have unpacked in your bot root