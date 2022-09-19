#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
python class to control relayDuino
"""
import sys
import os
import platform
import threading
import re
# import time
from usbasp_uart import USBasp_UART, USBaspERROR
# from threading import Thread
try:
    from PyQt5.QtCore import (QObject)
except ImportError as err:
    raise SystemExit("pip install PyQt5\n %s" % err)


# class Relay(Thread):
class Relay(QObject):
    __version__ = "20220412"

    def __init__(self, parent=None):
        self._DEBUG = 1
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)
        
        try:
            self.relay = USBasp_UART()
        except USBaspERROR as err:
            # print("ERROR: %s" % err)
            raise USBaspERROR("%s" % err)

        self.log(self.relay)

    def setPower(self, sPin, sSw):
        '''set Power Pin On/Off'''
        if (type(sPin) is int):
            sPin = str(sPin)
        if (type(sSw) is int):
            sSw = str(sSw)
        
        self.relay.write_all("set %s %s\n" % (sPin, sSw))
        self.stdout = self.relay.readline()
        if (self.stdout):
            # print(self.stdout)
            s = self.stdout.decode(encoding='UTF-8')
            if (":" in s):
                # expect s: Power 1 status: OFF/ON
                x, s = s.split(':')
                v = s.split()

                if v[0] in ['ON']:
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0

    def getPower(self, sPin):
        '''get Power Pin status return 0=OFF , 1=ON'''
        if (type(sPin) is int):
            sPin = str(sPin)
        
        self.relay.write_all("get %s\n" % (sPin))
        self.stdout = self.relay.readline()
        if (self.stdout):
            # print(self.stdout)
            s = self.stdout.decode(encoding='UTF-8')
            if (":" in s):
                # expect s: Power 1 status: ON/OFF
                x, s = s.split(':')
                v = s.split()
                if v[0] in ['ON']:
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0

    def getMaxPowerNum(self):
        '''get Max supported Power Pin Number,
            return: String of number
        '''
        self.relay.write_all("max\n")
        self.stdout = self.relay.readline()
        if (self.stdout):
            s = self.stdout.decode(encoding='UTF-8')
            rs = re.findall(r'\d+', s)
            if len(rs) > 0:
                try:
                    return rs[0]
                except Exception as err:
                    self.log("ERROR: %s" % err)
            else:
                return '0'
        else:
            return '0'

    def log(self, msg, lv=2):
        if self._DEBUG > lv:
            print("[%s]%s" % (self.__class__.__name__, msg))

    def traceback(self, err=None):
        exc_type, exc_obj, tb = sys.exc_info()
        # This function returns the current
        # line number set in the traceback object.
        lineno = tb.tb_lineno
        print("%s: %s - %s - Line: %s" % (self.__class__.__name__,
                                          exc_type, exc_obj, lineno))
