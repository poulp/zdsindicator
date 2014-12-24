#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests
import os
import webbrowser
import pynotify
import appindicator
import gtk
import gobject

from GConf import GConf
from authentication_dialog import AuthenticationtDialog
from zthread import UpdateThread
from configure_dialog import ConfigureDialog


class ZIndicator(object):
    def __init__(self):

        # general configuration
        self.app_name = 'Zds Indicator'
        self.app_identifier = 'zdsindicator'
        self.app_comments = 'Des notifications pour le site Zeste de Savoir'
        self.client = requests.Session()
        self.stopupdate = False
        self.timeout_id = -1
        self.icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icons')
        self.gconf = GConf(self.app_identifier)

        # default activate notifications
        self.activate_notifications = False
        # temp de rafraichissement par défaut en ms
        self.refresh_time = 60000
        # démarrage au lancement
        self.autostart = False
        # base url
        self.URL = 'https://zestedesavoir.com'
        # username member
        self.username = ""

        # indicator options
        self.ind = appindicator.Indicator(self.app_name, 'zdsindicator', appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.ind.set_icon_theme_path(self.icon_path)
        self.ind.set_icon("zdsindicator-icon")

        # initialisation des paramètres
        if self.gconf['activate_notifications'] is not None:
            self.activate_notifications = self.gconf['activate_notifications']

        if self.gconf['refresh_time'] is not None:
            self.refresh_time = self.gconf['refresh_time']

        if self.gconf['autostart'] is not None:
            self.autostart = self.gconf['autostart']

        self.menu = gtk.Menu()

        self.menu_mp = gtk.MenuItem('Messages Privés')
        self.menu_mp.show()
        self.menu.append(self.menu_mp)

        self.menu_notif = gtk.MenuItem('Notifications')
        self.menu_notif.show()
        self.menu.append(self.menu_notif)

        self.menu_serveur_error = gtk.MenuItem('Problème de connexion au serveur')
        self.menu_serveur_error.set_sensitive(False)
        self.menu.append(self.menu_serveur_error)

        self.menu_auth = gtk.MenuItem('Connexion')
        self.menu_auth.hide()
        self.menu_auth.connect('activate', AuthenticationtDialog, self)
        self.menu.append(self.menu_auth)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        self.menu_username = gtk.MenuItem('username')
        self.menu_username.hide()
        self.menu.append(self.menu_username)

        menu_refresh = gtk.MenuItem('Rafraichir')
        menu_refresh.show()
        menu_refresh.connect('activate', self.update)
        self.menu.append(menu_refresh)

        menu_configure = gtk.MenuItem('Paramètres')
        menu_configure.show()
        menu_configure.connect('activate', ConfigureDialog, self)
        self.menu.append(menu_configure)

        menu_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        menu_quit.connect("activate", self.quit)
        menu_quit.show()
        self.menu.append(menu_quit)

        self.menu.show()
        self.ind.set_menu(self.menu)

        pynotify.init('ZDSNotification')
        self.set_loop_update()

    def quit(self, widget, data=None):
        gtk.main_quit()

    def menuitem_response_website(self, data, url):
        webbrowser.open(url)

    def set_loop_update(self):
        self.timeout_id = gobject.timeout_add(self.refresh_time, self.update)

    def update(self, widget=None):
        UpdateThread(self).start()
        return True

    def set_mp(self, list_mp):
        self.menu_mp.set_label("Message Privés (" + str(len(list_mp)) + ")")

        submenu = gtk.Menu()

        for mp in list_mp:
            if mp.date[0] == "I":
                item = gtk.MenuItem("[" + mp.topic + "] par " + mp.username + " " + mp.date)
            else:
                item = gtk.MenuItem("[" + mp.topic + "] par " + mp.username + " le " + mp.date)

            item.connect('activate', self.menuitem_response_website, self.URL + mp.href)

            item.show()
            submenu.append(item)

        self.menu_mp.set_submenu(submenu)

    def set_notifications_forums(self, list_notif):
        self.menu_notif.set_label("Notifications (" + str(len(list_notif)) + ")")

        submenu = gtk.Menu()

        for notif in list_notif:
            if notif.date[0] == "I":
                item = gtk.MenuItem("[" + notif.topic + "] par " + notif.username + " " + notif.date)
            else:
                item = gtk.MenuItem("[" + notif.topic + "] par " + notif.username + " le " + notif.date)

            item.connect('activate', self.menuitem_response_website, self.URL + notif.href)

            item.show()
            submenu.append(item)

        self.menu_notif.set_submenu(submenu)

    def set_icon_app(self, mode):
        # mode possible :
        # icon
        # logout
        # parsing
        self.ind.set_icon("zdsindicator-" + mode)

    def set_menu_username(self, username):
        self.username = username
        self.menu_username.set_label(username)
        self.menu_username.show()

    def show_menu_item_error_server(self, error_label, show_connection=False):
        self.menu_serveur_error.set_label(error_label)
        self.menu_serveur_error.show()
        self.menu_mp.hide()
        self.menu_notif.hide()
        self.menu_username.hide()
        if show_connection:
            self.menu_auth.show()

    def show_menu_item_normal(self):
        self.menu_serveur_error.hide()
        self.menu_mp.show()
        self.menu_notif.show()
        self.menu_auth.hide()