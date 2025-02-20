/******************************************************************************
 * Vectors sum MPI program
 *****************************************************************************/
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#define MASTER 0
#define ARRAY_SIZE 5000000

int main(int argc, char *argv[], char *envv[])
{
    /* data */
    int *a = malloc(sizeof(int) * ARRAY_SIZE);
    int *b = malloc(sizeof(int) * ARRAY_SIZE);
    int *c = malloc(sizeof(int) * ARRAY_SIZE);

    int procs, id;

    /* Initialization of MPI environment */
    MPI_Init (&argc, &argv);
    /* Get number of processes in system (group COMM_WORLD) */
    MPI_Comm_size (MPI_COMM_WORLD, &procs);

    int n = ARRAY_SIZE / procs;

    /* receiving buffers */
    int *ap = malloc(sizeof(int) * n);
    int *bp = malloc(sizeof(int) * n);
    int *cp = malloc(sizeof(int) * n);
    
    /* Get process id (rank) */
    MPI_Comm_rank (MPI_COMM_WORLD, &id);
    if (id == MASTER) {
        /* initialize vectors */
        for (int i=0; i<ARRAY_SIZE; i++) {
            a[i] = 5;
            b[i] = 4;
            c[i] = 0;
        }
    }
    /* send n chunks of array a from MASTER to others */
    MPI_Scatter(a, n, MPI_INT, ap, n, MPI_INT, MASTER, MPI_COMM_WORLD);
    /* idem with b array */
    MPI_Scatter(b, n, MPI_INT, bp, n, MPI_INT, MASTER, MPI_COMM_WORLD);
    /* sum chunk */
    for (int i=0; i<n; i++) {
        cp[i] = ap[i] + bp[i];
    }
    /* collect results */
    MPI_Gather(cp, n, MPI_INT, c, n, MPI_INT, MASTER, MPI_COMM_WORLD);
    if (id == MASTER) {
        printf("%d %d %d\n", c[0], c[100000], c[199999]);
    }
    MPI_Finalize();
}
