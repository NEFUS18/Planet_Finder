from RPLCD.gpio import CharLCD
import time
import RPi.GPIO as GPIO
from astroquery.jplhorizons import Horizons

inSetUp = True
planetIndex = 0
stepperPinsAZ = [7,11,13,15]
stepperPinsEL = [40, 38, 36, 32]
selectBtnPin = 33
incBtnPin = 37
decBtnPin = 35
planets = [199, 299, 301, 499, 599, 699, 799, 899, 999]
planetNames = ["Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

def okSelect(channel):
	global planetIndex
	global planets
	global planetNames
	global stepperPinsAZ
	global stepperPinsEL
	if GPIO.input(channel) == GPIO.LOW:
		eph = getPlanetInfo(planets[planetIndex])
		percentageArcAZ = (eph['AZ'][0])/360 
		percentageArcEL = (eph['EL'][0])/360 
		stepsNeededAZ = int(percentageArcAZ*512) 
		stepsNeededEL = int(percentageArcEL*512) 

		lcd.clear()
		lcd.write_string(planetNames[planetIndex])
		lcd.crlf()
		lcd.write_string("AZ " + str(int(eph['AZ'][0])) + " EL " + str(int(eph['EL'][0])))
		time.sleep(1)
		if stepsNeededAZ > 256:
			moveStepperBack(stepperPinsAZ, (512-stepsNeededAZ)) 
		else:
			moveStepper(stepperPinsAZ, stepsNeededAZ) 
		time.sleep(1)
		if stepsNeededEL < 0:
			moveStepperBack(stepperPinsEL, -stepsNeededEL) 
		else:
			moveStepper(stepperPinsEL, stepsNeededEL) 
		time.sleep(8)

		if stepsNeededEL < 0:
			moveStepper(stepperPinsEL, -stepsNeededEL)
		else:
			moveStepperBack(stepperPinsEL, stepsNeededEL)
		time.sleep(1)
		if stepsNeededAZ > 256:
			moveStepper(stepperPinsAZ, (512-stepsNeededAZ)) 
		else:
			moveStepperBack(stepperPinsAZ, stepsNeededAZ) 
		time.sleep(1)
		lcd.clear()
		lcd.write_string(planetNames[planetIndex])

def incSelect(channel):
	global planetIndex
	global planetNames
	if GPIO.input(channel) == GPIO.LOW:
		if planetIndex < 8:
			planetIndex = planetIndex + 1
		lcd.clear()
		lcd.write_string(planetNames[planetIndex])
		time.sleep(1)

def decSelect(channel):
	global planetIndex
	global planetNames
	if GPIO.input(channel) == GPIO.LOW:
		if planetIndex > 0:
			planetIndex = planetIndex - 1
		lcd.clear()
		lcd.write_string(planetNames[planetIndex])
		time.sleep(1)

def increaseAZ(channel):
	if GPIO.input(channel) == GPIO.LOW:
		moveStepper(stepperPinsAZ, 32)

def decreaseAZ(channel):
	if GPIO.input(channel) == GPIO.LOW:
		moveStepperBack(stepperPinsAZ, 32)

def increaseEL(channel):
	if GPIO.input(channel) == GPIO.LOW:
		moveStepper(stepperPinsEL, 32)

def decreaseEL(channel):
	if GPIO.input(channel) == GPIO.LOW:
		moveStepperBack(stepperPinsEL, 32)


def getPlanetInfo(planet):
	obj = Horizons(id=planet, location='L32', epochs=None, id_type='majorbody')
	eph = obj.ephemerides()
	return eph

def moveStepper(axis, stepsNeeded):
	halfstep_seq = [
		[1,0,0,0],
		[1,1,0,0],
		[0,1,0,0],
		[0,1,1,0],
		[0,0,1,0],
		[0,0,1,1],
		[0,0,0,1],
		[1,0,0,1]
	]
	for i in range(stepsNeeded):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(axis[pin], halfstep_seq[halfstep][pin])
			time.sleep(0.002)

def moveStepperBack(axis, stepsNeeded):
	halfstep_seq = [
		[1,0,0,1],
		[0,0,0,1],
		[0,0,1,1],
		[0,0,1,0],
		[0,1,1,0],
		[0,1,0,0],
		[1,1,0,0],
		[1,0,0,0]
	]
	for i in range(stepsNeeded):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(axis[pin], halfstep_seq[halfstep][pin])
			time.sleep(0.002)


GPIO.setmode(GPIO.BOARD)

for pin in stepperPinsAZ + stepperPinsEL:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin,0)

lcd = CharLCD(cols=16, rows=2, dotsize=8, pin_rs=26,  pin_e=24, pins_data=[22, 18, 16, 12], numbering_mode=GPIO.BOARD)
lcd.clear()

GPIO.setup(selectBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(incBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(decBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

startUp()

while True:
	time.sleep(1)
