#define SH_MEM ".shmem"
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <unistd.h>

static int first = 1;
static double* mem;
static double iT0 = 0;
static double eT0 = 0;
static double ak =0.01243;
static double bk =0.00062;
static double ck =0.06215;

double ff(){
        if(first){
        // generacion de la clave
        key_t clave = ftok ("/home/pablo/lshort.pdf",0);
        if ( clave == -1 )
                printf("ERROR KEY \n");
        else {
                // creacion de la memoria compartida
                int shmId = shmget ( clave,sizeof(double),0644|IPC_CREAT );

                if ( shmId == -1 )
                        printf("ERROR SHMEM GET \n");
                else {
                        // attach del bloque de memoria al espacio de direcciones del proceso
                        void* ptrTemporal = shmat ( shmId,NULL,0 );

                        if ( ptrTemporal == (void *) -1 ) {
                                printf("ERROR SHMEM ATTCH \n");
                        } else {
             //                   printf("SHM [proc %d] - Creada con id %d. \n", getpid (), shmId);
                                mem = (double*) ptrTemporal;
				first = 0;
				
	//			printf("LEO VALOR DE LA SHMEM %f \n", value);
				
                        }
                }
        }
        }

	double eT = 1 - *mem;
        iT0 = iT0 + bk * eT;
        double dT = ck*(eT-eT0);
        eT0 = eT;
               
	return iT0+ak*eT+dT; 
}
