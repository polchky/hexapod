import machine
import servo
import utime

i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))
servos = servo.Servos(i2c)

mind = 800
maxd = 2400
res = 100

while(True):
	for i in range(mind, maxd, res):
		servos.position(0, us=i)
		utime.sleep_ms(100)
	servos.position(0, us=mind)
	utime.sleep(2)
