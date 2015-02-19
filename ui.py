import gtk


class ConfigDialog(gtk.Window):

    def __init__(self, config):
        gtk.Window.__init__(self)

        self.config = config

        self.set_size_request(600, 400)
        self.set_position(gtk.WIN_POS_CENTER)

        self.connect("delete_event", self.delete_event)

        self.init_ui()

        self.show()

    def delete_event(self, widget, event, data=None):
        return False

    def close(self, widget):
        self.destroy()

    def init_ui(self):
        self.set_border_width(10)

        main_vbox = gtk.VBox()

        search_box = gtk.Entry()
        places = gtk.List()


        main_buttons = gtk.HButtonBox()
        close = gtk.Button("Close")
        close.connect("clicked", self.close)

        main_buttons.add(close)

        main_vbox.pack_start(search_box, expand=False, fill=False)
        main_vbox.pack_start(places, fill=True)
        main_vbox.pack_end(main_buttons, expand=False, fill=False)

        search_box.show()
        places.show()
        close.show()
        main_buttons.show()
        main_vbox.show()

        self.add(main_vbox)


