"""
chango.py

     Test for font2bitmap converter for a GC9A01 display
    connected to a Raspberry Pi Pico.

    Pico Pin   Display
    =========  =======
    14 (GP10)  BL
    15 (GP11)  RST
    16 (GP12)  DC
    17 (GP13)  CS
    18 (GND)   GND
    19 (GP14)  CLK
    20 (GP15)  DIN
"""

from machine import Pin, SPI, I2C, Timer
import gc9a01
import time
import NotoSerif_32 as thefont
import btnY, btnG, btnR, btnB 
import mpr121

kbrd_evnt = False
prgrsTick = False
clockTick = False

def PRGRScallback(t):
	global prgrsTick
	prgrsTick = True
	
def CLOCKcallback(t):
	global clockTick
	clockTick = True

def keypad_handler(pin):
	global kbrd_evnt
	kbrd_evnt = True
	
def main():
	spi = SPI(1, baudrate=60000000, sck=Pin(14), mosi=Pin(15))
	tft = gc9a01.GC9A01(
		spi,
		240,
		240,
		reset=Pin(11, Pin.OUT),
		cs=Pin(13, Pin.OUT),
		dc=Pin(12, Pin.OUT),
		backlight=Pin(10, Pin.OUT),
		rotation=0)  
        
	i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)
	mpr = mpr121.MPR121(i2c)
	
	progrs_timer = Timer()
	clock_timer = Timer()
	progrs_timer.init(mode=Timer.PERIODIC, period=100, callback=PRGRScallback)
	clock_timer.init(mode=Timer.PERIODIC, period=1000, callback=CLOCKcallback)
	
	led = Pin(25, Pin.OUT)
	keypad_pressed = Pin(18, Pin.IN, Pin.PULL_UP)
	keypad_pressed.irq(trigger= Pin.IRQ_FALLING, handler=keypad_handler)      		
    
    # enable display and clear screen
	tft.init()
	tft.fill(gc9a01.BLACK)

	edgeRectWidth = 20	
	prgrsBgClor = 0x380    
	prgrsFgClor = 0x5e0
	prgrsClor = prgrsFgClor    
	prgrs = range(40,200,5)    
	prgrsIndx = 0
	prgrsStep = 1
	progress = prgrs[prgrsIndx] 

	timer_start = 0  
	timer_duration = 0
	keypad_key = 100000 
	try:
		global kbrd_evnt
		global prgrsTick
		global clockTick
	except Exception as e:
		print(e)
	clockTurn = 0	
	clockColors = [0x055, 0xe000, 0xa5a5, 0x0000]
	clocktim = 10
	
	tft.fill_rect(40,180,160,15, prgrsBgClor)						# progress bar bg
    
	tft.bitmap(btnG, 160, 40)
	tft.bitmap(btnR, 160, 100)
    
	while True:
		if kbrd_evnt == True:
			kbrd_evnt = False
			temp = mpr.touched()    		
			if temp == 0:
				timer_duration = time.ticks_diff(time.ticks_ms(), timer_start)
				if timer_duration > 100:
					if keypad_key == 32:
						tft.bitmap(btnY, 160, 40)
						tft.bitmap(btnB, 160, 100)						
					if keypad_key == 64:
						tft.bitmap(btnR, 160, 40)
						tft.bitmap(btnY, 160, 100)
					if keypad_key == 128:
						tft.bitmap(btnG, 160, 40)
						tft.bitmap(btnR, 160, 100)
					if keypad_key == 16:
						tft.bitmap(btnB, 160, 40)
						tft.bitmap(btnG, 160, 100)
					keypad_key = 100000        		
			else:
				timer_start = time.ticks_ms()
				keypad_key = temp  	
		
		if prgrsTick == True:
			prgrsTick = False
			progress = prgrs[prgrsIndx]
			prgrsIndx += prgrsStep
			tft.fill_rect(progress,180,5,15,prgrsClor)			
			if prgrsIndx == len(prgrs):
				prgrsStep = -1
				prgrsIndx -= 1
				prgrsClor = prgrsBgClor	    							    	    	   
			if prgrsIndx == -1:
				prgrsStep = 1
				prgrsIndx = 0
				prgrsClor = prgrsFgClor
			
		if clockTick == True:
			clockTick = False			
			if clockColors[0] != 0xa5a5:
				tft.fill_rect(0,240-edgeRectWidth,240,edgeRectWidth,clockColors[0])	# bottom arc
			if clockColors[1] != 0xa5a5:
				tft.fill_rect(0,0,edgeRectWidth,240,clockColors[1])					# left arc
			if clockColors[2] != 0xa5a5:
				tft.fill_rect(0,0,240,edgeRectWidth,clockColors[2])					# top arc		
			if clockColors[3] != 0xa5a5:				
				tft.fill_rect(240-edgeRectWidth,0,edgeRectWidth,240,clockColors[3])	# right arc 
			tempcolor = clockColors[1]
			clockColors[1] = clockColors[0]
			clockColors[0] = clockColors[3]
			clockColors[3] = clockColors[2]
			clockColors[2] = tempcolor					
			tft.write(thefont, "11", 40, 120, 0x0000)
			tft.write(thefont, str(clocktim), 40, 120, 0xece0)	
			clocktim -= 1	
			if clocktim == -1:
				clocktim = 10			

main()
