#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from usbasp_uart import USBasp_UART
import time

if __name__ == '__main__':
    usbasp = None
    try:
        usbasp = USBasp_UART()
    except Exception as err:
        print("%s" % err)
    if usbasp:
        # get Max power pin
        usbasp.write_all("max\n")
        rs = usbasp.readline()
        print("Max power control num: %s" % rs)
        # get power pin 0 status
        powerpin = 0
        usbasp.write_all("get %s\n" % powerpin)
        rs = usbasp.readline()
        print("power pin %s = %s" % (powerpin, rs))

        # set power pin 3 on
        powerpin = 3
        usbasp.write_all("set %s 1\n" % powerpin)
        rs = usbasp.readline()
        print("power pin %s = %s" % (powerpin, rs))

        time.sleep(3)
        usbasp.write_all("set %s 0\n" % powerpin)
