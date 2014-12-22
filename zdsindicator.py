#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests
import os
import sys
import webbrowser
import pynotify
import appindicator
import gtk
import gobject
import threading
import gconf
import gc
import lxml.html
from gconf import VALUE_BOOL, VALUE_INT, VALUE_STRING, VALUE_FLOAT
from types import BooleanType, StringType, IntType, FloatType

URL = 'http://localhost:8000'

client = requests.Session()

app_name = 'ZdsIndicator'
app_identifier = 'zdsindicator'
icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icons')

stoptimer = False
username = ""

# temp de rafraichissement par défaut en ms
refresh_time = 10000

# default activate notifications
activate_notifications = False

gobject.threads_init()

##############################
# REQUESTS
##############################


def auth(username, password):

    is_auth = False
    # première requète pour récuperer le csrftoken
    try:
        s = client.get(URL+'/membres/connexion/')
    except requests.exceptions.RequestException as e:
        raise e

    csrftoken = s.cookies['csrftoken']

    params = {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrftoken
    }

    # requète d'authentification
    try:
        s = client.post(URL+'/membres/connexion/', data=params)
        if s.url == URL+"/":
            is_auth = True
    except requests.exceptions.RequestException as e:
        raise e

    return is_auth


def get_home_page():
    response = client.get(URL)
    return response.content


def get_member_connexion_page():
    try:
        response = client.get(URL+"/membres/connexion")
    except requests.exceptions.RequestException:
        print "Probleme connexion"
        sys.exit(1)
    return response.content

##############################
# PARSING
##############################


def is_auth_from_homepage(root):
    is_auth = False

    result = root.find_class("unlogged")
    if result == []:
        is_auth = True

    return is_auth

def get_mp(root):
    list_mp = []

    result = root.find_class("notifs-links")
    if not result:
        return []

    li_mp = result[0].getchildren()[0].getchildren()[1].getchildren()[1].getchildren()
    for mp in li_mp:

        if mp.get('class') == 'dropdown-empty-message':
            return []

        tmp = Notification(
            href=mp.getchildren()[0].get('href'),
            username=mp.getchildren()[0].getchildren()[1].text,
            date=mp.getchildren()[0].getchildren()[2].text,
            topic=mp.getchildren()[0].getchildren()[3].text,
            avatar=mp.getchildren()[0].getchildren()[0].get('src')
        )
        list_mp.append(tmp)

    return list_mp


def get_notifications_forum(root):
    list_notif = []

    result = root.find_class("notifs-links")
    if not result:
        return []

    li_notif = result[0].getchildren()[1].getchildren()[1].getchildren()[1]

    for notif in li_notif:

        if notif.get('class') == 'dropdown-empty-message':
            return []

        tmp = Notification(
            href=notif.getchildren()[0].get('href'),
            username=notif.getchildren()[0].getchildren()[1].text,
            date=notif.getchildren()[0].getchildren()[2].text,
            topic=notif.getchildren()[0].getchildren()[3].text,
            avatar=notif.getchildren()[0].getchildren()[0].get('src')
        )
        list_notif.append(tmp)

    return list_notif

##############################
# NOTIFICATIONS DESKTOP
##############################


def send_mp_notification(nb_mp):
    if nb_mp > 0:
        image = icon_path+'/zdsindicator-mp.png'
        n = pynotify.Notification('Zeste de Savoir', str(nb_mp)+' messages privés non lus', image)
        n.show()


def send_notif_notification(nb_notif):
    if nb_notif > 0:
        image = icon_path+'/zdsindicator-forums.png'
        n = pynotify.Notification('Zeste de Savoir', str(nb_notif)+' notifications', image)

        n.show()

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


class AuthenticationtDialog(object):
    def __init__(self, widget):

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
            response = auth(self.entry_username.get_text(), self.entry_password.get_text())
            if response:
                self.dialog.destroy()
                UpdateThread().start()
                z.set_loop_update()
            else:
                self.entry_username.set_text("")
                self.entry_password.set_text("")


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

        hbox_refresh_scale = gtk.VBox(False, 0)
        vbox_window.pack_start(hbox_refresh_scale, False, True, 0)
        hbox_refresh_scale.show()

        self.label_refresh_scale = gtk.Label("Rafraichir toutes les 10 minutes")
        hbox_refresh_scale.pack_start(self.label_refresh_scale, False, False, 0)
        self.label_refresh_scale.show()

        button_refresh_scale = gtk.Adjustment(int(refresh_time/60000), 1.0, 90.0, 1.0, 10.0, 0.0)
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

    def set_refresh_scale_label(self, widget):
        value = widget.get_value()
        if int(value) == 1:
            self.label_refresh_scale.set_text("Rafraichir toutes les minutes")
        else:
            self.label_refresh_scale.set_text("Rafraichir toutes les "+str(int(value))+" minutes")

    def save(self, widget, data):
        global activate_notifications
        global refresh_time

        overridetime = False

        zdsindicator_gconf['activate_notifications'] = self.activate_notifications_check.get_active()
        activate_notifications = self.activate_notifications_check.get_active()

        if not refresh_time == int(self.scaletimer.get_value()*60000):
            zdsindicator_gconf['refresh_time'] = int(self.scaletimer.get_value()*60000)
            refresh_time = int(self.scaletimer.get_value()*60000)

        self.window.hide()

        gobject.source_remove(z.timeout_id)
        z.set_loop_update()


class ZDSNotification(object):
    def __init__(self):

        global activate_notifications
        global refresh_time

        self.ind = appindicator.Indicator(app_name, 'zdsindicator', appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.ind.set_icon_theme_path(icon_path)
        self.ind.set_icon("zdsindicator-icon")

        self.stopupdate = False
        self.timeout_id = -1

        # initialisation des paramètres
        if zdsindicator_gconf['activate_notifications'] is not None:
            activate_notifications = zdsindicator_gconf['activate_notifications']

        #if zdsindicator_gconf['refresh_time'] is not None:
            #refresh_time = zdsindicator_gconf['refresh_time']

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
        self.menu_auth.connect('activate', AuthenticationtDialog)
        self.menu.append(self.menu_auth)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        menu_refresh = gtk.MenuItem('Rafraichir')
        menu_refresh.show()
        menu_refresh.connect('activate', self.refresh)
        self.menu.append(menu_refresh)

        menu_configure = gtk.MenuItem('Paramètres')
        menu_configure.show()
        menu_configure.connect('activate', ConfigureDialog)
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

    def set_loop_update(self):
        self.timeout_id = gobject.timeout_add(refresh_time, self.update)


    def set_mp(self, list_mp):
        self.menu_mp.set_label("Message Privés ("+str(len(list_mp))+")")

        submenu = gtk.Menu()

        for mp in list_mp:
            if mp.date[0] == "I":
                item = gtk.MenuItem("["+mp.topic+"] par "+mp.username+" "+mp.date)
            else:
                item = gtk.MenuItem("["+mp.topic+"] par "+mp.username+" le "+mp.date)

            item.connect('activate', self.menuitem_response_website, URL+mp.href)

            item.show()
            submenu.append(item)

        self.menu_mp.set_submenu(submenu)

    def set_notifications_forums(self, list_notif):
        self.menu_notif.set_label("Notifications ("+str(len(list_notif))+")")

        submenu = gtk.Menu()

        for notif in list_notif:
            if notif.date[0] == "I":
                item = gtk.MenuItem("["+notif.topic+"] par "+notif.username+" "+notif.date)
            else:
                item = gtk.MenuItem("["+notif.topic+"] par "+notif.username+" le "+notif.date)

            item.connect('activate', self.menuitem_response_website, URL+notif.href)

            item.show()
            submenu.append(item)

        self.menu_notif.set_submenu(submenu)

    def menuitem_response_website(self, data, url):
        webbrowser.open(url)

    def refresh(self, widget):
        print "refresh"
        UpdateThread().start()

    def update(self, timeoverride=False):

        if self.stopupdate:
            self.stopupdate = False
            return False

        if timeoverride:
            self.timeout_id = gobject.timeout_add(refresh_time, self.update)
            return False

        UpdateThread().start()
        return True

    def set_icon_app(self, mode):
        # mode possible :
        # icon
        # logout
        # parsing

        self.ind.set_icon("zdsindicator-"+mode)

    def show_menu_item_error_server(self, error_label, show_connection=False):
        self.menu_serveur_error.set_label(error_label)
        self.menu_serveur_error.show()
        self.menu_mp.hide()
        self.menu_notif.hide()
        if show_connection:
            self.menu_auth.show()

    def show_menu_item_normal(self):
        self.menu_serveur_error.hide()
        self.menu_mp.show()
        self.menu_notif.show()
        self.menu_auth.hide()


class UpdateThread(threading.Thread):
    def __init__(self):
        super(UpdateThread, self).__init__()

    def run(self):
        print "update"
        gobject.idle_add(z.show_menu_item_normal)
        gobject.idle_add(z.set_icon_app, "parsing")

        try:
            html_output = get_home_page()
        except requests.exceptions.RequestException :
            gobject.idle_add(z.show_menu_item_error_server, "Problème de connexion serveur")
            return

        root = lxml.html.fromstring(html_output)

        if is_auth_from_homepage(root):

            try:
                list_mp = get_mp(root)
                list_notif = get_notifications_forum(root)
            except requests.exceptions.RequestException :
                gobject.idle_add(z.show_menu_item_error_server, "Problème de connexion serveur")
                return

            gobject.idle_add(z.set_mp, list_mp)
            gobject.idle_add(z.set_notifications_forums, list_notif)
            gobject.idle_add(z.set_icon_app, "icon")

            if activate_notifications:
                send_mp_notification(len(list_mp))
                send_notif_notification(len(list_notif))
        else:
            try:
                is_auth = auth(username, "")
                if is_auth:
                    try:
                        html_output = get_home_page()
                    except requests.exceptions.RequestException :
                        gobject.idle_add(z.show_menu_item_error_server, "Problème de connexion serveur")
                        return

                    root = lxml.html.fromstring(html_output)

                    try:
                        list_mp = get_mp(root)
                        list_notif = get_notifications_forum(root)
                    except requests.exceptions.RequestException :
                        gobject.idle_add(z.show_menu_item_error_server, "Problème de connexion serveur")
                        return

                    gobject.idle_add(z.set_mp, list_mp)
                    gobject.idle_add(z.set_notifications_forums, list_notif)
                    gobject.idle_add(z.set_icon_app, "icon")

                    if activate_notifications:
                        send_mp_notification(len(list_mp))
                        send_notif_notification(len(list_notif))
                else:
                    gobject.idle_add(z.show_menu_item_error_server, "Vous n'êtes pas authentifié", True)
                    gobject.idle_add(z.set_icon_app, "logout")
                    gobject.source_remove(z.timeout_id)

            except requests.exceptions.RequestException as e:
                gobject.idle_add(z.show_menu_item_error_server, "Problème de connexion serveur")
                return


if __name__ == "__main__":
    if not gc.isenabled():
        gc.enable()
    zdsindicator_gconf = GConf(app_identifier)
    z = ZDSNotification()
    z.update()
    gtk.main()