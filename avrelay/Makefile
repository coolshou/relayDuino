TARGET        = avrelay

#cross conpile under Linux
# mingw x86
#CROSS=i686-w64-mingw32-
# mingw x64
# CROSS=x86_64-w64-mingw32-
CROSS=

CC=$(CROSS)gcc
tmp = $(shell $(CC) -dumpmachine)
#$(warning $(tmp))
ifneq (,$(findstring i686,$(tmp)))
TARGET_DIR := x86
ifneq (,$(findstring mingw32,$(tmp)))
SRCPATH=/c/msys64/mingw32/bin/
COPYDLLS:=libgcc_s_dw2-1.dll
endif
else ifneq (,$(findstring x86_64,$(tmp)))
TARGET_DIR := x86_64
ifneq (,$(findstring mingw32,$(tmp)))
SRCPATH=/c/msys64/mingw64/bin/
COPYDLLS:=libgcc_s_seh-1.dll
endif
else
$(error "NOT support platform")
endif

ifneq (,$(findstring mingw32,$(tmp)))
TARGETRES     = $(TARGET).res
COPYDLLS+=libstdc++-6.dll libwinpthread-1.dll libusb-1.0.dll
else
TARGETRES=
endif

CC=$(CROSS)g++
MV=mv
CP=cp
WINRES=$(CROSS)windres
LINK          = $(CROSS)g++
LFLAGS=-O2 -Wall -Wextra -std=c++14
LDFLAGS+=$(shell $(CROSS)pkg-config --libs libusb-1.0)
CFLAGS+=$(shell $(CROSS)pkg-config --cflags libusb-1.0)
LIBS = ${CFLAGS} ${LDFLAGS} -lpthread
#Debug
#LFLAGS+=-g3

DEL_FILE      = rm -rf

SOURCES = \
	usbasp_uart.c \
	main.cpp

all: clean res $(TARGET)

$(TARGET):
	$(CC)  $(LFLAGS) $(SOURCES) $(TARGETRES) ${LIBS} -o "$@"
	mkdir -p "$(shell pwd)/$(TARGET_DIR)/"
	$(MV) $(TARGET) "$(shell pwd)/$(TARGET_DIR)/"
ifneq (,$(COPYDLLS))
	$(foreach DLL,$(COPYDLLS),$(CP) -u $(SRCPATH)$(DLL) "$(shell pwd)/$(TARGET_DIR)/";)
endif

res:
ifneq (,$(TARGETRES))
	$(WINRES) $(TARGET).rc -O coff -o $(TARGETRES)
endif

clean:
	$(DEL_FILE)  "$(shell pwd)/$(TARGET_DIR)"
