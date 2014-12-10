#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests
import os
import webbrowser
import bs4
import pynotify
import appindicator
import gtk
import gobject

URL = 'http://localhost:8000'
global client

app_name = 'ZdsIndicator'
app_identifier = 'zdsindicator'
icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icons')
print icon_path
update_time = 10000


##############################
# REQUESTS
##############################

def connect(client):
    s = client.get(URL+'/membres/connexion/')
    csrftoken = s.cookies['csrftoken']
    
    params = {
        'username': 'admin',
        'password': 'admin',
        'csrfmiddlewaretoken': csrftoken
    }

    s = client.post(URL+'/membres/connexion/', data=params)

def get_home_page(client):
    response = client.get(URL)
    return response.content
    
def get_mp(html_output):
    soup = bs4.BeautifulSoup(html_output)
    list_mp = []

    for node in soup.findAll(attrs={'class': 'notifs-links'}):
        for li_mp in node.div.div.ul.find_all('li'):
            tmp = Notification(
                    href=li_mp.a['href'],
                    username= li_mp.a.contents[3].string,
                    date= li_mp.a.contents[5].string,
                    topic= li_mp.a.contents[7].string,
                    avatar = li_mp.a.img['src']
            )
            list_mp.append(tmp)
    return list_mp

def get_notifications_forum(html_output):
    soup = bs4.BeautifulSoup(html_output)
    list_notif = []
    
    for node in soup.findAll(attrs={'class': 'notifs-links'}):
        for li_notif in node.contents[3].div.ul.find_all('li'):
            if not li_notif.get('class')[0] == 'dropdown-empty-message':
                tmp = Notification(
                        href=li_notif.a['href'],
                        username= li_notif.a.contents[3].string,
                        date= li_notif.a.contents[5].string,
                        topic= li_notif.a.contents[7].string,
                        avatar = li_notif.a.img['src']
                )
                list_notif.append(tmp)
    return list_notif

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

class ZDSNotification(object):
    def __init__(self):
        self.ind = appindicator.Indicator(app_name,'zdsindicator', appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.ind.set_icon_theme_path(icon_path)
        self.ind.set_icon("zdsindicator-icon")

        self.menu = gtk.Menu()

        self.mp_menu = gtk.MenuItem('Messages Privés')
        self.mp_menu.show()
        self.menu.append(self.mp_menu)
        
        self.notif_menu = gtk.MenuItem('Notifications')
        self.notif_menu.show()
        self.menu.append(self.notif_menu)

        image = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        image.connect("activate", self.quit)
        image.show()
        self.menu.append(image)
        
        self.menu.show()
        self.ind.set_menu(self.menu)
        
        pynotify.init('ZDSNotification')
        gobject.timeout_add(update_time, self.update)

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


    def setMP(self, list_mp=[]):
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

    def setNotificationsForums(self, list_notif=[]):
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
        connect(client)
        html_homepage = get_home_page(client)
        list_mp = get_mp(html_homepage)
        list_notif = get_notifications_forum(html_homepage)
        self.setMP(list_mp)
        self.setNotificationsForums(list_notif)
        self.send_mp_notification(len(list_mp))
        self.send_notif_notification(len(list_notif))

        return True

if __name__ == "__main__":
    client = requests.Session()
    z = ZDSNotification()
    z.update()
    gtk.main()
