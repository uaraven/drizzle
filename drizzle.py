# coding=utf-8
import sys
import os
import gtk
import appindicator
import pywapi
import datetime


CONFIG_PATH = '.config/drizzle'

NOW = 'now'
ATMOSPHERE = 'atmosphere'
DEGREE = u'°'
CONDITION = 'condition'


class Config:
    def __init__(self):
        self.config = os.path.join(os.path.expanduser('~'), CONFIG_PATH)

    def is_location_present(self):
        return self.get_locations() is not None

    def get_locations(self):
        loc_file = os.path.join(self.config, 'location')
        if os.path.exists(loc_file):
            with open(loc_file) as inp:
                location = inp.readlines()
                return [x.strip() for x in location]
        else:
            return None


class Forecast:
    def __init__(self, yahoo_forecast):
        self.code = yahoo_forecast['code']
        self.date = datetime.date.strptime(yahoo_forecast['date'], '%d %b %Y')
        self.day = yahoo_forecast['day']
        self.high = yahoo_forecast['high']
        self.low = yahoo_forecast['low']


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

    def __init__(self, locations):

        self_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")

        self.update_interval = 3
        self.weather = {}

        self.indicator = appindicator.Indicator("Weather", self.UNKNOWN_WEATHER, appindicator.CATEGORY_OTHER, )
        self.indicator.set_icon_theme_path(self_path)
        self.indicator.set_status(appindicator.STATUS_ACTIVE)
        self.menu_setup()

        self.temperature_unit = ''

        gtk.timeout_add(self.update_interval * 60 * 1000, self.update_weather)
        self.locations = locations
        self.id = locations[0]

    def create_menu_item(self, text):
        menu_item = gtk.MenuItem(text)
        menu_item.set_sensitive(False)
        menu_item.show()
        return menu_item

    def menu_setup(self):
        self.menu = gtk.Menu()

        if len(self.weather) != 0:
            self.menu.append(self.create_menu_item(self.location_name))
            self.menu.append(self.create_menu_item(None))
            self.menu.append(self.create_menu_item(self.weather[NOW]['text']))
            self.menu.append(self.create_menu_item(
                "Temperature: " + self.weather[NOW]['temp'] + DEGREE + self.temperature_unit))  # TODO: Localize
            self.menu.append(self.create_menu_item('Feels like: ' + self.weather[NOW]['wind_chill'] + DEGREE
                                                   + self.temperature_unit))
            self.menu.append(self.create_menu_item('Humidity: ' + self.weather[NOW]['humidity'] + '%'))
            self.menu.append(self.create_menu_item('Pressure: ' + self.weather[NOW]['pressure'] + ' '
                                                   + self.pressure_unit))
            if len(self.weather[NOW]['visibility']) > 0:
                self.menu.append(self.create_menu_item('Visibility: ' + self.weather[NOW]['visibility'] + ' '
                                                       + self.distance_unit))
            pass
            self.menu.append(self.create_menu_item(None))
        self.quit_item = gtk.MenuItem("Quit") # TODO: Localize
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

        self.indicator.set_menu(self.menu)

    def quit(self, widget):
        sys.exit(0)

    def set_location(self, location, lookup=False):
        if lookup:
            ids = pywapi.get_location_ids(location)
            for k in ids:
                self.id = k
                self.location_name = ids[k]
                break
        else:
            self.id = location
            self.location_name = ''

        self.update_weather()

    def update_weather(self):
        weather = pywapi.get_weather_from_yahoo(self.id)
        print 'Updated @', datetime.datetime.today()

        self.weather = {NOW: {'condition_code': weather[CONDITION]['code'], 'temp': weather[CONDITION]['temp'],
                              'text': weather[CONDITION]['text']}}

        self.weather[NOW]['wind_chill'] = weather['wind']['chill']
        self.weather[NOW]['wind_direction'] = weather['wind']['direction']
        self.weather[NOW]['wind_speed'] = weather['wind']['speed']

        self.weather[NOW]['humidity'] = weather[ATMOSPHERE]['humidity']
        self.weather[NOW]['pressure'] = weather[ATMOSPHERE]['pressure']
        self.weather[NOW]['pressure_rising'] = weather[ATMOSPHERE]['rising']
        self.weather[NOW]['visibility'] = weather[ATMOSPHERE]['visibility']

        self.location_name = weather['location']['city'] + ', ' + weather['location']['country']
        self.title = weather[CONDITION]['title']

        self.indicator.set_icon(weather[CONDITION]['code'])

        self.temperature_unit = weather['units']['temperature']
        self.distance_unit = weather['units']['distance']
        self.pressure_unit = weather['units']['pressure']
        self.speed_unit = weather['units']['speed']

        self.menu_setup()
        gtk.timeout_add(self.update_interval * 60 * 1000, self.update_weather)
        return False


class Drizzle:
    def __init__(self):
        self.config = Config()
        self.indicator = WeatherIndicator()


if __name__ == '__main__':
    c = Config()
    c.get_location()
    wi = WeatherIndicator()
    wi.set_location(u'CAXX0295')
    gtk.main()