int initServer();
double getValue(char* function);
void sendValue(char* var, double value);

typedef struct _ValueController		ValueController;

struct _ValueController {
	int type;
	double time;
	int step;
	char varName[4];
	double value;
	double position[3];
};

typedef struct _CallController		CallController;

struct _CallController {
	int type;
	char funcName[30];
};

typedef struct _ReturnController	ReturnController;

struct _ReturnController {
	char funcName[30];
	double returnValue;
};

