#!/usr/bin/env python

import curses
import curses.textpad
import PyV8
import textwrap

class FakeDocument(PyV8.JSClass):
	def getElementById(self, id):
		return None

class FakeBrowserContext(PyV8.JSClass):
	document = FakeDocument()

stdscr = curses.initscr()

def draw_progress(win, perc):
	pad = 5
	tmp, length = win.getmaxyx()
	length -= pad*2
	if perc > 100:
		perc = 100
	if perc < 0:
		perc= 0
	mystrOn = (perc*length/100)*' '
	mystrOff = (((100-perc)*length)/100)*' '
	win.addstr(2, pad, mystrOn, curses.color_pair(2))
	win.addstr(2, pad+len(mystrOn), mystrOff, curses.color_pair(3))
	win.refresh()


def testCode(string):
	with PyV8.JSContext(FakeBrowserContext()) as ctxt:
		score = 0
		try:
			ctxt.eval(string)
			# Score calculation, we need to score higher for:
			# * length
			# * use of fancy constructs?
			score = 1 + len(string)/20
		except (ReferenceError, SyntaxError):
			pass # for the moment?
	
	return score


def addHistory(win, txt, score):
	# colour code to indicate points scored
	try:
		attr = 0
		if score > 5:
			attr = curses.color_pair(1)
		elif score == 0:
			attr = curses.color_pair(4)
		win.addstr(txt, attr)
	except curses.error:
		win.clear()
		win.border()
		win.addstr(txt)
	win.refresh()


def game(stdscr):
	cury, curx = stdscr.getmaxyx()
	histheight = (cury-3)/2
	status = curses.newwin( 5, curx, 0,0)
	history = curses.newwin(histheight, curx, 3, 0)
	history.scrollok(1)
#	history.border()
	console = curses.newwin(histheight, curx, 3+histheight, 0)
	console.attrset(curses.color_pair(1)) # leet writings!
	editbox = curses.textpad.Textbox(console)

	history.addstr("JS here")
	history.refresh()
	var = 0
	while var < 100:
		draw_progress(status, var)
		editbox.edit()
		txt = editbox.gather()
		if len(txt) > 0:
			txt_score = testCode(txt)
			var += txt_score
			addHistory(history, txt, txt_score)
		console.erase()
		

def intro(stdscr):
	cury, curx = stdscr.getmaxyx()
	stdscr.erase()
	stdscr.refresh()

	rawmsg = """Gain access to this system by typing snippets	of Javascript, like proper hackers.  Press Ctrl-G to send each snippet
	to the vulnerable computer.

	Ctrl-C to quit.
	"""
	msg = textwrap.wrap(rawmsg, (curx/2)-3)
	
	win = curses.newwin(cury/2, curx/2, cury/4, curx/4)
	win.border()
	win.addstr(2, 2, "TOP SECRET - EYES ONLY")
	for n, line in enumerate(msg):
		win.addstr(4+n, 2, line)
	win.refresh()
	win.getch()


def outro(stdscr, msg):
	cury, curx = stdscr.getmaxyx()
	stdscr.erase()
	stdscr.refresh()
	
	win = curses.newwin(cury/2, curx/2, cury/4, curx/4)
	win.border()
	win.addstr(2,2, msg)
	win.refresh()
	win.getch()


def main(stdscr):
	stdscr.keypad(1)
	curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_GREEN)
	curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_RED)
	curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

	intro(stdscr)
	msg = "I don't know why that happened"
	try:
		game(stdscr)
	except KeyboardInterrupt:
		msg = "Given up, eh?"
		stdscr.getch() # eat the ctrl-c
	outro(stdscr, msg)

if __name__ == "__main__":
		curses.wrapper(main)