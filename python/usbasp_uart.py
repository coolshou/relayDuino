# -*- coding: utf-8 -*-
import os
import platform
import sys
from ctypes import byref, POINTER, create_string_buffer
try:
    # import usb1
    import libusb1
    from libusb1 import LIBUSB_REQUEST_TYPE_VENDOR, LIBUSB_RECIPIENT_DEVICE
except ImportError as err:
    raise SystemExit("pip3 install libusb1==2.0.0\n%s\n" % err)


if sys.version_info[0] == 3:
    long = int
# define
USB_ERROR_OK = 0
USB_ERROR_NOTFOUND = 1
USB_ERROR_ACCESS = 2
USB_ERROR_IO = 3
# usbasp-uart/firmware/usbasp.h
USBASP_FUNC_UART_CONFIG = 60
USBASP_FUNC_UART_TX = 64
USBASP_FUNC_UART_RX = 65
USBASP_FUNC_UART_TX_FREE = 66
USBASP_FUNC_UART_RX_FREE = 67
USBASP_FUNC_GETCAPABILITIES = 127
#
USBASP_UART_PARITY_MASK = 0b11
USBASP_UART_PARITY_NONE = 0b00
USBASP_UART_PARITY_EVEN = 0b01
USBASP_UART_PARITY_ODD = 0b10
USBASP_UART_STOP_MASK = 0b100
USBASP_UART_STOP_1BIT = 0b000
USBASP_UART_STOP_2BIT = 0b100
USBASP_UART_BYTES_MASK = 0b111000
USBASP_UART_BYTES_5B = 0b000000
USBASP_UART_BYTES_6B = 0b001000
USBASP_UART_BYTES_7B = 0b010000
USBASP_UART_BYTES_8B = 0b011000
USBASP_UART_BYTES_9B = 0b100000

USBASP_NO_CAPS = -4
USBASP_CAP_6_UART = (1 << 6)


def create_binary_buffer(string_or_len):
    # Prevent ctypes from adding a trailing null char.
    if isinstance(string_or_len, (int, long)):
        result = create_string_buffer(string_or_len)
    else:
        result = create_string_buffer(string_or_len, len(string_or_len))
    return result


class USBaspERROR(Exception):
    pass


class USBasp_UART:
    VENDOR_ID = 0x16C0  # vendor ID: 5824
    PRODUCT_ID = 0x05DC  # product ID: 1500
    MANUFACTURE = "www.fischl.de"
    PRODUCT = "USBasp"

    def __init__(self, baud=9600, flags=USBASP_UART_PARITY_NONE | USBASP_UART_BYTES_8B | USBASP_UART_STOP_1BIT):
        if getattr(sys, 'frozen', False):
            # we are running in a |PyInstaller| bundle
            self._basedir = sys._MEIPASS
        else:
            # we are running in a normal Python environment
            self._basedir = os.path.dirname(__file__)
        self.DEBUG = 3
        self._errorinfo = ""
        self.dummy = create_binary_buffer(4)
        self.dummysend = [0] * 4
        self.handle = None
        rc = self.config(baud, flags)
        if rc < 0:
            raise USBaspERROR("%s(%s)" % (self._errorinfo, rc))

    def open(self):
        errorCode = USB_ERROR_NOTFOUND
        ctx = POINTER(libusb1.libusb_context_p)()
        rc = libusb1.libusb_init(ctx)

        if not rc:
            usbhandle = POINTER(libusb1.libusb_device_handle)()

            dev_list = libusb1.libusb_device_p_p()
            # print("libusb_get_device_list")
            dev_list_len = libusb1.libusb_get_device_list(ctx, dev_list)
            for j in range(dev_list_len):
                dev = dev_list[j]  # int
                # device = libusb1.libusb_get_device(dev)
                # print("[%s]= %s" % (dev, device))
                descriptor = libusb1.libusb_device_descriptor()
                # print("libusb_get_device_descriptor:%s" % descriptor)
                rc = libusb1.libusb_get_device_descriptor(dev, descriptor)
                if not rc:
                    if (descriptor.idVendor == self.VENDOR_ID
                            and descriptor.idProduct == self.PRODUCT_ID):
                        # print("libusb_open")
                        try:
                            libusb1.libusb_open(dev, usbhandle)
                            if (not usbhandle):
                                errorCode = USB_ERROR_ACCESS
                                print("errorCode: %s" % errorCode)
                                continue
                        except Exception as err:
                            self.log("ERROR: libusb_open: %s" % err)
                            continue

                        # manufacturer = ""
                        manufacturer = create_binary_buffer(256)
                        # print("libusb_get_string_descriptor_ascii manufacturer")
                        libusb1.libusb_get_string_descriptor_ascii(usbhandle,
                                                                   descriptor.iManufacturer & 0xff,
                                                                   manufacturer, len(manufacturer))
                        if("www.fischl.de" not in manufacturer.value.decode()):
                            libusb1.libusb_close(usbhandle)
                            usbhandle = None
                            continue
                        self.log("manufacturer: %s" % manufacturer.value.decode(), 3)
                        product = create_binary_buffer(256)
                        # print("libusb_get_string_descriptor_ascii product")
                        libusb1.libusb_get_string_descriptor_ascii(usbhandle,
                                                                   descriptor.iProduct & 0xff,
                                                                   product, len(product))
                        if("USBasp" not in product.value.decode()):
                            libusb1.libusb_close(usbhandle)
                            usbhandle = None
                            continue
                        self.log("Product: %s" % product.value.decode(), 3)
                        break

            if usbhandle:
                errorCode = USB_ERROR_OK
                self.handle = usbhandle
        # print("open end: %s" % errorCode)
        return errorCode

    def config(self, baud, flags):
        #  baud: int
        # flags: int
        if(self.open() != 0):
            self._errorinfo = "ERROR: device USBasp not founded"
            if platform.system() == 'Windows':
                self._errorinfo = self._errorinfo + "\n please install USBasp driver: %s/bin/Windows/libusbK/InstallDriver.exe" % self._basedir
            self.log(self._errorinfo)
            return -1
        caps = self.capabilities()
        self.log("Capabilities: %d" % caps, 4)

        if(not(caps and USBASP_CAP_6_UART)):
            self._errorinfo = "ERROR: USBasp Capabilities not match: %d" % caps
            self.log(self._errorinfo)
            return USBASP_NO_CAPS

        send = [0] * 4

        FOSC = 12000000
        presc = FOSC / 8 / baud - 1
        self.log("Baud prescaler: %d" % presc, 4)
        real_baud = FOSC / 8 / (presc + 1)
        if(real_baud != baud):
            self.log("Note: cannot select baud=%d, selected %d instead.\n", baud, real_baud)

        send[1] = int(presc) >> 8
        send[0] = int(presc) & 0xFF
        send[2] = flags & 0xFF
        self.transmit(1, USBASP_FUNC_UART_CONFIG, send, self.dummy, 0)
        # self.log("usbasp_uart_transmit: %d" % rc, 3)
        return 0

    def capabilities(self):
        res = create_binary_buffer(4)
        send = [0] * 4
        ret = 0
        if(self.transmit(1, USBASP_FUNC_GETCAPABILITIES,
                         send, res, len(res)) == 4):
            if 0:
                for idx in range(4):
                    self.log("%s[%s]res(%s): %s" % (idx,
                                                    type(res[idx]),
                                                    len(res[idx]), res[idx].decode()))
            # ret = res[0] | ((uint32_t)res[1] << 8) | ((uint32_t)res[2] << 16) |((uint32_t)res[3] << 24);
            ret = int.from_bytes(res, byteorder="little")
        return ret

    def transmit(self, receive, functionid, send, buffer, buffersize):
        self.log("send: %s" % (send,), 5)
        rc = -1
        try:
            rc = libusb1.libusb_control_transfer(self.handle,
                                                 (LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE | (receive << 7)) & 0xff,
                                                 functionid,
                                                 ((send[1] << 8) | send[0]),
                                                 ((send[3] << 8) | send[2]),
                                                 buffer,
                                                 buffersize,
                                                 5000)         # 5s timeout.
        except OSError as err:
            self._errorinfo = "ERROR: transmit %s (%s)" % (err, rc)
            self.log(self._errorinfo)
        return rc

    def write(self, buff, bufflen):
        # buff: byte format
        # bufflen

        # if type(buff) is not bytes:
            #self.log("buff must be byte format!!")
            # return -1
        self.log("buff: %s: %s (len:%s)" % (type(buff), buff, bufflen), 6)
        # tmp[2]
        tmp = create_binary_buffer(2)
        rc = self.transmit(1, USBASP_FUNC_UART_TX_FREE, self.dummysend, tmp, 2)
        if rc < 0:
            self.log("ERROR: write USBASP_FUNC_UART_TX_FREE: %s: " % (rc))
            return -1
        # avail = (tmp[0] << 8) | tmp[1]
        avail = int.from_bytes(tmp, byteorder="big")
        #avail = int.from_bytes(tmp, byteorder="little")
        self.log("write avail: %s (%s)" % (avail, rc), 5)
        if(bufflen > avail):
            bufflen = avail

        self.log("Received free=%d, transmitting %d bytes" % (avail, bufflen), 6)
        if(bufflen == 0):
            return 0

        return self.transmit(0, USBASP_FUNC_UART_TX, self.dummysend, buff, bufflen)

    def write_all(self, buffs):
        # buffs: string
        if type(buffs) == str:
            buffs = buffs.encode()  # conver to bytes
        i = 0
        bufflen = len(buffs)
        # for idx in range(bufflen):
        while(i < bufflen):
            #buff = buffs[i]
            #rv = self.write(buffs, bufflen - 1)
            rv = self.write(buffs, bufflen)
            if(rv < 0):
                self.log("write_all: rv=%d" % rv, 5)
                return rv
            i += rv
            self.log("write_all: %d/%d sent" % (i, bufflen), 4)
        return len

    def read(self, buff, bufflen):
        if(bufflen > 254):
            bufflen = 254  # // Limitation of V - USB library.
        return self.transmit(1, USBASP_FUNC_UART_RX, self.dummysend, buff, bufflen)

    def readline(self):
        # read to \n
        rs = b""
        b = True
        while(b):
            #buff = [0] * 300
            buff = create_binary_buffer(300)
            rv = self.read(buff, len(buff))
            if(rv < 0):
                self.log("read: rv=%d" % rv, 5)
                return

            for i in range(rv):
                #rs = rs + buff[i].decode()
                rs = rs + buff[i]
            # fflush(stdout)
            if (buff.value.decode() == "\n"):
                # // found \n //
                self.log("found new line %s" % buff[0], 5)
                b = False
        if rs:
            self.log("readline: %s" % rs, 5)  # .decode())
        return rs

    def log(self, msg, lv=1):
        if self.DEBUG > lv:
            print("[%s]%s" % (self.__class__.__name__, msg))

