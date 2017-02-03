#------------------------------------------------------------------------------#
# This makefile was generated by 'cbp2make' tool rev.147                       #
#------------------------------------------------------------------------------#


WORKDIR = `pwd`

CC = gcc
CXX = g++
AR = ar
LD = g++
WINDRES = windres

INC = 
CFLAGS = -Wall
RESINC = 
LIBDIR = 
LIB = -lgdi32 -luser32 -lkernel32 C:/CodeBlocks/MinGW/lib/libhid.a C:/CodeBlocks/MinGW/lib/libsetupapi.a C:/CodeBlocks/MinGW/lib/libusb.a
LDFLAGS = -static-libgcc

INC_DEBUG = $(INC)
CFLAGS_DEBUG = $(CFLAGS) -g
RESINC_DEBUG = $(RESINC)
RCFLAGS_DEBUG = $(RCFLAGS)
LIBDIR_DEBUG = $(LIBDIR)
LIB_DEBUG = $(LIB)-lgdi32 -luser32 -lkernel32 C:/CodeBlocks/MinGW/lib/libusb.a C:/CodeBlocks/MinGW/lib/libhid.a C:/CodeBlocks/MinGW/lib/libsetupapi.a
LDFLAGS_DEBUG = $(LDFLAGS) -static-libgcc
OBJDIR_DEBUG = obj/Debug
DEP_DEBUG = 
OUT_DEBUG = bin/Debug/USBASP_tty

INC_RELEASE = $(INC)
CFLAGS_RELEASE = $(CFLAGS) -O2
RESINC_RELEASE = $(RESINC)
RCFLAGS_RELEASE = $(RCFLAGS)
LIBDIR_RELEASE = $(LIBDIR)
LIB_RELEASE = $(LIB)-lgdi32 -luser32 -lkernel32 C:/CodeBlocks/MinGW/lib/libhid.a C:/CodeBlocks/MinGW/lib/libsetupapi.a C:/CodeBlocks/MinGW/lib/libusb.a
LDFLAGS_RELEASE = $(LDFLAGS) -s -static-libgcc
OBJDIR_RELEASE = obj/Release
DEP_RELEASE = 
OUT_RELEASE = bin/Release/USBASP_tty

OBJ_DEBUG = $(OBJDIR_DEBUG)/opendevice.o $(OBJDIR_DEBUG)/usbasp_tty.o $(OBJDIR_DEBUG)/usbasp_tty.o

OBJ_RELEASE = $(OBJDIR_RELEASE)/opendevice.o $(OBJDIR_RELEASE)/usbasp_tty.o $(OBJDIR_RELEASE)/usbasp_tty.o

all: debug release

clean: clean_debug clean_release

before_debug: 
	test -d bin/Debug || mkdir -p bin/Debug
	test -d $(OBJDIR_DEBUG) || mkdir -p $(OBJDIR_DEBUG)

after_debug: 

debug: before_debug out_debug after_debug

out_debug: before_debug $(OBJ_DEBUG) $(DEP_DEBUG)
	$(LD) $(LIBDIR_DEBUG) -o $(OUT_DEBUG) $(OBJ_DEBUG)  $(LDFLAGS_DEBUG) $(LIB_DEBUG)

$(OBJDIR_DEBUG)/opendevice.o: opendevice.c
	$(CC) $(CFLAGS_DEBUG) $(INC_DEBUG) -c opendevice.c -o $(OBJDIR_DEBUG)/opendevice.o

$(OBJDIR_DEBUG)/usbasp_tty.o: usbasp_tty.c usbasp_tty.rc
	$(CC) $(CFLAGS_DEBUG) $(INC_DEBUG) -c usbasp_tty.c -o $(OBJDIR_DEBUG)/usbasp_tty.o
	$(WINDRES) -i usbasp_tty.rc -J rc -o $(OBJDIR_DEBUG)/usbasp_tty.o -O coff $(INC_DEBUG)

clean_debug: 
	rm -f $(OBJ_DEBUG) $(OUT_DEBUG)
	rm -rf bin/Debug
	rm -rf $(OBJDIR_DEBUG)

before_release: 
	test -d bin/Release || mkdir -p bin/Release
	test -d $(OBJDIR_RELEASE) || mkdir -p $(OBJDIR_RELEASE)

after_release: 

release: before_release out_release after_release

out_release: before_release $(OBJ_RELEASE) $(DEP_RELEASE)
	$(LD) $(LIBDIR_RELEASE) -o $(OUT_RELEASE) $(OBJ_RELEASE)  $(LDFLAGS_RELEASE) $(LIB_RELEASE)

$(OBJDIR_RELEASE)/opendevice.o: opendevice.c
	$(CC) $(CFLAGS_RELEASE) $(INC_RELEASE) -c opendevice.c -o $(OBJDIR_RELEASE)/opendevice.o

$(OBJDIR_RELEASE)/usbasp_tty.o: usbasp_tty.c usbasp_tty.rc
	$(CC) $(CFLAGS_RELEASE) $(INC_RELEASE) -c usbasp_tty.c -o $(OBJDIR_RELEASE)/usbasp_tty.o
	$(WINDRES) -i usbasp_tty.rc -J rc -o $(OBJDIR_RELEASE)/usbasp_tty.o -O coff $(INC_RELEASE)

clean_release: 
	rm -f $(OBJ_RELEASE) $(OUT_RELEASE)
	rm -rf bin/Release
	rm -rf $(OBJDIR_RELEASE)

.PHONY: before_debug after_debug clean_debug before_release after_release clean_release
