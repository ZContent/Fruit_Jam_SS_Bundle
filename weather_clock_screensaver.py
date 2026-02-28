"""
Weather Clock Screensaver for the Adafruit Fruit Jam
and Fruit Jam OSDan Cogliano, https://DanTheGeek.com
"""

from displayio import Group, TileGrid, Bitmap, Palette
import adafruit_imageload

import supervisor
import displayio
import os
import random
import time
import terminalio
import sys

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import bitmaptools

from os import getenv

import adafruit_connection_manager
import adafruit_requests
import board
from digitalio import DigitalInOut

from adafruit_esp32spi import adafruit_esp32spi

SCREENWIDTH = 640
SCREENHEIGHT = 480
SCREENDEPTH = 8

# Open-Meteo API URL for weather data
API_URL = "https://api.open-meteo.com/v1/forecast"

# User-defined settings

# New York City
LATITUDE = "40.7128"
LONGITUDE = "74.0060"
TMZ = "America/New_York"
METRIC = False
CITY = "New York, NY"

# Annapolis
LATITUDE = 38.9764
LONGITUDE = 76.4896
TMZ = "America/New_York"
METRIC = False
CITY = "Annapolis, MD"

class WeatherClockScreenSaver(Group):

    display_size = [SCREENWIDTH,SCREENHEIGHT]
    screenwidth = SCREENWIDTH
    screenheight = SCREENHEIGHT

    last_move_time = 0
    move_cooldown = .05
    last_weather_check = 0

    weather_codes = {
        0: "B",
        1: "B", 2: "H", 3: "N",
        45: "L", 48: "L",
        51: "Q", 53: "Q", 55: "R",
        56: "X", 57: "X",
        61: "Q", 63: "R", 65: "R",
        66: "X", 67: "X",
        71: "U", 73: "W", 75: "W",
        77: "U",
        80: "Q", 81: "R", 82: "R",
        85: "U", 86: "W",
        95: "P"

    }
    def __init__(self):
        super().__init__()
        os.chdir("/".join(__file__.split("/")[:-1]))

        self.init_wifi()
        self.init_graphics()

    def init_wifi(self):
        print("init_wifi()")

        # Get wifi details and more from a settings.toml file
        ssid = getenv("CIRCUITPY_WIFI_SSID")
        password = getenv("CIRCUITPY_WIFI_PASSWORD")

        # If you are using a board with pre-defined ESP32 Pins:
        esp32_cs = DigitalInOut(board.ESP_CS)
        esp32_ready = DigitalInOut(board.ESP_BUSY)
        esp32_reset = DigitalInOut(board.ESP_RESET)

        spi = board.SPI()
        esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

        pool = adafruit_connection_manager.get_radio_socketpool(esp)
        ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
        self.requests = adafruit_requests.Session(pool, ssl_context)

        if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
            print("ESP32 found and in idle mode")
        print("Firmware vers.", esp.firmware_version)
        print("MAC addr:", ":".join("%02X" % byte for byte in esp.MAC_address))
        for ap in esp.scan_networks():
            print("\t%-23s RSSI: %d" % (ap.ssid, ap.rssi))

        print("Connecting to AP...")
        while not esp.is_connected:
            try:
                esp.connect_AP(ssid, password)
            except OSError as e:
                print("could not connect to AP, retrying: ", e)
                continue
        print("Connected to", esp.ap_info.ssid, "\tRSSI:", esp.ap_info.rssi)
        print("My IP address is", esp.ipv4_address)

    def init_graphics(self):
        print("debug init_graphics")
        self.bmp = Bitmap(self.screenwidth, self.screenheight, SCREENDEPTH)
        bg_palette = Palette(2)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0x333333
        self.bmp.fill(0)
        font24 = bitmap_font.load_font("ssbundle_assets/fonts/Baloo-24.bdf")
        self.bb24 = font24.get_bounding_box()
        weatherfont = bitmap_font.load_font("ssbundle_assets/fonts/meteocons-48.bdf")
        self.temp_label = label.Label(font24, text=f'---', color=0xFFFFFF, x=10, y=10)
        city_label = label.Label(font24, text=f'{CITY}', color=0xFFFFFF, x=10, y=50)
        self.icon_label = label.Label(weatherfont, text=f')', color=0xFFFFFF, x=10, y=120)
        #weather_label = label.Label(terminalio.FONT, text=f'Weather: {weather_description}', color=0xFFFFFF, x=10, y=40)

        bg_tg = TileGrid(bitmap=self.bmp, pixel_shader=bg_palette)
        self.bmp.fill(0)
        display_group = Group(scale=1)
        display_group.append(bg_tg)
        display_group.append(self.temp_label)
        display_group.append(city_label)
        display_group.append(self.icon_label)
        self.append(display_group)
        print(f"display size: {self.display_size}")
        print("debug end init_graphics")
        self.startcount = 0


    def temperature_text(self,tempC):
        if METRIC:
            return "{:3.0f}°C".format(tempC)
        else:
            return "{:3.0f}°F".format(32.0 + 1.8 * tempC)

    # Function to fetch weather data
    def get_weather(self):
        print("get_weather()")
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "weather_code,temperature_2m,precipitation",
            #"current_weather": True,
        }
        # Initialize a requests session
        #requests = adafruit_requests.Session(socketpool, ssl.create_default_context())
        #response = requests.get(API_URL, params=params)
        print("debug 1")
        dir(self.requests)
        print("getting data...")
        URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&"
        URL += "daily=weather_code,temperature_2m_max,temperature_2m_min"
        URL += ",sunrise,sunset,wind_speed_10m_max,wind_direction_10m_dominant"
        URL += "&current=weather_code,precipitation,temperature_2m"
        URL += "&timeformat=unixtime"
        URL += f"&timezone={TMZ}"
        response = self.requests.get(URL)
        json = response.json()
        print("response json:",json)
        response.close()
        return json

    # Function to update display with weather data
    def update_display(self,weather_data):
        display = supervisor.runtime.display
        current_weather = weather_data['current']
        temperature = self.temperature_text(current_weather['temperature_2m'])  # Get the temperature
        weather_description = current_weather['weather_code']  # Weather code for description
        print(f"debug1: {current_weather['weather_code']}")
        print(f"debug2: {self.weather_codes[current_weather['weather_code']]}")
        self.temp_label.text = temperature
        self.icon_label.text = self.weather_codes[current_weather['weather_code']]

    def tick(self):
        now = time.monotonic()

        if now - self.last_move_time > self.move_cooldown:
            self.last_move_time = now
            print("***tick***")
            if now - self.last_weather_check > 600 or self.last_weather_check == 0: # 10 minutes
                self.last_weather_check = now
                data = self.get_weather()
                print(data)
                self.update_display(data)
            return True
        return False

