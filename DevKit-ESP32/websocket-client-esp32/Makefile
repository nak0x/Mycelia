PROJECT_NAME := template-project
PORT ?= /dev/cu.usbserial-0001
BAUD ?= 115200

config:
	idf.py set-target esp32

all:
	idf.py build

flash:
	idf.py -p $(PORT) -b $(BAUD) flash

monitor:
	idf.py -p $(PORT) monitor

flash-monitor:
	idf.py -p $(PORT) flash monitor

clean:
	idf.py clean

