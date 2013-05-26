#!/usr/bin/python

import RPi.GPIO as GPIO
from multiprocessing import Process
import time
import requests
import json
import ConfigParser


class Api:

    def __init__(self, url, token):
        self.url = url
        self.token = token

    def coffee(self):
        payload = self.prepare_payload('coffees')
        return self.send_payload(payload)

    def sandwich(self):
        payload = self.prepare_payload('sandwiches')
        return self.send_payload(payload)

    def prepare_payload(self, stat_name):
        data = {
            'token': self.token,
            'stats': {
                'name': stat_name
            }
        }
        payload = json.dumps(data)
        return payload

    def send_payload(self, payload):
        headers = {'Content-Type': 'application/json'}
        req = requests.post(self.url, data=payload, headers=headers)
        return req


class Config:

    def __init__(self, filepath):
        self.config = ConfigParser.ConfigParser()
        self.config.read(filepath)

    def api_url(self):
        url = self.config.get('API', 'url')
        return url

    def api_token(self):
        token = self.config.get('API', 'token')
        return token


class Clicker:

    def __init__(self):
        self.b_list = []
        GPIO.setmode(GPIO.BOARD)

    def start_working(self):
        for b in  self.b_list:
            b.start()
        for b in  self.b_list:
            b.join()


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
            try:
                time_start = time.time()
                self.f()
                duration = time.time() - time_start
                if duration <= 1:
                    time.sleep(1-duration)
            except:
                for _ in range(0,20):
                    GPIO.output(self.led_pin, GPIO.HIGH)
                    time.sleep(0.1)
                    GPIO.output(self.led_pin, GPIO.LOW)
            GPIO.output(self.led_pin, GPIO.LOW)

    def start(self):
        self.p.start()

    def join(self):
        self.p.join()


if __name__ == '__main__':
    config = Config('config.cfg')
    api = Api(config.api_url(), config.api_token())
    clicker = Clicker(api)
    b_coffee = Button(11, 16, api.coffee)
    b_sandwich = Button(13, 18, api.sandwich)
    clicker.b_list = [b_coffee, b_sandwich]
    clicker.start_working()
