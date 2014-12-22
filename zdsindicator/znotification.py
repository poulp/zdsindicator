#!/usr/bin/env python
# -*- coding: utf8 -*-

import pynotify


def send_mp_notification(nb_mp, icon_path):
    if nb_mp > 0:
        image = icon_path+'/zdsindicator-mp.png'
        n = pynotify.Notification('Zeste de Savoir', str(nb_mp)+' messages privés non lus', image)
        n.show()


def send_notif_notification(nb_notif, icon_path):
    if nb_notif > 0:
        image = icon_path+'/zdsindicator-forums.png'
        n = pynotify.Notification('Zeste de Savoir', str(nb_notif)+' notifications', image)
        n.show()