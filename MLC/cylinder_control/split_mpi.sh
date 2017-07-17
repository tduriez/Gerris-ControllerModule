#! /bin/bash

#split the domain 2 times so, 2 boxes become 2*4*4 boxes
gerris2D -m -s 1 cylinder_control.gfs > cylinder_control_s2.gfs

#partition the domain in N exp 2 processor groups
gerris2D -p 2 cylinder_control_s2.gfs > cylinder_control_p2.gfs

mv cylinder_control_p2.gfs cylinder_run.gfs
rm cylinder_control_s2.gfs
