#! /bin/bash
rm -rf results/*
mpirun -np 4 gerris2D cylinder_run.gfs 2>log.txt
