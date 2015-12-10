#ifndef __PYTHON_CONTROLLER_CONECTION_H__
#define __PYTHON_CONTROLLER_CONECTION_H__
#include "ftt.h"
#include <stdint.h>

/**
* Set gerris to use python controller and create pipes.
*/
int useController(int use);

/**
* Set gerris to print debug.
*/
int useDebug(int deb);

/**
* Initialize server. Creates pipes and open file descriptors.
*/
int initServer();

/**
* Get a controlled value. Called by the C code compiled dinamically from the simulation file.
* Calls python controller.
*/
double getValue(char* function);

/**
* Send to python Force values read by ControllerSolidForce
*/
void sendForceValue(FttVector pf, FttVector vf, FttVector pm, FttVector vm, int step, double time);

/**
* Send to python Location values read by ControllerLocation
*/
void sendLocationValue(char* var, double value, int step, double time, double x, double y, double z);

typedef struct _ValueController		ValueController;
typedef struct _ForceValue	        ForceValue;
typedef struct _LocationValue         	LocationValue;

/**
* Force value struct. Represents the pressure and viscous force, and pressure and viscous moments.
*/
struct _ForceValue {
        FttVector pf, vf, pm, vm;
};

/**
* Location value struct. Represents a location and a value of a variable in that location.
*/
struct _LocationValue{
        double value;
        double position[3];
	char varName[64];
};

/**
* Value Controller struct. Represents a value to be sent to python. 
* It can be either a Force value or a Location value.
*/
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

/**
* Call controller struct. Used to call a function controller in python.
*/
struct _CallController {
	int32_t type;
	char funcName[32];
};

typedef struct _ReturnController	ReturnController;

/**
* Return controller struct. Used to get the returned value of a controller from python.
*/
struct _ReturnController {
	double returnValue;
	char funcName[32];
};

#endif
