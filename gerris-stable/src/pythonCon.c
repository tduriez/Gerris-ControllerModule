#include <stdio.h>

static int updated = 0; 
static double actualValue = 0;
static double sentValue = 0;


int initServer(){
	printf("Inciando conexion con python \n");
	return 0;
}


double help(){
	return sentValue * -10.0;
}

double getValue(char* function){
	help();
	if(updated){
		printf("Calling %s function \n ", function);
                double a = help();
                actualValue = a;
                updated = 0;
		printf("Value got: %f \n", actualValue);
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


