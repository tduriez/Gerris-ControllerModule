# Gerris-Taller3


- sudo apt-get install libglib2.0-dev libnetpbm10-dev m4 libproj-dev libgsl0-dev libnetcdf-dev libode-dev libfftw3-dev libhypre-dev libgtkglext1-dev libstartup-notification0-dev ffmpeg
- darcs get http://gfs.sf.net/darcs/gerris/gts-stable
- darcs get http://gfs.sf.net/darcs/gerris/gerris-stable
- darcs get http://gfs.sf.net/darcs/gerris/gfsview-stable

You can use
- ./configure --prefix=$HOME/local
or
- ./configure

- cd gts-stable
- ./configure
- make
- sudo make install
- cd ../gerris-stable
- ./configure
- make
- sudo make install
- cd ../gfsview-stable
- ./configure
- make
- sudo make install

- sudo /sbin/ldconfig


Full instructions at:
 - http://gfs.sourceforge.net/wiki/index.php/Installing_from_source

