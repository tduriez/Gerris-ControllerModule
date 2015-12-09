#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <pythonCon.h>

static int updated = 0; 
static double actualValue = 0;
static double sentValue = 0;
static int callFd = 0;
static int recvFd = 0;
static int valuesFd = 0;
static char* callfifo = "/tmp/callfifo";
static char* recvfifo = "/tmp/recvfifo";
static char* valuesfifo = "/tmp/valuesfifo";

int initServer(){
	printf("Inciando conexion con python \n");
	struct stat st;

    	// if fifos exist, delete them
    	if (stat(callfifo, &st) == 0)
        	unlink(callfifo);
    	if (stat(recvfifo, &st) == 0)
        	unlink(recvfifo);        
	if (stat(valuesfifo, &st) == 0)
                unlink(valuesfifo);


	mkfifo(callfifo, 0666);
	mkfifo(recvfifo, 0666);
	mkfifo(valuesfifo, 0666);

	callFd = open(callfifo, O_RDWR); 
	recvFd = open(recvfifo, O_RDWR);
	valuesFd = open(valuesfifo, O_RDWR);

	return 0;
}

int closeServer(){
	close(callFd);
	close(recvFd);
	close(valuesFd);
	unlink(callfifo);
	unlink(recvfifo);
	unlink(valuesfifo);
}


double help(){
	return sentValue * -10.0;
}

double getValue(char* function){
	help();
	if(updated){
		printf("Calling %s function \n ", function);
		CallController callController;
		callController.type = 0;
		strncpy(callController.funcName, function, 31);
		callController.funcName[31] = '\0';
                write(callFd, (void*)&callController,sizeof(callController));
		printf("Call size %d", sizeof(CallController));
		fflush(stdout);
		char buf[40];
		int bytes = read(recvFd,buf,40);
		printf("read %d \n",bytes);
		buf[39] = '\0';
		ReturnController* returnValue = (ReturnController*) buf;
                actualValue = returnValue->returnValue;
                updated = 0;
		printf("Value got: %s %f \n",returnValue->funcName, actualValue);
		fflush(stdout);
	}
	return actualValue;
}

void sendForceValue(FttVector pf, FttVector vf, FttVector pm, FttVector vm, int step, double time){
        printf("Actual value %f \n", actualValue);
	ValueController valueToSend;
	// FORCE TYPE
	valueToSend.type = 0;
	valueToSend.time = time;
	valueToSend.step = step;
	valueToSend.data.forceValue.pf = pf;
	valueToSend.data.forceValue.vf = vf;
	valueToSend.data.forceValue.pm = pm;
	valueToSend.data.forceValue.vm = vm;
	// Send it through FIFO.
	write(valuesFd,&valueToSend,sizeof(valueToSend));

	printf("Sending pf.x value: %f  time: %f step %d \n", valueToSend.data.forceValue.pf.x, valueToSend.time, valueToSend.step);

	sentValue = pf.x;
        updated = 1;
        printf("Updated %d \n", updated);
}

void sendLocationValue(char* var, double value, int step, double time, double x, double y, double z){
	printf("Actual value %f \n", actualValue);
        ValueController valueToSend;
        // LOCATION TYPE
        valueToSend.type = 1;
        valueToSend.time = time;
        valueToSend.step = step;
	strncpy(valueToSend.data.locationValue.varName, var, 9);
	valueToSend.data.locationValue.varName[9] = '\0';
        valueToSend.data.locationValue.value = value;
	valueToSend.data.locationValue.position[0] = x;
	valueToSend.data.locationValue.position[1] = y;
	valueToSend.data.locationValue.position[2] = z;
        // Send it through FIFO.
        write(valuesFd,&valueToSend,sizeof(valueToSend));

        //printf("Sending var %s value: %f  time: %f step %d location (x,y,z): (%f, %f, %f) \n", valueToSend.data.locationValue.varName, valueToSend.data.locationValue.value, valueToSend.time, valueToSend.step,  valueToSend.data.locationValue.position[0],  valueToSend.data.locationValue.position[1],  valueToSend.data.locationValue.position[2]);

        sentValue = value;
        updated = 1;
        printf("Updated %d \n", updated);

}


