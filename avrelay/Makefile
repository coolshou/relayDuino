TARGET        = avrelay

CC=g++
LINK          = g++
LFLAGS=-O2 -Wall -Wextra -std=c++14
LDFLAGS+=$(shell pkg-config --libs libusb-1.0)
CFLAGS+=$(shell pkg-config --cflags libusb-1.0)
LIBS = ${CFLAGS} ${LDFLAGS} -lpthread

DEL_FILE      = rm -f

SOURCES = \
	usbasp_uart.c \
	main.cpp

all: clean $(TARGET)

$(TARGET):
	$(CC)  $(LFLAGS) $(SOURCES) ${LIBS} -o "$@"

clean:
	$(DEL_FILE) $(TARGET)
