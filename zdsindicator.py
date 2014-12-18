#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests
import os
import sys
import webbrowser
import bs4
import pynotify
import appindicator
import gtk
import gobject
import threading
import gconf
from gconf import VALUE_BOOL, VALUE_INT, VALUE_STRING, VALUE_FLOAT
from types import BooleanType, StringType, IntType, FloatType

URL = 'http://localhost:8000'
client = requests.Session()

app_name = 'ZdsIndicator'
app_identifier = 'zdsindicator'
icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icons')
update_time = 5000

# default activate notifications
activate_notifications = False

gobject.threads_init()

##############################
# REQUESTS
##############################


def auth():
    # première requète pour récuperer le csrftoken
    try:
        s = client.get(URL+'/membres/connexion/')
    except requests.exceptions.RequestException:
        print "Probleme connexion"
        sys.exit(1)

    csrftoken = s.cookies['csrftoken']

    params = {
        'username': 'admin',
        'password': 'admin',
        'csrfmiddlewaretoken': csrftoken
    }

    # requète d'authentification
    try:
        client.post(URL+'/membres/connexion/', data=params)
    except requests.exceptions.RequestException:
        print "Probleme connexion"
        sys.exit(1)


def get_home_page():
    try:
        response = client.get(URL)
    except requests.exceptions.RequestException:
        print "Probleme connexion"
        sys.exit(1)
    return response.content


def get_mp(soup):
    list_mp = []

    for node in soup.findAll(attrs={'class': 'notifs-links'}):
        for li_mp in node.div.div.ul.find_all('li'):
            tmp = Notification(
                href=li_mp.a['href'],
                username=li_mp.a.contents[3].string,
                date=li_mp.a.contents[5].string,
                topic=li_mp.a.contents[7].string,
                avatar=li_mp.a.img['src']
            )
            list_mp.append(tmp)
    return list_mp


def get_notifications_forum(soup):
    list_notif = []

    for node in soup.findAll(attrs={'class': 'notifs-links'}):
        for li_notif in node.contents[3].div.ul.find_all('li'):
            if not li_notif.get('class')[0] == 'dropdown-empty-message':
                tmp = Notification(
                    href=li_notif.a['href'],
                    username=li_notif.a.contents[3].string,
                    date=li_notif.a.contents[5].string,
                    topic=li_notif.a.contents[7].string,
                    avatar=li_notif.a.img['src']
                )
                list_notif.append(tmp)
    return list_notif

##############################
# GCONF
##############################


class GConf:
    def __init__(self, appname, allowed={}):
        self._domain = '/apps/%s/' % appname
        self._allowed = allowed
        self._gconf_client = gconf.client_get_default()

    def __getitem__(self, attr):
        return self.get_value(attr)

    def __setitem__(self, key, val):
        allowed = self._allowed
        if key in allowed:
            if key not in allowed[key]:
                ', '.join(allowed[key])
                return False
        self.set_value(key, val)

    def _get_type(self, key):
        keytype = type(key)
        if keytype == BooleanType:
            return 'bool'
        elif keytype == StringType:
            return 'string'
        elif keytype == IntType:
            return 'int'
        elif keytype == FloatType:
            return 'float'
        else:
            return None

    # Public functions
    def set_allowed(self, allowed):
        self._allowed = allowed

    def set_domain(self, domain):
        self._domain = domain

    def get_domain(self):
        return self._domain

    def get_gconf_client(self):
        return self._gconf_client

    def get_value(self, key):
        """returns the value of key 'key' """
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        value = self._gconf_client.get(self._domain + key)
        if value is not None:
            valuetype = value.type
            if valuetype == VALUE_BOOL:
                return value.get_bool()
            elif valuetype == VALUE_INT:
                return value.get_int()
            elif valuetype == VALUE_STRING:
                return value.get_string()
            elif valuetype == VALUE_FLOAT:
                return value.get_float()
            else:
                return None
        else:
            return None

    def set_value(self, key, value):
        """sets the value of key 'key' to 'value' """
        value_type = self._get_type(value)
        if value_type is not None:
            if '/' in key:
                raise 'GConfError', 'key must not contain /'
            func = getattr(self._gconf_client, 'set_' + value_type)
            apply(func, (self._domain + key, value))

    def get_string(self, key):
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        return self._gconf_client.get_string(self._domain + key)

    def set_string(self, key, value):
        if type(value) != StringType:
            raise 'GConfError', 'value must be a string'
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        self._gconf_client.set_string(self._domain + key, value)

    def get_bool(self, key):
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        return self._gconf_client.get_bool(self._domain + key)

    def set_bool(self, key, value):
        if type(value) != IntType and (key != 0 or key != 1):
            raise 'GConfError', 'value must be a boolean'
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        self._gconf_client.set_bool(self._domain + key, value)

    def get_int(self, key):
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        return self._gconf_client.get_int(self._domain + key)

    def set_int(self, key, value):
        if type(value) != IntType:
            raise 'GConfError', 'value must be an int'
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        self._gconf_client.set_int(self._domain + key, value)

    def get_float(self, key):
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        return self._gconf_client.get_float(self._domain + key)

    def set_float(self, key, value):
        if type(value) != FloatType:
            raise 'GConfError', 'value must be a float'
        if '/' in key:
            raise 'GConfError', 'key must not contain /'
        self._gconf_client.set_float(self._domain + key, value)

##############################
# CORE CLASS
##############################


class Notification(object):
    def __init__(self, href, username, date, topic, avatar):
        self.href = href
        self.username = username
        self.date = date
        self.topic = topic
        self.avatar = avatar


class ConnectDialog(object):
    def __init__(self):
        pass


class ConfigureDialog(object):
    def __init__(self, widget):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title('Paramètres')
        self.window.connect('delete_event', self.cancel_dialog)
        self.window.connect('key-press-event', self.keypress)
        self.window.set_border_width(10)

        vbox_window = gtk.VBox(True, 2)
        self.window.add(vbox_window)
        vbox_window.show()

        vbox_check = gtk.VBox(True, 2)
        vbox_window.pack_start(vbox_check, True, True, 2)
        vbox_check.show()

        self.activate_notifications_check = gtk.CheckButton("Afficher les notifications")
        vbox_check.pack_start(self.activate_notifications_check, True, True, 2)
        self.activate_notifications_check.show()
        self.activate_notifications_check.set_active(activate_notifications)

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

    def save(self, widget, data):
        global activate_notifications

        zdsindicator_gconf['activate_notifications'] = self.activate_notifications_check.get_active()
        activate_notifications = self.activate_notifications_check.get_active()

        print 'save configuration'


class ZDSNotification(object):
    def __init__(self):

        global activate_notifications

        self.ind = appindicator.Indicator(app_name, 'zdsindicator', appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.ind.set_icon_theme_path(icon_path)
        self.ind.set_icon("zdsindicator-icon")

        # initialisation des paramètres
        if zdsindicator_gconf['activate_notifications'] is not None:
            activate_notifications = zdsindicator_gconf['activate_notifications']

        self.menu = gtk.Menu()

        self.mp_menu = gtk.MenuItem('Messages Privés')
        self.mp_menu.show()
        self.menu.append(self.mp_menu)

        self.notif_menu = gtk.MenuItem('Notifications')
        self.notif_menu.show()
        self.menu.append(self.notif_menu)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        menu_configure = gtk.MenuItem('Paramètres')
        menu_configure.show()
        menu_configure.connect('activate', ConfigureDialog)
        self.menu.append(menu_configure)

        quit_menu = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_menu.connect("activate", self.quit)
        quit_menu.show()
        self.menu.append(quit_menu)

        self.menu.show()
        self.ind.set_menu(self.menu)

        pynotify.init('ZDSNotification')
        self.timeout_id = gobject.timeout_add(update_time, self.update)

    def quit(self, widget, data=None):
        gtk.main_quit()

    def send_mp_notification(self, nb_mp):
        if nb_mp > 0:
            image = icon_path+'/zdsindicator-mp.png'
            n = pynotify.Notification('Zeste de Savoir', str(nb_mp)+' messages privés non lus', image)
            n.show()

    def send_notif_notification(self, nb_notif):
        if nb_notif > 0:
            image = icon_path+'/zdsindicator-forums.png'
            n = pynotify.Notification('Zeste de Savoir', str(nb_notif)+' notifications', image)
            n.show()

    def set_mp(self, list_mp):
        self.mp_menu.set_label("Message Privés ("+str(len(list_mp))+")")

        submenu = gtk.Menu()

        for mp in list_mp:
            if mp.date[0] == "I":
                item = gtk.MenuItem("["+mp.topic+"] par "+mp.username+" "+mp.date)
            else:
                item = gtk.MenuItem("["+mp.topic+"] par "+mp.username+" le "+mp.date)

            item.connect('activate', self.menuitem_response_website, URL+mp.href)

            item.show()
            submenu.append(item)

        self.mp_menu.set_submenu(submenu)

    def set_notifications_forums(self, list_notif):
        self.notif_menu.set_label("Notifications ("+str(len(list_notif))+")")

        submenu = gtk.Menu()

        for notif in list_notif:
            if notif.date[0] == "I":
                item = gtk.MenuItem("["+notif.topic+"] par "+notif.username+" "+notif.date)
            else:
                item = gtk.MenuItem("["+notif.topic+"] par "+notif.username+" le "+notif.date)

            item.connect('activate', self.menuitem_response_website, URL+notif.href)

            item.show()
            submenu.append(item)

        self.notif_menu.set_submenu(submenu)

    def menuitem_response_website(self, data, url):
        webbrowser.open(url)

    def update(self):
        print "update"
        UpdateThread().start()
        return True


class UpdateThread(threading.Thread):
    def __init__(self):
        super(UpdateThread, self).__init__()

    def connect(self):
        auth()

    def run(self):
        self.connect()
        html_output = get_home_page()
        # TODO dégager bsoup
        soup = bs4.BeautifulSoup(html_output)
        list_mp = get_mp(soup)
        list_notif = get_notifications_forum(soup)

        # détruit le tree pour libérer la mémoire
        soup.decompose()

        gobject.idle_add(z.set_mp, list_mp)
        gobject.idle_add(z.set_notifications_forums, list_notif)

        if activate_notifications:
            z.send_mp_notification(len(list_mp))
            z.send_notif_notification(len(list_notif))


if __name__ == "__main__":
    zdsindicator_gconf = GConf(app_identifier)
    z = ZDSNotification()
    z.update()
    gtk.main()
