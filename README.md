# relayDuino
USBasp+ control power on/off relay

#burn usbasp+ (only do once)
    #install require package: gcc-avr
    sudo apt install gcc-avr avr-libc
    cd usbasp-uart/firmware
    make main.hex
    #upload firmware to ATMega8
    #install require package: avrdude
    sudo apt install avrdude
    avrdude -v -patmega8 -c usbasp -Uflash:w:main.hex:i

#burn relayDuino ()
    #install Arduino IDE (https://www.arduino.cc)
    #install resuire Arduino lib: ArduinoThread (https://github.com/ivanseidel/ArduinoThread)
    Menu -> Sketch ->  Include Library -> Manage Libraries
    filter with ArduinoThread and install it
    #open firmware/Relay/Relay.ino

    Verify/Compile
    Upload Using Programmer

# Use avrelay to control relayDuino's  power pin
    cd avrelay
    make
    #get Power pin state
    avrelay -g 1
    #set Power pin ON
    avrelay -s 1 1
    #set Power pin OFF
    avrelay -s 1 0

# Use usbasp_uart to communicate with the relayDuino (interactive)
    #require libusb-1.0-0-dev
    cd usbasp-uart/terminal
    make
    #windows mingw64 require mingw-w64-i686-libusb or mingw-w64-x86_64-libusb
    install msys2
    pacman -S mingw32/mingw-w64-i686-libusb mingw64/mingw-w64-x86_64-libusb
