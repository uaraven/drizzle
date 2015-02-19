# coding=utf-8
import sys
import os
import datetime
import ConfigParser

import gtk
import appindicator

import pywapi
import ui

CONFIG_PATH = '.config/drizzle'

NOW = 'now'
ATMOSPHERE = 'atmosphere'
DEGREE = u'°'
CONDITION = 'condition'


class Config:
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser('~'), CONFIG_PATH)
        self.config = ConfigParser.SafeConfigParser()
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)

    def is_location_present(self):
        return self.config.has_section('location')

    def get_locations(self):
        if self.config.has_section('location'):
            return [x[1] for x in self.config.items('location')]
        else:
            return [u'CAXX0295']

    def get_update_interval(self):
        if self.config.has_option('settings', 'update'):
            timeout_secs = self.config.getint('settings', 'update')
        else:
            timeout_secs = 60 * 120
        return timeout_secs * 1000


class Forecast:
    def __init__(self, yahoo_forecast):
        self.code = yahoo_forecast['code']
        date = yahoo_forecast['date'].split(' ')
        self.date = datetime.date(int(date[2]), self.get_month(date[1]), int(date[0]))
        self.day = yahoo_forecast['day']
        self.high = yahoo_forecast['high']
        self.low = yahoo_forecast['low']

    def get_month(self, param):
        return {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
                'Oct': 10, 'Nov': 11, 'Dec': 12}[param]

    def not_today(self):
        return self.date != datetime.date.today()


class CurrentWeather:
    def __init__(self, descriptor):
        self.condition_code = descriptor[CONDITION]['code']
        self.temp = descriptor[CONDITION]['temp']
        self.text = descriptor[CONDITION]['text']

        self.wind_chill = descriptor['wind']['chill']
        self.wind_direction = descriptor['wind']['direction']
        self.wind_speed = descriptor['wind']['speed']

        self.humidity = descriptor[ATMOSPHERE]['humidity']
        self.pressure = descriptor[ATMOSPHERE]['pressure']
        self.pressure_rising = descriptor[ATMOSPHERE]['rising']
        self.visibility = descriptor[ATMOSPHERE]['visibility']

        self.location_name = descriptor['location']['city'] + ', ' + descriptor['location']['country']
        self.title = descriptor[CONDITION]['title']

        self.temperature_unit = descriptor['units']['temperature']
        self.distance_unit = descriptor['units']['distance']
        self.pressure_unit = descriptor['units']['pressure']
        self.speed_unit = descriptor['units']['speed']


class WeatherIndicator:
    UNKNOWN_WEATHER = "na"

    def __init__(self, config):

        self.config = config

        self_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")

        self.indicator = appindicator.Indicator("Weather", self.UNKNOWN_WEATHER, appindicator.CATEGORY_OTHER, )
        self.indicator.set_icon_theme_path(self_path)
        self.indicator.set_status(appindicator.STATUS_ACTIVE)
        self.update_indicator_menu(None)

    def create_menu_item(self, text):
        menu_item = gtk.MenuItem(text)
        menu_item.set_sensitive(False)
        menu_item.show()
        return menu_item

    def update_indicator_menu(self, weather):
        self.menu = gtk.Menu()

        tm = datetime.datetime.now().strftime('%X')

        if weather is not None:
            self.menu.append(self.create_menu_item(weather.location_name + ' at ' + tm))
            self.menu.append(self.create_menu_item(None))
            self.menu.append(self.create_menu_item(weather.text))
            self.menu.append(self.create_menu_item(
                "Temperature: " + weather.temp + DEGREE + weather.temperature_unit))  # TODO: Localize
            self.menu.append(self.create_menu_item('Feels like: ' + weather.wind_chill + DEGREE
                                                   + weather.temperature_unit))
            self.menu.append(self.create_menu_item('Humidity: ' + weather.humidity + '%'))
            self.menu.append(self.create_menu_item('Pressure: ' + weather.pressure + ' '
                                                   + weather.pressure_unit))
            if len(weather.visibility) > 0:
                self.menu.append(self.create_menu_item('Visibility: ' + weather.visibility + ' '
                                                       + weather.distance_unit))
            self.menu.append(self.create_menu_item(None))
        self.menu.append(self.create_configure_menu())
        self.quit_item = gtk.MenuItem("Quit")  # TODO: Localize
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

        self.indicator.set_menu(self.menu)

    def quit(self, widget):
        sys.exit(0)

    def update_weather(self, weather):
        self.indicator.set_icon(weather.condition_code)
        if weather is not None:
            self.update_indicator_menu(weather)

    def create_configure_menu(self):
        config = gtk.MenuItem("Configure...")
        config.connect("activate", self.show_configurator)
        config.show()
        return config

    def show_configurator(self, widget):
        ui.ConfigDialog(self.config)



class Drizzle:
    def __init__(self):
        self.config = Config()
        self.indicator = WeatherIndicator(self.config)
        self.weather = None

        gtk.timeout_add(self.config.get_update_interval(), self.update_weather)
        self.update_weather()

    def update_weather(self):
        try:
            locations = self.config.get_locations()
            weather = pywapi.get_weather_from_yahoo(locations[0])
            self.weather = CurrentWeather(weather)
            self.forecasts = filter(self.not_today, [Forecast(x) for x in weather['forecasts']])

            self.indicator.update_weather(self.weather)
        except Exception as e:
            print e
            self.weather = None

        return True

    def not_today(self, forecast):
       return forecast.not_today()


if __name__ == '__main__':
    drizzle = Drizzle()
    gtk.main()
