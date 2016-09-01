#!/usr/bin/env python

"""Here we load a .TTF font file, and display it in
a basic pygame window. It demonstrates several of the
Font object attributes. Nothing exciting in here, but
it makes a great example for basic window, event, and
font management."""


import pygame
from pygame.locals import *
from pygame.compat import unichr_, unicode_
import sys
import locale
import websocket_eeg
import websocket
import Queue
import threading


window_size = 800

if sys.version_info >= (3,):
	def print_unicode(s):
		e = locale.getpreferredencoding()
		print (s.encode(e, 'backslashreplace').decode())
else:
	def print_unicode(s):
		e = locale.getpreferredencoding()
		print (s.encode(e, 'backslashreplace'))

event_queue = Queue.Queue()

def on_message(w, m):

	websocket_eeg.on_message(w, m)

	c = dict(websocket_eeg.lastdif)
	


	sig = 1.8
	hisig = 2.6
	
	if c['e2']>hisig and c['e3']>hisig and c['c1'] * -1 > hisig and c['c2'] * -1 > hisig:
		event="Startled"
	elif c['e1']>sig:
		event="Excited"
	elif c['c1']>sig:
		event="Concentrated"
	elif c['c1'] * -1 > sig:
		event="Distracted"
	elif c['h1']>sig or c['h2']>sig:
		event="Happy"
#	elif c['h1'] * -1 > sig or c['h2'] * -1 > sig:
#		event="Sad"
	else:
		event=""



	message = { 'raw_data' : websocket_eeg.data[-1],
				'change' : dict(websocket_eeg.lastdif),
				'event' : event }
#	print "adding to queue"
##	print message
	event_queue.put(message)
	

def websocket_thread():
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("ws://cloud.neurosteer.com:8080/v1/features/0006664e5c1a/pull",
								on_message = on_message,
								on_error = websocket_eeg.on_error,
								on_close = websocket_eeg.on_close)
#	ws.on_open = on_open

	ws.run_forever()


fields = ['c1','c2','c3','h1','h2','e1','e2','e3']
hues = [0, 20, 40, 100, 130, 230,250,270]

def check_mood_event(c):
	sig = 1.8
	hisig = 2.6
	
	if c['e2']>hisig and c['e3']>hisig and c['c1'] * -1 > hisig and c['c2'] * -1 > hisig:
		event="Startled"
	elif c['e1']>sig:
		event="Excited"
	elif c['c1']>sig:
		event="Concentrated"
	elif c['c1'] * -1 > sig:
		event="Distracted"
	elif c['h1']>sig or c['h2']>sig:
		event="Happy"
#	elif c['h1'] * -1 > sig or c['h2'] * -1 > sig:
#		event="Sad"
	else:
		event=""
	
	if event != "":
		print "******",event,"******"	

def update_bars(msg):
#	print 'updating bars'
	if len(msg['change']) != 0:
		changes = [msg['change'][field] for field in fields]
#		print "Changes: ", changes
		check_mood_event(msg['change'])
	else:
		changes = [None]*len(fields)

	bars = zip(fields, hues, [msg['raw_data'][field] for field in fields], changes)	
	return bars		
		
def draw_bars(screen,bars,event):
	if len(bars) == 0 or bars[0][3] is None: return
#	print 'drawing bars'
	width = float(window_size) / len(bars)
	scale = window_size/40
	for index, (name, hue, value, change) in enumerate(bars):
#		print index,name,value
		col = pygame.Color(0)
		col.hsva = (hue, 100, 100, 100)
		y = window_size/2 if change < 0 else window_size/2-change*scale
		
		screen.fill(col, (index*width,y,width, abs(change*scale)))
		
		title_size = font.size(name)
		ren = font.render(name, 0, (250,240, 230))
		y = 10
		screen.blit(ren,(index*width,y))
		y += title_size[1] + 10
		ren = font.render("{:.2f}".format(change), 0, (250,240, 230))
		screen.blit(ren,(index*width,y))

		y = window_size - 150 - title_size[1]
		ren = font.render(event, 0, (250,240, 230))		
		screen.blit(ren,(350,y))
		
		y = window_size - 10 - title_size[1]
		ren = font.render(str(value), 0, (250,240, 230))		
		screen.blit(ren,(index*width,y))



font = None

def main():
	global font
	#initialize
	clock = pygame.time.Clock()
	pygame.init()
	resolution = window_size, window_size
	screen = pygame.display.set_mode(resolution)

##	pygame.mouse.set_cursor(*pygame.cursors.diamond)

	#launch websocket thread
	ws_thread = threading.Thread(target=websocket_thread)
	ws_thread.start()

	fg = 250, 240, 230
	bg = 5, 5, 5
	wincolor = 40, 40, 90

	#fill background
	screen.fill(wincolor)
#	print 'loading first font'
	#load font, prepare values
	font = pygame.font.Font(None, 32)
	text = 'Fonty'
	size = font.size(text)

	#no AA, no transparancy, normal
	ren = font.render(text, 0, fg, bg)
	screen.blit(ren, (10, 10))

	#no AA, transparancy, underline
	font.set_underline(1)
	ren = font.render(text, 0, fg)
	screen.blit(ren, (10, 40 + size[1]))
	font.set_underline(0)

	#show the surface and await user quit
	pygame.display.flip()
	
	done = 0
	bars = []
	while not done:
		event=""
		try:
			message = event_queue.get_nowait()
			bars = update_bars(message)
			event = message['event']
		except Queue.Empty:
			pass
		#update_bars()
		screen.fill(0)
		draw_bars(screen, bars,event)
		pygame.display.update()
		for e in pygame.event.get():
			if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
#				done = 1
				break
#			elif e.type == MOUSEBUTTONDOWN and e.button == 1:
#				WINCENTER[:] = list(e.pos)
		clock.tick(50)
		



if __name__ == '__main__': main()
	
