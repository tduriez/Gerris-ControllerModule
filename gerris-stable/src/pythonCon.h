#ifndef __PYTHON_CONTROLLER_CONECTION_H__
#define __PYTHON_CONTROLLER_CONECTION_H__
#include "ftt.h"
#include <stdint.h>

int initServer();
double getValue(char* function);
void sendForceValue(FttVector pf, FttVector vf, FttVector pm, FttVector vm, int step, double time);
void sendLocationValue(char* var, double value, int step, double time, double x, double y, double z);

typedef struct _ValueController		ValueController;
typedef struct _ForceValue	        ForceValue;
typedef struct _LocationValue         	LocationValue;

struct _ForceValue {
        FttVector pf, vf, pm, vm;
};

struct _LocationValue{
        char varName[10];
        double value;
        double position[3];
};


struct _ValueController {
	int32_t type;
	double time;
	int32_t step;
	union {
		ForceValue forceValue;
		LocationValue locationValue;
	} data;
};

typedef struct _CallController		CallController;

struct _CallController {
	int32_t type;
	char funcName[32];
};

typedef struct _ReturnController	ReturnController;

struct _ReturnController {
	double returnValue;
	char funcName[32];
};

#endif
