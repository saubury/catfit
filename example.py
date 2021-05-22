#! /usr/bin/python2

import time
import sys
from datetime import datetime

EMULATE_HX711=False

threshHold = 1000

referenceUnit_A = 22.839
referenceUnit_B = -1092.8
GPIO_A_DT = 17
GPIO_A_SCK = 27
GPIO_B_DT = 5
GPIO_B_SCK = 6


if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx_a = HX711(GPIO_A_DT, GPIO_A_SCK)
hx_b = HX711(GPIO_B_DT, GPIO_B_SCK)

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx_a.set_reading_format("MSB", "MSB")
hx_b.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(92)
hx_a.set_reference_unit(referenceUnit_A)
hx_a.reset()
hx_a.tare()
print("Tare A done! Add weight now...")

hx_b.set_reference_unit(referenceUnit_B)
hx_b.reset()
hx_b.tare()
print("Tare B done! Add weight now...")


# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
        
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string
        
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        val_a = hx_a.get_weight(GPIO_A_DT)
        val_b = hx_b.get_weight(GPIO_B_DT)
        # print(val_a)

        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        # print "A: %s  B: %s" % ( val_a, val_b )

        if (val_a > threshHold or val_b > threshHold):
            now = datetime.now()
            print('{}    {:,.0f}  {:,.0f}'.format(now.strftime("%d/%m/%Y %H:%M:%S"), val_a, val_b))
        
        hx_a.power_down()
        hx_a.power_up()
        hx_b.power_down()
        hx_b.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
