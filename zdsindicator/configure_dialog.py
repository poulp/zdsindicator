#!/usr/bin/env python
# -*- coding: utf8 -*-

import gtk
import gobject


class ConfigureDialog(object):
    def __init__(self, widget, indicator):

        self.indicator = indicator

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title('Paramètres')
        self.window.connect('delete_event', self.cancel_dialog)
        self.window.connect('key-press-event', self.keypress)
        self.window.set_border_width(10)
        self.window.set_icon_from_file(self.indicator.icon_path+"/zdsindicator-icon.png")

        vbox_window = gtk.VBox(True, 2)
        self.window.add(vbox_window)
        vbox_window.show()

        hbox_refresh_scale = gtk.VBox(False, 0)
        vbox_window.pack_start(hbox_refresh_scale, False, True, 0)
        hbox_refresh_scale.show()

        self.label_refresh_scale = gtk.Label("Rafraichir toutes les 10 minutes")
        hbox_refresh_scale.pack_start(self.label_refresh_scale, False, False, 0)
        self.label_refresh_scale.show()

        button_refresh_scale = gtk.Adjustment(int(self.indicator.refresh_time / 60000), 1.0, 90.0, 1.0, 10.0, 0.0)
        button_refresh_scale.connect('value_changed', self.set_refresh_scale_label)
        self.scaletimer = gtk.HScale(button_refresh_scale)
        self.scaletimer.set_draw_value(False)
        self.scaletimer.set_digits(0)
        hbox_refresh_scale.pack_start(self.scaletimer, True, True, 0)
        self.set_refresh_scale_label(self.scaletimer)
        self.scaletimer.show()

        vbox_check = gtk.VBox(True, 2)
        vbox_window.pack_start(vbox_check, True, True, 2)
        vbox_check.show()

        self.activate_notifications_check = gtk.CheckButton("Afficher les notifications")
        vbox_check.pack_start(self.activate_notifications_check, True, True, 2)
        self.activate_notifications_check.show()
        self.activate_notifications_check.set_active(self.indicator.activate_notifications)

        hbox_button = gtk.HBox(True, 2)
        hbox_button.show()
        vbox_window.pack_start(hbox_button, True, True, 2)

        button_cancel = gtk.Button("Annuler")
        button_cancel.show()
        button_cancel.connect('clicked', self.cancel_dialog)
        hbox_button.pack_start(button_cancel, True, True, 2)

        button_save = gtk.Button("Sauver")
        button_save.show()
        button_save.connect('clicked', self.save, None)
        hbox_button.pack_start(button_save, True, True, 2)

        self.window.set_keep_above(True)
        self.window.show()

    def cancel_dialog(self, widget, data=None):
        self.window.hide()

    def keypress(self, widget, data):
        if data.keyval == gtk.keysyms.Escape:
            self.window.hide()

    def set_refresh_scale_label(self, widget):
        value = widget.get_value()
        if int(value) == 1:
            self.label_refresh_scale.set_text("Rafraichir toutes les minutes")
        else:
            self.label_refresh_scale.set_text("Rafraichir toutes les " + str(int(value)) + " minutes")

    def save(self, widget, data):

        self.indicator.gconf['activate_notifications'] = self.activate_notifications_check.get_active()
        self.indicator.activate_notifications = self.activate_notifications_check.get_active()

        if not self.indicator.refresh_time == int(self.scaletimer.get_value() * 60000):
            self.indicator.gconf['refresh_time'] = int(self.scaletimer.get_value() * 60000)
            self.indicator.refresh_time = int(self.scaletimer.get_value() * 60000)

        self.window.hide()

        gobject.source_remove(self.indicator.timeout_id)
        self.indicator.set_loop_update()