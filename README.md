haxx0rs
=======

Ludum Dare #26 candidate - a Hollyword hacking simulator, in ncurses

The aim of the game is to hack into a computer by typing Javascript, just like they do in films.  A big progress bar at the top of the screen lets you know how you're doing.  There's also an arbitrary time limit, just like they do in films.

The V8 engine is used to evaluate the Python being written, and creates a blank context which is reused between snippets entered.  Snippets can contain newlines, and are sent to the "vulnerable computer" by pressing Ctrl-G.  Some other Emacs keybindings are available.

Dependencies
------------

Currently this has an annoying set of dependencies:

	1. `apt-get install libboost-python-dev python-dev python-pip subversion`
	1. `pip install pyv8`

Running
-------

	python game.py

TODO
----

1. Make this more fun
1. Reward more complex snippets (search for keywords, perhaps)
1. Mock out a browser environment, with standard document, console, those sort of bits?
