# relayDuino
USBasp+ control power on/off relay

#burn usbasp+ (only do once)
    #install gcc-avr
    sudo apt install gcc-avr avr-libc
    cd usbasp-uart/firmware
    make main.hex
    #upload firmware to ATMega8
    sudo apt install avrdude
    avrdude -v -patmega8 -c usbasp -Uflash:w:main.hex:i

#burn relayDuino ()
    #resuire ArduinoThread (https://github.com/ivanseidel/ArduinoThread)
    install from Arduino library


# Use usbasp_uart to communicate with the relayDuino (interactive)
    #require libusb-1.0-0-dev
    cd usbasp-uart/terminal
    make
    #windows
    install mingw64
    pacman -S mingw-w64-x86_64-libusb mingw-w64-x86-libusb

# Use avrelay to control relayDuino's  power pin
    cd avrelay
    make
