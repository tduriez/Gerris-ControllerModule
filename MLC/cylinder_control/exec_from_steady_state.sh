#! /bin/bash
rm -rf results/*
mpirun -np 2 gerris2D cylinder_060.000.gfs 2>log.txt