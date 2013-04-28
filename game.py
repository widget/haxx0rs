#!/usr/bin/env python

import argparse
import curses
import curses.textpad
import datetime
import PyV8
import textwrap
import threading
import time

class FakeDocument(PyV8.JSClass):
	def getElementById(self, id):
		return None

class FakeBrowserContext(PyV8.JSClass):
	document = FakeDocument()

class StatusWindow(threading.Thread):
	def __init__(self, y, x):
		self.win = curses.newwin( y, x, 0,0)
		self.percentage = 0
		self.endtime = datetime.datetime.now()
		self.running = True
		threading.Thread.__init__(self)

	def __del__(self):
		self.running = False
		self.join()
	
	def remaining(self):
		rem = self.endtime - datetime.datetime.now()
		if rem < datetime.timedelta(0):
			rem = datetime.timedelta(0)
		return rem

	def set_duration(self, duration):
		self.endtime = datetime.datetime.now() + datetime.timedelta(0, duration)
		self.start()
		#self.timer = threading.Thread(target=self.draw_thread, args=self)
		#self.timer.start()
	
	def run(self):
		while self.remaining().seconds > 0 and self.running:
			time.sleep(0.25)
			self.draw()

	def set_progress(self, perc):
		if perc > 100:
			self.percentage = 100
		elif perc < 0:
			self.percentage = 0
		else:
			self.percentage = perc

	def draw(self):
		pad = 5
		tmp, length = self.win.getmaxyx()
		length -= pad*4
		sec = self.remaining().seconds
		timeStr = "%02d:%02d" % (sec / 60, sec % 60)
		mystrOn = (self.percentage*length/100)*' '
		mystrOff = (((100-self.percentage)*length)/100)*' '
		self.win.addstr(2, pad, mystrOn, curses.color_pair(2))
		self.win.addstr(2, pad+len(mystrOn), mystrOff, curses.color_pair(3))
		self.win.addstr(2, (pad*2)+length, timeStr)
		self.win.refresh()


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


def game(stdscr, score_aim, duration):
	cury, curx = stdscr.getmaxyx()
	histheight = (cury-3)/2
	status = StatusWindow(5, curx)
	history = curses.newwin(histheight, curx, 3, 0)
	history.scrollok(1)
#	history.border()
	console = curses.newwin(histheight, curx, 3+histheight, 0)
	console.attrset(curses.color_pair(1)) # leet writings!
	editbox = curses.textpad.Textbox(console)

	history.addstr("JS here")
	history.refresh()
	var = 0
	status.set_duration(duration)
	ret = False
	try:
		while var < score_aim and status.remaining().seconds > 0:
			status.set_progress(var*100/score_aim)
			#status.draw()
			editbox.edit()
			txt = editbox.gather()
			if len(txt) > 0:
				txt_score = testCode(txt)
				var += txt_score
				addHistory(history, txt, txt_score)
			console.erase()

		if var >= score_aim:
			ret = True
	except KeyboardInterrupt:
		stdscr.getch() # eat the ctrl-c
	finally:
		status.running = False
		status.join()
	
	return ret

LEVELS = [ \
	(10, 120),
	(20, 120),
	(30, 90),
	(40, 90),
	(50, 60)
		]

class Popup(object):
	def __init__(self, scr, title, msg):
		self.title = title
		scr.erase()
		scr.refresh()
		self.cury, self.curx = scr.getmaxyx()
		self.msg = textwrap.wrap(msg, (self.curx/2)-3)

	def show(self):
		win = curses.newwin(self.cury/2, self.curx/2, self.cury/4, self.curx/4)
		win.border()
		win.addstr(2, 2, self.title)
		for n, line in enumerate(self.msg):
			win.addstr(4+n, 2, line)
		win.refresh()
		win.getch()


def main(stdscr, args):
	stdscr.keypad(1)
	curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_GREEN)
	curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_RED)
	curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

	intro = Popup(stdscr, "TOP SECRET","""Gain access to this system by typing snippets of Javascript, like proper hackers.  Press Ctrl-G to send each snippet to the vulnerable computer.

	Ctrl-C to quit.
	""")
	intro.show()
	msg = "I don't know why that happened"
	alive = True
	level = args.level
	score = 0
	try:
		while alive and level < len(LEVELS):
			info = Popup(stdscr, "Level %d" % (level+1), "Score %d points in %d seconds.  Press any key to start" % LEVELS[level])
			info.show()
			alive = game(stdscr, *LEVELS[level])
			if alive:
				score += LEVELS[level][0]
			level += 1
	except KeyboardInterrupt:
		msg = "Given up, eh?"
		stdscr.getch() # eat the ctrl-c
	outro = Popup(stdscr, "Finished", msg)
	outro.show()

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Hollywood hacker simulation - write Javascript to pwn")
	parser.add_argument("-l", "--level", default=1, type=int)
	try:
		args = parser.parse_args()
		args.level -= 1
		if not 0 <= args.level < len(LEVELS):
			raise ValueError("Invalid level selection.  Choose 1-%d" % len(LEVELS)+1)
		curses.wrapper(main, args)
	except ValueError as e:
		print e
		parser.print_help()

