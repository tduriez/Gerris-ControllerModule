#define SH_MEM ".shmem"
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <unistd.h>
#include "pythonCon.h"

double controller(char* function){
        return getValue(function);
}
