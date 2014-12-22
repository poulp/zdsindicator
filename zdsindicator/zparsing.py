#!/usr/bin/env python
# -*- coding: utf8 -*-


class NotificationItem(object):
    def __init__(self, href, username, date, topic, avatar):
        self.href = href
        self.username = username
        self.date = date
        self.topic = topic
        self.avatar = avatar


def is_auth_from_homepage(root):
    is_auth = False

    result = root.find_class("unlogged")
    if not result:
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

        tmp = NotificationItem(
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

        tmp = NotificationItem(
            href=notif.getchildren()[0].get('href'),
            username=notif.getchildren()[0].getchildren()[1].text,
            date=notif.getchildren()[0].getchildren()[2].text,
            topic=notif.getchildren()[0].getchildren()[3].text,
            avatar=notif.getchildren()[0].getchildren()[0].get('src')
        )
        list_notif.append(tmp)

    return list_notif