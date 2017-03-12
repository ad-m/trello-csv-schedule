===============================
trello-csv-schedule
===============================

.. image:: https://badge.fury.io/py/trello-csv-schedule.png
    :target: http://badge.fury.io/py/trello-csv-schedule

Tools to two-way sync Trello & CSV to easily manage due date.

Features
=========

* Manage Trello access credentials
* Download cards of boards to CSV file
* Sync changes of due date in CSV to Trello board

Usage
=====

There is a build-in ``--help`` command.

Firstly you have to setup tools to provide access keys. It simple as::

    trello-csv-schedule.py setup --key="XXXX"

``XXXX`` mean access key of Trello. You can grab them at `Trello developers site <https://trello.com/app-key>`_.

Next to download boards to CSV file::

    trello-csv-schedule.py download link grab.csv

``link`` mean link to Trello boards. 

Next to you can modify ``grab.csv`` and upload changes to Trello board::
    
    trello-csv-schedule.py sync link grab.csv


For details see at ``--help`` command output too::

    $ python trello-csv-schedule.py --help
    usage: trello-csv-schedule.py [-h] [-g GLOBAL] {sync,download,setup} ...

    positional arguments:
      {sync,download,setup}
        sync                Import cards from file
        download            Export cards to file
        setup               Perform a initial configuration of tool

    optional arguments:
      -h, --help            show this help message and exit
      -g GLOBAL, --global GLOBAL
    $ python trello-csv-schedule.py setup --help
    usage: trello-csv-schedule.py setup [-h] -k KEY

    optional arguments:
      -h, --help         show this help message and exit
      -k KEY, --key KEY
    $ python trello-csv-schedule.py download --help
    usage: trello-csv-schedule.py download [-h] board file

    positional arguments:
      board       ID or URL of board
      file        Filename of file to write cards

    optional arguments:
      -h, --help  show this help message and exit
    $ python trello-csv-schedule.py sync --help
    usage: trello-csv-schedule.py sync [-h] board file

    positional arguments:
      board       ID or URL of board
      file        Filename of file with cards

    optional arguments:
      -h, --help  show this help message and exit
