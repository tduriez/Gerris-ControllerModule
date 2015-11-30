#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>

static int updated = 0; 
static double actualValue = 0;
static double sentValue = 0;
static int sendFd = 0;
static int recvFd = 0;
static char* sendfifo = "/tmp/sendfifo";
static char* recvfifo = "/tmp/recvfifo";

int initServer(){
	printf("Inciando conexion con python \n");
        mkfifo(sendfifo, 0666);
	mkfifo(recvfifo,0666);
	sendFd = open(sendfifo, O_RDWR); 
	recvFd = open(recvfifo, O_RDWR);
	return 0;
}

int closeServer(){
	close(sendFd);
	close(recvFd);
	unlink(sendfifo);
	unlink(recvfifo);
}


double help(){
	return sentValue * -10.0;
}

double getValue(char* function){
	help();
	if(updated){
		printf("Calling %s function \n ", function);
                write(sendFd,"call",sizeof("call"));
		char buf[10];
		int bytes = read(recvFd,buf,2);
		printf("read %d \n",bytes);
		buf[2] = '\0';
		//double a = help();
                actualValue = atof(buf);
                updated = 0;
		printf("Value got: %s %f \n",buf, actualValue);
		fflush(stdout);
	}
	return actualValue;
}

void sendValue(char* var, double value){
	printf("Sending value %s %f \n", var, value);
        printf("Actual value %f \n", actualValue);
	sentValue = value;
        updated = 1;
        printf("Updated %d \n", updated);
}


