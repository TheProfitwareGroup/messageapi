#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2014, The Profitware Group'


class AbstractPlugin(dict):
    """Abstract plugin interface."""

    def __getattr__(self, item):
        try:
            return self.__getattribute__(item)
        except AttributeError:
            return self[item]


class AbstractSenderPlugin(AbstractPlugin):
    def send(self, **kwargs):
        raise NotImplementedError


class AbstractReceiverPlugin(AbstractPlugin):
    def receive(self, **kwargs):
        raise NotImplementedError
