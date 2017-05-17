CC=gcc
DBG=0
CFLAGS=-DDEBUG=$(DBG) -w
#-static -static-libgcc
SRC=microwaveCollated.c

define _dump
	objdump -d $(1) -M intel-mnemonic > $(1).dump
endef

define dump
	touch makefile
endef

all: o0 o1 o2 o3 os

o0: $(SRC)
	$(CC) $(SRC) $(CFLAGS) -o o0 -O0 -DTRACE_FNAME=\"o0.trace.csv\"
	$(call dump, o0)

o1: $(SRC)
	$(CC) $(SRC) $(CFLAGS) -o o1 -O1 -DTRACE_FNAME=\"o1.trace.csv\"
	$(call dump, o1)

o2: $(SRC)
	$(CC) $(SRC) $(CFLAGS) -o o2 -O2 -DTRACE_FNAME=\"o2.trace.csv\"
	$(call dump, o2)

o3: $(SRC)
	$(CC) $(SRC) $(CFLAGS) -o o3 -O3 -DTRACE_FNAME=\"o3.trace.csv\"
	$(call dump, o3)

os: $(SRC)
	$(CC) $(SRC) $(CFLAGS) -o os -Os -DTRACE_FNAME=\"os.trace.csv\"
	$(call dump, os)

oi: $(SRC)
	$(CC) $(SRC) $(CFLAGS) -o oi -finline-small-functions -DTRACE_FNAME=\"oi.trace.csv\"
	$(call dump, oi)

clean:
	rm o0 o1 o2 o3 os oi *.dump *.cov *.pincov

