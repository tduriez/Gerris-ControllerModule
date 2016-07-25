#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <pythonCon.h>
//#ifdef HAVE_MPI
 #include <mpi.h>
//#endif


#define DEFAULT_SEND_FIFO_NAME "/tmp/gerris2python_request"
#define DEFAULT_RECV_FIFO_NAME "/tmp/python2gerris_response"
#define DEFAULT_VALUES_FIFO_NAME "/tmp/gerris2python_values"
#define PYTHON_CONTROLLER_PATH "python/main.py"

static int useCont = 0;
static int debug = 0;
static py_connector_t connector;


static void py_connector_init_fifos(py_connector_t* self);
static void py_connector_init_controller(py_connector_t* self);

int useController(int use){
	useCont = use;
	return 0;
}

int useDebug(int deb){
	debug = deb;
	return 0;
}

void py_connector_init(py_connector_t* self) {
    self->worldRank = 0;
    self->sim = NULL;
//#ifdef HAVE_MPI
    int world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    self->worldRank = world_rank;
//#endif

    size_t sendNameSize = sizeof(DEFAULT_SEND_FIFO_NAME)+3;
    size_t recvNameSize = sizeof(DEFAULT_RECV_FIFO_NAME)+3;
    size_t valuesNameSize = sizeof(DEFAULT_VALUES_FIFO_NAME)+3;
    self->sendFifoName = (char*)malloc(sendNameSize);
    self->recvFifoName = (char*)malloc(recvNameSize);
    self->valuesFifoName = (char*)malloc(valuesNameSize);
    snprintf(self->sendFifoName, sendNameSize, "%s_%02d", DEFAULT_SEND_FIFO_NAME, self->worldRank);
    snprintf(self->recvFifoName, recvNameSize, "%s_%02d", DEFAULT_RECV_FIFO_NAME, self->worldRank);
    snprintf(self->valuesFifoName, valuesNameSize, "%s_%02d", DEFAULT_VALUES_FIFO_NAME, self->worldRank);

    self->cache = g_hash_table_new(g_str_hash, g_str_equal);

    py_connector_init_controller(self);
    py_connector_init_fifos(self);
}

void py_connector_init_simulation(py_connector_t* self, GfsSimulation* sim) {
    if (! self->sim) {
        g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "step=%d - t=%.3f - Defining Simulation for py_connector", sim->time.i, sim->time.t);
        self->sim = sim;
    }
}
static void py_connector_init_controller(py_connector_t* self) {
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_INFO, "Starting Python controller at '%s'...", PYTHON_CONTROLLER_PATH);
    pid_t pid = fork();
    if (pid) {
        self->pythonControllerPID = pid;
        g_log (G_LOG_DOMAIN, G_LOG_LEVEL_INFO, "Python controller started.");
    }
    else {
        char worldRankStr[3];
        snprintf(worldRankStr, 3, "%02d", self->worldRank);
        execl(PYTHON_CONTROLLER_PATH, "main.py", "--script","python/module/script.py","--samples","5","--mpiproc", worldRankStr,
              "--requestfifo", self->sendFifoName, "--returnfifo", self->recvFifoName, "--samplesfifo", self->valuesFifoName, NULL);
        g_log (G_LOG_DOMAIN, G_LOG_LEVEL_ERROR, "Python controller couldn't start propertly.");
        exit(EXIT_FAILURE);
    }
}

static void py_connector_init_fifos(py_connector_t* self) {
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_INFO, "Creating FIFOs: %s, %s", self->sendFifoName, self->recvFifoName);
    struct stat st;
    if (stat(self->sendFifoName, &st) == 0)
        unlink(self->sendFifoName);
    if (stat(self->recvFifoName, &st) == 0)
        unlink(self->recvFifoName);
	if (stat(self->valuesFifoName, &st) == 0)
        unlink(self->valuesFifoName);

    mkfifo(self->sendFifoName, 0666);
    mkfifo(self->recvFifoName, 0666);
    mkfifo(self->valuesFifoName, 0666);

    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "FIFOs created. Opening FDs");
    self->sendFD = open(self->sendFifoName, O_WRONLY);
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "FIFO created at %s.", self->sendFifoName);
    self->recvFD = open(self->recvFifoName, O_RDONLY);
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "FIFO created at %s.", self->recvFifoName);
    self->valuesFD = open(self->valuesFifoName, O_WRONLY);
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "FIFO created at %s.", self->valuesFifoName);
}

static void py_connector_clear_cache(py_connector_t* self) {
    GList* values = g_hash_table_get_values(self->cache);
    while (values) {
        g_free(values->data);
        values = values->next;
    }
    g_hash_table_remove_all (self->cache);
}

void py_connector_destroy(py_connector_t* self) {
    free(self->sendFifoName);
    free(self->recvFifoName);
    free(self->valuesFifoName);
    py_connector_clear_cache(self);
    g_hash_table_destroy(self->cache);

    close(self->sendFD);
    close(self->recvFD);
    close(self->valuesFD);
    unlink(self->sendFifoName);
    unlink(self->recvFifoName);
    unlink(self->valuesFifoName);
}

double py_connector_get_value(py_connector_t* self, char* function) {
    double value = 0;
	char* cachedValue = g_hash_table_lookup(self->cache, function);
	if(cachedValue == NULL){
		CallController callController;
		callController.type = 0;
		strncpy(callController.funcName, function, 31);
		callController.funcName[31] = '\0';
        size_t bytesToSend = sizeof(callController);
        int sentBytes = write(self->sendFD, (void*)&callController, bytesToSend);
        if (sentBytes != bytesToSend)
             g_log (G_LOG_DOMAIN, G_LOG_LEVEL_ERROR,"Fail on py_connector_get_value - SentBytes=%d BytesToSend=%d", sentBytes, bytesToSend);
		char buf[40];
		int bytes = read(self->recvFD, buf, 40);
		buf[39] = '\0';
		ReturnController* returnValue = (ReturnController*) buf;
        value = returnValue->returnValue;
        gchar* newCachedValue = g_strdup_printf("%f", value);
        g_hash_table_insert(self->cache, function, newCachedValue);
        if (!self->sim)
            g_log (G_LOG_DOMAIN, G_LOG_LEVEL_WARNING,"No simulation defined before calling py_connector_get_value. System will resume and use controller results anyway.");
        gint step = self->sim ? self->sim->time.i : 0;
        double time = self->sim ? self->sim->time.t : 0;
        g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG,"step=%d t=%.3f py_connector_get_value - %s=%f", step, time, function, value);
	}
    else
        value = atof(cachedValue);

    return value;
}

void py_connector_send_force(py_connector_t* self, FttVector pf, FttVector vf, FttVector pm, FttVector vm, int step, double time) {
	ValueController valueToSend;
	valueToSend.type = 0;
	valueToSend.time = time;
	valueToSend.step = step;
	valueToSend.data.forceValue.pf = pf;
	valueToSend.data.forceValue.vf = vf;
	valueToSend.data.forceValue.pm = pm;
	valueToSend.data.forceValue.vm = vm;
    int bytesToSend = sizeof(valueToSend);
	int sentBytes = write(self->valuesFD,&valueToSend,bytesToSend);
    if (sentBytes != bytesToSend)
        g_log (G_LOG_DOMAIN, G_LOG_LEVEL_ERROR,"Fail on py_connector_send_force - SentBytes=%d BytesToSend=%d", sentBytes, bytesToSend);
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "step=%d - t=%.3f - Sending pf=(%.3f,%.3f,%.3f), vm=(%.3f,%.3f,%.3f)", 
                                            valueToSend.step, valueToSend.time,
                                            valueToSend.data.forceValue.pf.x,valueToSend.data.forceValue.pf.y,valueToSend.data.forceValue.pf.z,
                                            valueToSend.data.forceValue.vm.x,valueToSend.data.forceValue.vm.y,valueToSend.data.forceValue.vm.z);
    py_connector_clear_cache(self);
}

void py_connector_send_location(py_connector_t* self, char* var, double value, FttVector p, int step, double time){
    ValueController valueToSend;
    // LOCATION TYPE
    valueToSend.type = 1;
    valueToSend.time = time;
    valueToSend.step = step;
    strncpy(valueToSend.data.locationValue.varName, var, 63);
    valueToSend.data.locationValue.varName[63] = '\0';
    valueToSend.data.locationValue.value = value;
    valueToSend.data.locationValue.position[0] = p.x;
    valueToSend.data.locationValue.position[1] = p.y;
    valueToSend.data.locationValue.position[2] = p.z;
    // Send it through FIFO.
    int bytesToSend = sizeof(valueToSend);
	int sentBytes = write(self->valuesFD,&valueToSend,bytesToSend);
    if (sentBytes != bytesToSend)
        g_log (G_LOG_DOMAIN, G_LOG_LEVEL_ERROR,"Fail on py_connector_send_location - SentBytes=%d BytesToSend=%d", sentBytes, bytesToSend);
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "step=%d - t=%.3f - Sending %s=%f - (x,y,z)=(%f, %f, %f)", step, time, var, value, p.x, p.y, p.z);
    g_hash_table_remove_all(connector.cache);
}

int initServer(){
    if (useCont)
        py_connector_init(&connector);

    return 0;
}
void defineSimServer(GfsSimulation* sim){
    if (useCont)
        py_connector_init_simulation(&connector, sim);
}

int closeServer(){
    if(useCont){
        py_connector_destroy(&connector);
    }
    return 0;
}

double controller(char* function){
    if(useCont)
        return py_connector_get_value(&connector, function);
    else
        return 0;
}

void sendForceValue(FttVector pf, FttVector vf, FttVector pm, FttVector vm, int step, double time){
    if (useCont)
        py_connector_send_force(&connector, pf, vf, pm, vm, step, time);
}

void sendLocationValue(char* var, double value, FttVector p, int step, double time){
    if (useCont)
        py_connector_send_location(&connector, var, value, p, step, time);
}

