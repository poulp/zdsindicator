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


def send_notif(nb_mp, nb_notif, icon_path):
    title = 'Zeste de Savoir'
    content = ''
    image = icon_path+'/zdsindicator-icon.png'

    if nb_mp:
        if nb_mp > 1:
            content += str(nb_mp)+' messages privés non lus'
        else:
            content += str(nb_mp)+' message privé non lu'

    if nb_notif:
        if nb_mp:
            content += '\n'

        if nb_notif > 1:
            content += str(nb_notif)+' notifications'
        else:
            content += str(nb_notif)+' notification'

    if nb_notif or nb_mp:
        n = pynotify.Notification(title, content, image)
        n.show()