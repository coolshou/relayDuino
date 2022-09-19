#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 09:52:55 2019

@author: jimmy
"""
#import sys
#import signal
import time
import unittest

from relay import Relay


class RelayTest(unittest.TestCase):
    '''    test case for Wlan class '''

    def setUp(self):
        self.relay = Relay()
        self.powerpin = 3

    def test_getMaxPowerNum(self):
        if self.relay:
            iMax = self.relay.getMaxPowerNum()
            self.assertEqual(iMax, '4')

    def test_setpower_on(self):
        if self.relay:
            self.relay.setPower(self.powerpin, 1)
            val = self.relay.getPower(self.powerpin)
            #print("val: (%s) %s" % (type(val), val))
            self.assertEqual(val, 1)

    def test_setpower_off(self):
        if self.relay:
            self.relay.setPower(self.powerpin, 0)
            val = self.relay.getPower(self.powerpin)
            self.assertEqual(val, 0)

    def tearDown(self):
        '''
        clean up when test finish
        '''
        pass


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(RelayTest('test_getMaxPowerNum'))
    suite.addTest(RelayTest('test_setpower_on'))
    time.sleep(3)
    suite.addTest(RelayTest('test_setpower_off'))
    unittest.TextTestRunner(verbosity=2).run(suite)
