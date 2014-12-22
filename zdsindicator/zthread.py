#!/usr/bin/env python
# -*- coding: utf8 -*-

import threading
import gobject
import requests
from lxml import html

from zrequest import get_home_page, auth
from znotification import send_mp_notification, send_notif_notification
from zparsing import is_auth_from_homepage, get_mp, get_notifications_forum


class UpdateThread(threading.Thread):
    def __init__(self, indicator):
        super(UpdateThread, self).__init__()
        self.indicator = indicator

    def run(self):
        print "update"
        gobject.idle_add(self.indicator.show_menu_item_normal)
        gobject.idle_add(self.indicator.set_icon_app, "parsing")

        try:
            html_output = get_home_page(self.indicator.client, self.indicator.URL)
        except requests.exceptions.RequestException:
            gobject.idle_add(self.indicator.show_menu_item_error_server, "Problème de connexion serveur")
            return

        root = html.fromstring(html_output)

        if is_auth_from_homepage(root):

            try:
                list_mp = get_mp(root)
                list_notif = get_notifications_forum(root)
            except requests.exceptions.RequestException:
                gobject.idle_add(self.indicator.show_menu_item_error_server, "Problème de connexion serveur")
                return

            gobject.idle_add(self.indicator.set_mp, list_mp)
            gobject.idle_add(self.indicator.set_notifications_forums, list_notif)
            gobject.idle_add(self.indicator.set_icon_app, "icon")

            if self.indicator.activate_notifications:
                send_mp_notification(len(list_mp), self.indicator.icon_path)
                send_notif_notification(len(list_notif), self.indicator.icon_path)
        else:
            try:
                is_auth = auth(self.indicator.client, self.indicator.URL, self.indicator.username, "")
                if is_auth:
                    try:
                        html_output = get_home_page(self.indicator.client, self.indicator.URL)
                    except requests.exceptions.RequestException:
                        gobject.idle_add(self.indicator.show_menu_item_error_server, "Problème de connexion serveur")
                        return

                    root = html.fromstring(html_output)

                    try:
                        list_mp = get_mp(root)
                        list_notif = get_notifications_forum(root)
                    except requests.exceptions.RequestException:
                        gobject.idle_add(self.indicator.show_menu_item_error_server, "Problème de connexion serveur")
                        return

                    gobject.idle_add(self.indicator.set_mp, list_mp)
                    gobject.idle_add(self.indicator.set_notifications_forums, list_notif)
                    gobject.idle_add(self.indicator.set_icon_app, "icon")

                    if self.indicator.activate_notifications:
                        send_mp_notification(len(list_mp), self.indicator.icon_path)
                        send_notif_notification(len(list_notif), self.indicator.icon_path)
                else:
                    gobject.idle_add(self.indicator.show_menu_item_error_server, "Vous n'êtes pas authentifié", True)
                    gobject.idle_add(self.indicator.set_icon_app, "logout")
                    gobject.source_remove(self.indicator.timeout_id)

            except requests.exceptions.RequestException:
                gobject.idle_add(self.indicator.show_menu_item_error_server, "Problème de connexion serveur")
                return
