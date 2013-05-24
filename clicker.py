#!/usr/bin/python

import RPi.GPIO as GPIO
from multiprocessing import Process
import time


class Clicker:

    B_CHAN_1 = 11
    B_CHAN_2 = 13
    L_CHAN_1 = 16
    L_CHAN_2 = 18

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

    def start_working(self):
        b_coffee = Button(Clicker.B_CHAN_1, Clicker.L_CHAN_1, self.coffee_f)
        b_sandwich = Button(Clicker.B_CHAN_2, Clicker.L_CHAN_2, self.sandwich_f)
        b_list = [b_coffee, b_sandwich]
        for b in  b_list:
            b.start()
        for b in  b_list:
            b.join()

    def coffee_f(self):
        print("coffee")

    def sandwich_f(self):
        print("sandwich")


class Button:

    def __init__(self, channel, led_pin, f):
        self.channel = channel
        self.f = f
        self.led_pin = led_pin
        self.p = Process(target=self.target_f)
        GPIO.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.led_pin, GPIO.OUT, initial=GPIO.LOW)

    def target_f(self):
        while True:
            counter = 0
            while counter < 4:
                if GPIO.input(self.channel) == GPIO.HIGH:
                    if counter > 0:
                        counter -= 1
                else:
                    counter += 1
            time.sleep(0.05)
            GPIO.wait_for_edge(self.channel, GPIO.RISING)
            GPIO.output(self.led_pin, GPIO.HIGH)
            self.f()
            time.sleep(1)
            GPIO.output(self.led_pin, GPIO.LOW)

    def start(self):
        self.p.start()

    def join(self):
        self.p.join()

if __name__ == '__main__':
    clicker = Clicker()
    clicker.start_working()
