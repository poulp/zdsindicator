#!/usr/bin/env python
# -*- coding: utf8 -*-

# original code : https://github.com/nicolas-raoul/Feedindicator

import gconf
from gconf import VALUE_BOOL, VALUE_INT, VALUE_STRING, VALUE_FLOAT
from types import BooleanType, StringType, IntType, FloatType


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
