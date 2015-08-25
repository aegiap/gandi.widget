#!/usr/bin/env python

import os

from gi.repository import Gtk, Gdk, GLib
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify

from gandi.cli.modules.status import Status

from .iaas import Iaas


_curr_dir=os.path.split(__file__)[0]


class GandiWidget:
    _subs = {'Iaas': Iaas}

    def __init__(self):
        self.indicator = appindicator.Indicator.new(
            "gandi.widget",
            "gandi.widget",
            appindicator.IndicatorCategory.APPLICATION_STATUS)

        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        icon = os.path.join(_curr_dir, 'resources', 'gandi.png')
        self.indicator.set_icon(icon)

        Notify.init('Gandi Widget')

        # create a menu
        self.menu = Gtk.Menu()
        # Add items to Menu and connect signals.
        self.build_menu()
        # Refresh menu every 1 min by default
        GLib.timeout_add_seconds(60, self.on_refresh)
        # Poll for status new events
        GLib.timeout_add_seconds(20, self.on_status_refresh)

    def build_menu(self):
        for name, kls in self._subs.items():
            menu_item = Gtk.ImageMenuItem.new_with_label(name)
            menu_item.set_always_show_image(False)
            menu_item.show()

            sub_menu = Gtk.Menu.new()
            for item in kls(self).list():
                sub_menu.append(item)

            menu_item.set_submenu(sub_menu)
            self.menu.append(menu_item)

        self.seperator = Gtk.SeparatorMenuItem.new()
        self.seperator.show()
        self.menu.append(self.seperator)

        self.refresh = Gtk.MenuItem('Refresh')
        self.refresh.connect("activate", self.on_refresh)
        self.refresh.show()
        self.menu.append(self.refresh)

        self.quit = Gtk.MenuItem('Quit')
        self.quit.connect('activate', self.on_exit_activate)
        self.quit.show()
        self.menu.append(self.quit)

        self.menu.show()
        self.indicator.set_menu(self.menu)

    def on_refresh(self, widget=None):
        self.rebuild_menu()

    def on_status_refresh(self, widget=None):
        filters = {
            'category': 'Incident',
            'current': True,
        }
        events = Status.events(filters)
        for event in events:
            message = '%s: %s' % (','.join(event['services']), event['title'])
            notification = Notify.Notification.new(
                'Gandi Status Event',
                message,
                'gandi-widget'
            )

            notification.set_hint("transient", GLib.Variant.new_boolean(True))
            notification.set_urgency(urgency=Notify.Urgency.CRITICAL)
            notification.set_timeout(1)
            notification.show()

    def rebuild_menu(self):
        for i in self.menu.get_children():
            self.menu.remove(i)
        self.build_menu()
        return True

    def on_exit_activate(self, widget):
        self.on_destroy(widget)

    def on_destroy(self, widget, data=None):
        Gtk.main_quit()


if __name__ == "__main__":
    # create the widget menu
    GandiWidget()
    # run the widget
    Gtk.main()
