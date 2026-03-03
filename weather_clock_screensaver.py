"""
Weather Clock Screensaver for the Adafruit Fruit Jam
and Fruit Jam OSDan Cogliano, https://DanTheGeek.com
"""

from displayio import Group, TileGrid
import adafruit_imageload
import adafruit_ntp

import supervisor
import displayio
import os
import time

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

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

# Default city if not defined in settings.toml: New York City
LATITUDE = "40.7128"
LONGITUDE = "-74.0060"
TMZ = "America/New_York"
METRIC = 0

TEXTCOLOR = 0xCCCCFF
ICONCOLOR = 0x7777FF

class WeatherClockScreenSaver(Group):

    display_size = [SCREENWIDTH, SCREENHEIGHT]
    screenwidth = SCREENWIDTH
    screenheight = SCREENHEIGHT

    last_move_time = 0
    move_cooldown = .05
    last_weather_check = 0
    last_time_check = 0
    daytime = True

    day_outline_weather_codes = {
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

    night_outline_weather_codes = {
        0: "C",
        1: "C", 2: "I", 3: "N",
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

    day_fill_weather_codes = {
        0: "1",
        1: "1", 2: "3", 3: "5",
        45: "L", 48: "L",
        51: "7", 53: "7", 55: "8",
        56: "X", 57: "X",
        61: "7", 63: "8", 65: "8",
        66: "%", 67: "%",
        71: "\"", 73: "#", 75: "#",
        77: "\"",
        80: "7", 81: "8", 82: "8",
        85: "\"", 86: "#",
        95: "6"
    }

    night_fill_weather_codes = {
        0: "2",
        1: "2", 2: "4", 3: "5",
        45: "L", 48: "L",
        51: "7", 53: "7", 55: "8",
        56: "X", 57: "X",
        61: "7", 63: "8", 65: "8",
        66: "%", 67: "%",
        71: "\"", 73: "#", 75: "#",
        77: "\"",
        80: "7", 81: "8", 82: "8",
        85: "\"", 86: "#",
        95: "6"
    }

    def __init__(self):
        super().__init__()
        os.chdir("/".join(__file__.split("/")[:-1]))

        self.init_wifi()
        self.init_graphics()
        lat = os.getenv("LATITUDE")
        print("lat:", lat)
        lon = os.getenv("LONGITUDE")
        print("lon:", lon)
        tmz = os.getenv("TMZ")
        metric = os.getenv("METRIC")
        if lat is not None and lon is not None and tmz is not None:
            self.latitude = lat
            self.longitude = lon
            self.tmz = tmz
            if metric == 1:
                self.metric = True
            else:
                self.metric = False
        else:  # use default location
            print("no location set, using default location")
            self.latitude = LATITUDE
            self.longitude = LONGITUDE
            self.tmz = TMZ
            self.metric = False
            if METRIC == 1:
                self.metric = True

    def init_wifi(self):
        print("init_wifi()")

        # If you are using a board with pre-defined ESP32 Pins:
        esp32_cs = DigitalInOut(board.ESP_CS)
        esp32_ready = DigitalInOut(board.ESP_BUSY)
        esp32_reset = DigitalInOut(board.ESP_RESET)

        spi = board.SPI()
        self.esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

        self.pool = adafruit_connection_manager.get_radio_socketpool(self.esp)
        ssl_context = adafruit_connection_manager.get_radio_ssl_context(self.esp)
        self.requests = adafruit_requests.Session(self.pool, ssl_context)

        if self.esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
            print("ESP32 found and in idle mode")
        print("Firmware vers.", self.esp.firmware_version)
        print("MAC addr:", ":".join("%02X" % byte for byte in self.esp.MAC_address))
        for ap in self.esp.scan_networks():
            print("\t%-23s RSSI: %d" % (ap.ssid, ap.rssi))
        self.connect_wifi()

    def connect_wifi(self):
        # Get wifi details and more from a settings.toml file
        ssid = os.getenv("CIRCUITPY_WIFI_SSID")
        password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

        print("Connecting to AP...")
        while not self.esp.is_connected:
            try:
                self.esp.connect_AP(ssid, password)
            except OSError as e:
                print("could not connect to AP, retrying: ", e)
                continue
        print("Connected to", self.esp.ap_info.ssid, "\tRSSI:", self.esp.ap_info.rssi)
        print("My IP address is", self.esp.ipv4_address)

    def init_graphics(self):
        print("debug init_graphics")
        font24 = bitmap_font.load_font("ssbundle_assets/fonts/Baloo-24.bdf")
        weatherfont = bitmap_font.load_font("ssbundle_assets/fonts/meteocons-90.bdf")
        font48 = bitmap_font.load_font("ssbundle_assets/fonts/Baloo-num-48.bdf")
        font12 = bitmap_font.load_font("ssbundle_assets/fonts/Baloo-12.bdf")
        self.temp_label = label.Label(font24, text='', color=TEXTCOLOR, x=10, y=20)
        self.date_label = label.Label(font24, text='', color=TEXTCOLOR, x=10, y=180)
        self.icon_label = label.Label(weatherfont, text='', color=ICONCOLOR, x=10, y=90)
        self.clockpos = [150, 100]
        self.hour_label = label.Label(font48, text="00", color=TEXTCOLOR, x=self.clockpos[0]-90, y=self.clockpos[1])
        self.sep_label = label.Label(font48, text=":", color=TEXTCOLOR, x=self.clockpos[0], y=self.clockpos[1])
        self.min_label = label.Label(font48, text="00", color=TEXTCOLOR, x=self.clockpos[0]+20, y=self.clockpos[1])
        self.ampm_label = label.Label(font12, text="", color=TEXTCOLOR, x=self.clockpos[0]+100, y=self.clockpos[1])

        self.bmp_day, bg_palette = adafruit_imageload.load(
                    "ssbundle_assets/weatherclock/daytimebg.bmp",
                    bitmap=displayio.Bitmap,
                    palette=displayio.Palette
                    )
        self.day_tg = TileGrid(bitmap=self.bmp_day, pixel_shader=bg_palette)

        self.bmp_night, bg_palette = adafruit_imageload.load(
                    "ssbundle_assets/weatherclock/nighttimebg.bmp",
                    bitmap=displayio.Bitmap,
                    palette=displayio.Palette
                    )
        self.night_tg = TileGrid(bitmap=self.bmp_night, pixel_shader=bg_palette)

        self.display_group = Group(scale=1)
        self.display_group.append(self.day_tg)
        self.display_group.append(self.temp_label)
        self.display_group.append(self.date_label)
        self.display_group.append(self.icon_label)
        self.display_group.append(self.hour_label)
        self.display_group.append(self.min_label)
        self.display_group.append(self.sep_label)
        self.display_group.append(self.ampm_label)
        self.append(self.display_group)
        print(f"display size: {self.display_size}")
        print("debug end init_graphics")
        self.startcount = 0

    def temperature_text(self, tempC):
        if self.metric:
            return "{:3.0f}°".format(tempC)
        else:
            return "{:3.0f}°".format(32.0 + 1.8 * tempC)

    # Function to fetch weather data
    def get_weather(self):
        print("get_weather()")
        # Initialize a requests session


        print("debug 1")
        dir(self.requests)
        print("getting data...")
        URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&"
        URL += "daily=weather_code,temperature_2m_max,temperature_2m_min"
        URL += ",sunrise,sunset,wind_speed_10m_max,wind_direction_10m_dominant"
        URL += "&current=weather_code,precipitation,temperature_2m"
        URL += "&timeformat=unixtime"
        URL += f"&timezone={self.tmz}"
        response = self.requests.get(URL)
        json = response.json()
        tz_offset = json["utc_offset_seconds"] // 3600
        self.ntp = adafruit_ntp.NTP(self.pool, tz_offset=tz_offset, cache_seconds=3600)
        response.close()
        return json

    # Function to update display with weather data
    def update_weather(self, weather_data):
        current = weather_data['current']['time']
        sunrise = weather_data['daily']['sunrise'][0]
        sunset = weather_data['daily']['sunset'][0]
        print("sunrise, current, sunset:", sunrise, current, sunset)
        if (current < sunrise or current > sunset) and self.daytime is not False:
            # switch to nighttime
            self.daytime = False
            self.display_group.pop(0)
            self.display_group.insert(0, self.night_tg)
            pass
        elif (sunrise < current and current < sunset) and self.daytime != True:
            # switch to daytime
            self.daytime = True
            self.display_group.pop(0)
            self.display_group.insert(0, self.day_tg)
        current_weather = weather_data['current']
        temperature = self.temperature_text(current_weather['temperature_2m'])  # Get the temperature
        self.temp_label.text = temperature
        self.temp_label.x = SCREENWIDTH - 10 - self.temp_label.width
        if self.daytime:
            # use sun in icons
            self.icon_label.text = self.day_fill_weather_codes[current_weather['weather_code']]
        else:
            # use moon in icons:
            self.icon_label.text = self.night_fill_weather_codes[current_weather['weather_code']]

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
        try:
            print(self.ntp.datetime)
            hour = self.ntp.datetime.tm_hour
            min = self.ntp.datetime.tm_min
            mon = self.ntp.datetime.tm_mon
            day = self.ntp.datetime.tm_mday
            year = self.ntp.datetime.tm_year
            if hour < 12:
                is_pm = False
            else:
                is_pm = True
            hour = hour % 12
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
            # self.icon_label.x = SCREENWIDTH - 10 - self.icon_label.width
            self.date_label.hidden = True
            self.date_label.text = f"{months[mon]} {day}, {year}"
            self.date_label.x = (SCREENWIDTH - self.date_label.width) // 2
            self.date_label.hidden = False
        except OSError as e:
            print(f"Network error: {e}, restarting connection")
            self.connect_wifi()

    def tick(self):
        now = time.monotonic()

        if now - self.last_move_time > self.move_cooldown:
            self.last_move_time = now
            # print("***tick***")
            if now - self.last_weather_check > 600 or self.last_weather_check == 0:  # 10 minutes
                self.last_weather_check = now
                data = self.get_weather()
                print(data)
                self.update_weather(data)
            if now - self.last_time_check >= 1 or self.last_time_check == 0:
                self.last_time_check = now
                self.update_clock()
            return True
        return False

