#ifndef __PYTHON_CONTROLLER_CONECTION_H__
#define __PYTHON_CONTROLLER_CONECTION_H__
#include "ftt.h"
#include <stdint.h>
#include <glib.h>
#include "simulation.h"

typedef struct {
  int worldRank;
  char* sendFifoName;
  char* recvFifoName;
  char* valuesFifoName;
  int sendFD;
  int recvFD;
  int valuesFD;
  GHashTable* cache;
  pid_t pythonControllerPID;
  GfsSimulation * sim;
} py_connector_t;


void py_connector_init(py_connector_t* self);
void py_connector_init_simulation(py_connector_t* self, GfsSimulation* sim);
void py_connector_destroy(py_connector_t* self);
double py_connector_get_value(py_connector_t* self, char* function);
void py_connector_send_force(py_connector_t* self, FttVector pf, FttVector vf, FttVector pm, FttVector vm, int step, double time);
void py_connector_send_location(py_connector_t* self, char* var, double value, FttVector p, int step, double time);

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
* Defines the current simulation for internal usage.
*/
void defineSimServer(GfsSimulation* sim);

/**
* Finalize server. Destroy pipes and close file descriptors.
*/
int closeServer();

/**
* Get a controlled value. Called by the C code compiled dinamically from the simulation file.
* Calls python controller.
*/
double controller(char* function);

/**
* Send to python Force values read by ControllerSolidForce
*/
void sendForceValue(FttVector pf, FttVector vf, FttVector pm, FttVector vm, int step, double time);

/**
* Send to python Location values read by ControllerLocation
*/
void sendLocationValue(char* var, double value, FttVector p, int step, double time);

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
