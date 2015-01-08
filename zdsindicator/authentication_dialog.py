#!/usr/bin/env python
# -*- coding: utf8 -*-

from gi.repository import Gtk

from zrequest import auth
from zthread import UpdateThread


class AuthenticationtDialog(object):
    def __init__(self, widget, indicator):

        self.indicator = indicator
        self.dialog = Gtk.Dialog()
        self.dialog.set_title("Connexion")
        self.dialog.set_default_size(200, 200)
        self.dialog.set_icon_from_file(self.indicator.icon_path+"/zdsindicator-icon.png")
        self.dialog.set_border_width(10)

        label_username = Gtk.Label("Nom d'utilisateur")
        label_username.show()
        self.dialog.get_content_area().add(label_username)

        self.entry_username = Gtk.Entry()
        self.entry_username.show()
        self.entry_username.set_activates_default(True)
        self.dialog.get_content_area().add(self.entry_username)

        label_password = Gtk.Label("Mot de passe")
        label_password.show()
        self.dialog.get_content_area().add(label_password)

        self.entry_password = Gtk.Entry()
        self.entry_password.set_visibility(False)
        self.entry_password.show()
        self.dialog.get_content_area().add(self.entry_password)

        self.dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.dialog.set_default(self.dialog.get_widget_for_response(Gtk.ResponseType.OK))
        self.dialog.connect("response", self.response)

        self.dialog.run()

    def response(self, widget, data):
        global username

        if data == Gtk.ResponseType.CANCEL:
            self.dialog.destroy()

        if data == Gtk.ResponseType.OK:
            response = auth(
                self.indicator.client,
                self.indicator.URL,
                self.entry_username.get_text(),
                self.entry_password.get_text())

            if response:
                self.dialog.destroy()
                UpdateThread(self.indicator).start()
                self.indicator.set_loop_update()
            else:
                self.entry_username.set_text("")
                self.entry_password.set_text("")