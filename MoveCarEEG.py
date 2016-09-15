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
import serial

bluetoothComPort = 'COM7'
ser = serial.Serial(
    port=bluetoothComPort,
    baudrate=115200,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

def MoveCar(Concenteration1,Concenteration2):
    if not ser.isOpen():
        try:        
            ser.open()        
        except:           
            return
    try:
        ser.write("mot {0},{1}\r".format(ConvertConsentrationToMotorValues(Concenteration1),ConvertConsentrationToMotorValues(Concenteration2)).encode())        
    except:
        return

def ConvertConsentrationToMotorValues(concentration):
    return concentration * 60 if concentration > 0 else 0

event_queue1 = Queue.Queue()
event_queue2 = Queue.Queue()

def on_message(w, m):
	websocket_eeg.on_message(w, m)
	c = dict(websocket_eeg.lastdif)
	if w.__doc__ == 1:
          event_queue1.put(c['c1'])
        else:
          event_queue2.put(c['c1'])
      
def websocket_thread():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(adressEEG,
						on_message = on_message,
						on_error = websocket_eeg.on_error,
						on_close = websocket_eeg.on_close) 
#	ws.on_open = on_open
    ws.run_forever()    

adressEEG1 = "ws://cloud.neurosteer.com:8080/v1/features/0006664e5c1a/pull"
adressEEG2 = "ws://cloud.neurosteer.com:8080/v1/features/0006664e5c1a/pull"

def main():
	#initialize
	clock = pygame.time.Clock()
	
	#launch websocket thread
        adressEEG = adressEEG1
        ws_thread1 = threading.Thread(target=websocket_thread)
        ws_thread1.__doc__ = 1
        ws_thread1.start()
        adressEEG = adressEEG2
        ws_thread2 = threading.Thread(target=websocket_thread)
        ws_thread2.__doc__ = 2
        ws_thread2.start()
	
	done = 0	
	while not done:		
		try:
                 player1Concentration = event_queue1.get_nowait()
                 player2Concentration = event_queue2.get_nowait()
                 MoveCar(player1Concentration,player2Concentration)
		except Queue.Empty:
			pass
		clock.tick(50)		

if __name__ == '__main__': main()
