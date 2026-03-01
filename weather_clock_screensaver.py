"""
Weather Clock Screensaver for the Adafruit Fruit Jam
and Fruit Jam OSDan Cogliano, https://DanTheGeek.com
"""

from displayio import Group, TileGrid, Bitmap, Palette
import adafruit_imageload
import adafruit_ntp

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

SCREENWIDTH = 320
SCREENHEIGHT = 240
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
    last_time_check = 0

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

        self.pool = adafruit_connection_manager.get_radio_socketpool(esp)
        ssl_context = adafruit_connection_manager.get_radio_ssl_context(esp)
        self.requests = adafruit_requests.Session(self.pool, ssl_context)

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
        font24 = bitmap_font.load_font("ssbundle_assets/fonts/Baloo-24.bdf")
        weatherfont = bitmap_font.load_font("ssbundle_assets/fonts/meteocons-48.bdf")
        font48 = bitmap_font.load_font("ssbundle_assets/fonts/Baloo-48.bdf")
        font12 = bitmap_font.load_font("ssbundle_assets/fonts/Baloo-12.bdf")
        self.temp_label = label.Label(font24, text='', color=0xFFFFFF, x=10, y=40)
        self.date_label = label.Label(font12, text='', color=0xFFFFFF, x=10, y=180)
        self.icon_label = label.Label(weatherfont, text='', color=0xFFFFFF, x=SCREENWIDTH, y=40)
        self.clockpos = [150,100]
        self.hour_label = label.Label(font48,text="00", color=0xFFFFFF, x=self.clockpos[0]-90, y=self.clockpos[1])
        self.sep_label = label.Label(font48,text=":", color=0xFFFFFF, x=self.clockpos[0], y=self.clockpos[1])
        self.min_label = label.Label(font48,text="00", color=0xFFFFFF, x=self.clockpos[0]+20, y=self.clockpos[1])
        self.ampm_label = label.Label(font12,text="", color=0xFFFFFF, x=self.clockpos[0]+100, y=self.clockpos[1])

        self.bmp, bg_palette = adafruit_imageload.load(
                    "ssbundle_assets/weatherclock/blue_gradient.bmp",
                    bitmap=displayio.Bitmap,
                    palette=displayio.Palette
                    )
        bg_tg = TileGrid(bitmap=self.bmp, pixel_shader=bg_palette)
        display_group = Group(scale=1)
        display_group.append(bg_tg)
        display_group.append(self.temp_label)
        display_group.append(self.date_label)
        display_group.append(self.icon_label)
        display_group.append(self.hour_label)
        display_group.append(self.min_label)
        display_group.append(self.sep_label)
        display_group.append(self.ampm_label)
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
        tz_offset = json["utc_offset_seconds"] // 3600
        print("tz_offset:",tz_offset)
        self.ntp = adafruit_ntp.NTP(self.pool, tz_offset=tz_offset, cache_seconds=3600)
        response.close()
        return json

    # Function to update display with weather data
    def update_weather(self,weather_data):
        display = supervisor.runtime.display
        current_weather = weather_data['current']
        temperature = self.temperature_text(current_weather['temperature_2m'])  # Get the temperature
        weather_description = current_weather['weather_code']  # Weather code for description
        print(f"debug1: {current_weather['weather_code']}")
        print(f"debug2: {self.weather_codes[current_weather['weather_code']]}")
        self.temp_label.text = temperature
        self.icon_label.text = self.weather_codes[current_weather['weather_code']]

    def update_clock(self):
        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }
        print(self.ntp.datetime)
        hour = self.ntp.datetime.tm_hour
        min = self.ntp.datetime.tm_min
        is_dst = self.ntp.datetime.tm_isdst
        mon = self.ntp.datetime.tm_mon
        day = self.ntp.datetime.tm_mday
        year = self.ntp.datetime.tm_year
        if hour < 12:
            is_pm = False
        else:
            is_pm = True
        hour = hour%12
        if hour == 0:
            hour = 12
        print(f"{hour}:{min}")
        if is_pm:
            self.ampm_label.text = "pm"
        else:
            self.ampm_label.text = "am"
        self.hour_label.text = f"{hour:2d}"
        self.min_label.text = f"{min:02d}"
        self.hour_label.x = self.clockpos[0] - self.hour_label.width
        self.icon_label.x = SCREENWIDTH - 10 - self.icon_label.width
        self.date_label.hidden = True
        self.date_label.text = f"{months[mon]} {day}, {year}"
        self.date_label.x = (SCREENWIDTH - self.date_label.width) // 2
        self.date_label.hidden = False

    def tick(self):
        now = time.monotonic()

        if now - self.last_move_time > self.move_cooldown:
            self.last_move_time = now
            print("***tick***")
            if now - self.last_weather_check > 600 or self.last_weather_check == 0: # 10 minutes
                self.last_weather_check = now
                data = self.get_weather()
                print(data)
                self.update_weather(data)
            if now - self.last_time_check >= 1 or self.last_time_check == 0:
                self.last_time_check = now
                self.update_clock()
            return True
        return False

