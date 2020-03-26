# Created on Fri Feb 14 2020:22:00:40
# Created by Ratnadeep Bhattacharya

CC=gcc
CFLAGS=-g -Wall -Wextra -Wno-unused-variable -Wno-unused-parameter
LIBS=-lpthread
TARGET=gen_load

OBJS=gen_load.o

all: ${TARGET}

${TARGET}: ${OBJS} ${LIBS}
	@${CC} ${CFLAGS} ${OBJS} ${LIBS} -o ${TARGET} ${LIBS}

gen_load.o: gen_load.c
	@${CC} ${CFLAGS} -c -I . gen_load.c -o gen_load.o ${LIBS}

clean:
	@rm -f *.o
	@rm gen_load

cleanall:
	@make clean

remake:
	@make cleanall; make all

# pass the file name that will collect the states
# run as: make ARGS="<filename>" run
# Eg. make ARGS="example.json" run
run:
	@make all
	@./check_python.py
	@./gen_load &
	@python get_states.py ${ARGS}
