#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests


def auth(client, base_url, username, password):

    is_auth = False
    # première requète pour récuperer le csrftoken
    try:
        s = client.get(base_url+'/membres/connexion/')
    except requests.exceptions.RequestException as e:
        raise e

    csrftoken = s.cookies['csrftoken']

    params = {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrftoken
    }

    # si https
    client.headers.update({'Referer': base_url+'/membres/connexion/'})

    # requète d'authentification
    try:
        s = client.post(base_url+'/membres/connexion/', data=params)
        if s.url == base_url+"/":
            is_auth = True
    except requests.exceptions.RequestException as e:
        raise e

    return is_auth


def get_home_page(client, base_url):
    response = client.get(base_url)
    return response.content


def get_member_connexion_page(client, base_url):
    response = client.get(base_url+"/membres/connexion")
    return response.content