# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib
from gi.repository import Notify


class Base(object):
    def __init__(self, widget):
        self._widget = widget

    def list(self):
        raise NotImplemented()

    def copy(self, widget, element):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(element, -1)
        message = '%s copied to clipboard' % element
        self._notify(message)

    def _call_api(self, method, *args, **kwargs):
        try:
            method(*args)
        except Exception as err:
            print('Error: ', err.message)
            error_indicator = Gtk.ImageMenuItem.new_with_label(
                'An error occured.')
            img = Gtk.Image.new_from_icon_name("error", Gtk.IconSize.MENU)
            error_indicator.set_always_show_image(True)
            error_indicator.set_image(img)
            error_indicator.show()
            self._widget.menu.append(error_indicator)

    def _notify(self, message):
        notification = Notify.Notification.new(
            'Gandi Widget',
            message,
            'gandi-widget'
        )

        notification.set_hint('transient', GLib.Variant.new_boolean(True))
        notification.set_urgency(urgency=Notify.Urgency.CRITICAL)
        notification.set_timeout(1)
        notification.show()