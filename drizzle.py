import sys
import os
import gtk
import appindicator
import pywapi

NOW = 'now'

ATMOSPHERE = 'atmosphere'

CONDITION = 'condition'


class WeatherIndicator:
    UNKNOWN_WEATHER = "na"

    def __init__(self):

        self_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")

        self.update_interval = 30
        self.weather = {}

        self.indicator = appindicator.Indicator("Weather", self.UNKNOWN_WEATHER, appindicator.CATEGORY_OTHER, )
        self.indicator.set_icon_theme_path(self_path)
        self.indicator.set_status(appindicator.STATUS_ACTIVE)
        self.menu_setup()

        self.temperature_unit = ''

        gtk.timeout_add(1000, self.update_weather)

    def create_menu_item(self, text):
        menu_item = gtk.MenuItem(text)
        menu_item.set_sensitive(False)
        menu_item.show()
        return menu_item

    def menu_setup(self):
        self.menu = gtk.Menu()

        if len(self.weather) != 0:
            self.menu.append(self.create_menu_item(self.title))
            self.menu.append(self.create_menu_item(None))
            self.menu.append(self.create_menu_item(self.weather[NOW]['text']))
            self.menu.append(self.create_menu_item(
                "Temperature: " + self.weather[NOW]['temp'] + ' ' + self.temperature_unit))  # TODO: Localize
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

        self.weather = {}

        self.weather[NOW] = {'condition_code': weather[CONDITION]['code'], 'temp': weather[CONDITION]['temp'],
                             'text': weather[CONDITION]['text']}

        self.weather[NOW]['wind_chill'] = weather['wind']['chill']
        self.weather[NOW]['wind_direction'] = weather['wind']['direction']
        self.weather[NOW]['wind_speed'] = weather['wind']['speed']

        self.weather[NOW]['humidity'] = weather[ATMOSPHERE]['humidity']
        self.weather[NOW]['pressure'] = weather[ATMOSPHERE]['pressure']
        self.weather[NOW]['pressure_rising'] = [False, True][int(weather[ATMOSPHERE]['rising'])]
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


if __name__ == '__main__':
    wi = WeatherIndicator()
    wi.set_location(u'CAXX0295')
    gtk.main()