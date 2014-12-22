#!/usr/bin/env python
# -*- coding: utf8 -*-

import gtk

from zrequest import auth
from zthread import UpdateThread


class AuthenticationtDialog(object):
    def __init__(self, widget, indicator):

        self.indicator = indicator
        self.dialog = gtk.Dialog()

        label_username = gtk.Label("Nom d'utilisateur")
        label_username.show()
        self.dialog.get_content_area().add(label_username)

        self.entry_username = gtk.Entry()
        self.entry_username.show()
        self.entry_username.set_activates_default(True)
        self.dialog.get_content_area().add(self.entry_username)

        label_password = gtk.Label("Mot de passe")
        label_password.show()
        self.dialog.get_content_area().add(label_password)

        self.entry_password = gtk.Entry()
        self.entry_password.set_visibility(False)
        self.entry_password.show()
        self.dialog.get_content_area().add(self.entry_password)

        self.dialog.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.dialog.set_default(self.dialog.get_widget_for_response(gtk.RESPONSE_OK))
        self.dialog.connect("response", self.response)

        self.dialog.run()

    def response(self, widget, data):
        global username

        if data == gtk.RESPONSE_CANCEL:
            self.dialog.destroy()

        if data == gtk.RESPONSE_OK:
            username = self.entry_username.get_text()
            response = auth(
                self.indicator.client,
                self.indicator.URL,
                self.entry_username.get_text(),
                self.entry_password.get_text())

            if response:
                self.dialog.destroy()
                UpdateThread(self.indicator).start()
                self.indicator.set_loop_update()
                pass
            else:
                self.entry_username.set_text("")
                self.entry_password.set_text("")