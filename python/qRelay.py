#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 13:47:30 2017

@author: lab
"""
import os
import sys
import time
import signal
try:
    from PyQt5.QtCore import (QThread, pyqtSlot, QSize)
    from PyQt5.QtGui import (QIcon)
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                                 QLabel)
    from PyQt5 import (QtCore)
    from PyQt5.uic import loadUi
except ImportError as err:
    raise SystemExit("pip3 install PyQt5\n%s" % err)

from relay import Relay


class MyApp(QApplication):
    """wrapper to the QApplication """

    def __init__(self, argv=None):
        super(MyApp, self).__init__(argv)

    def event(self, event_):
        """handle event """
        return QApplication.event(self, event_)


def signal_handler(signal_, frame):
    """signal handler"""
    print('You pressed Ctrl+C!')
    sys.exit(0)


def sig_segv(signum, frame):
    print("segfault: %s" % frame)


class MainWindow(QMainWindow):
    __version__ = "20220209"

    def __init__(self):
        super(MainWindow, self).__init__()
        if getattr(sys, 'frozen', False):
            # we are running in a |PyInstaller| bundle
            basedir = sys._MEIPASS
        else:
            # we are running in a normal Python environment
            basedir = os.path.dirname(__file__)
        img_ico = os.path.join(basedir, 'images', 'avrelay.ico')
        img_ON = os.path.join(basedir, 'images', 'on.png')
        img_OFF = os.path.join(basedir, 'images', 'off.png')
        self.img_normal = os.path.abspath(os.path.join(basedir, 'images', 'normal.png'))

        self.setWindowIcon(QIcon(img_ico))
        loadUi(os.path.join(basedir, 'qRelay.ui'), self)

        self.imgON = QIcon(img_ON)
        self.imgOFF = QIcon(img_OFF)
        
        try:
            self.avrelay = Relay()
        except Exception as err:
            self.avrelay = None
            print("%s" % err)
        if self.avrelay:
            v = self.avrelay.getMaxPowerNum()
            print("Support Max power num: %s" % v)
            if int(v) <= 0:
                msg = 'ERROR:\nNot found supported power pin on avrelay'
                self.createNotice(msg)
                return
            self.button = {}
            for i in range(1, int(v) + 1):
                self.createButton(i)
        else:
            msg = 'ERROR:\nNot found avrelay device!!'
            self.createNotice(msg)

    def createNotice(self, msg):
        self.lbNotice = QLabel(msg)
        self.saLayout.addWidget(self.lbNotice)

    def createButton(self, pPin):
        self.button[pPin] = QPushButton('%s' % pPin, self)
        style = "QPushButton { "
        # style += "background: url(images/normal.png);"
        style += "background-repeat: repeat-n;"
        style += "border-width: 1px; border-style: solid; border-color: white;"
        style += "}"
        self.button[pPin].setStyleSheet(style)
        # self.button[pPin].setMaximumWidth(100)
        # self.button[pPin].setMaximumHeight(50)
        self.button[pPin].setIcon(self.getImg(pPin))
        self.button[pPin].setIconSize(QSize(48, 48))
        self.button[pPin].clicked.connect(self.PowerSwitch)
        # self.button[pPin].setCheckable(False)
        # self.saContents.setWidget(self.button[pPin])
        self.saLayout.addWidget(self.button[pPin])

    def getImg(self, pPin):
        if self.avrelay.getPower(pPin):
            img = self.imgON
        else:
            img = self.imgOFF

        return img

    @pyqtSlot(bool)
    def PowerSwitch(self, checked):
        # print('PowerSwitch: %s' % checked)
        sPin = self.sender().text()
        if (self.getPowerStatus(sPin)):
            self.setPowerStatus(sPin, '0')
        else:
            self.setPowerStatus(sPin, '1')

        self.updateStatus(sPin)

    def setPowerStatus(self, sPin, sSW):
        return self.avrelay.setPower(sPin, sSW)

    def getPowerStatus(self, sPin):
        return self.avrelay.getPower(sPin)

    def updateStatus(self, sPin):
        if (type(sPin) is str):
            iPin = int(sPin)
        else:
            iPin = sPin
        self.button[iPin].setIcon(self.getImg(sPin))

    def run(self):
        self.th1.start()

    def stop(self):
        self.th1.pipe.terminate()

    def writeLog(self, str):
        self.text.appendPlainText(str)


if __name__ == '__main__':
    app = MyApp(sys.argv)
    # Connect your cleanup function to signal.SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGSEGV, sig_segv)
    # And start a timer to call Application.event repeatedly.
    # You can change the timer parameter as you like.
    app.startTimer(200)

    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
