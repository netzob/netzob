DEBUG=no
SRC=rel_test.c 			\
	  rel_equality.c	\
	  rel_size.c
OBJ=$(SRC:.c=.o)
SOBJ=$(OBJ:.o=.so)
CFLAGS=-fPIC -I../../includes
LDFLAGS=-L/usr/lib

ifeq ($(DEBUG),yes)
	CFLAGS+= -g -D__DEBUG__
endif

all: $(SOBJ)

%.o: %.c
	$(CC) -c -pthread $(CFLAGS) $< -o $@

%.so: %.o
	$(CC) -shared -Wl,-soname,$@ $(LDFLAGS) $< -o $@

clean:
	$(RM) $(OBJ) $(SOBJ)

re: clean all
