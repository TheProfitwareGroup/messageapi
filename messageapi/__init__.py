#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'

from importlib import import_module


def messageapi_factory(messageapi_classname, class_params):
    global class_object
    class_parts = messageapi_classname.split('.')
    module_name = '.'.join(class_parts[:-1])
    class_name = class_parts[-1]
    module = import_module(module_name)
    module_class = getattr(module, class_name)

    class_kwargs = dict(class_params)
    class_object = module_class(**class_kwargs)
    return True


def send_message(send_params):
    global class_object
    send_kwargs = dict(send_params)
    class_object.send(**send_kwargs)
    return True
