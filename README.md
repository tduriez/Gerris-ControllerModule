# Gerris - Controller Module

The following tutorial provides quick guidelines in how to install the Gerris Controller Module using the latest source code version. This module was not yet packaged so an old-school installation is required.

## Prerequisites

As first step, it is recommended to test your environment against the latest version of Gerris. In order to install it, you should download the source code and required dependencies as follows:
```bash
sudo apt-get install libglib2.0-dev libnetpbm10-dev m4 libproj-dev libgsl0-dev libnetcdf-dev libode-dev libfftw3-dev libhypre-dev libgtkglext1-dev libstartup-notification0-dev ffmpeg
darcs get http://gfs.sf.net/darcs/gerris/gts-stable
darcs get http://gfs.sf.net/darcs/gerris/gerris-stable
darcs get http://gfs.sf.net/darcs/gerris/gfsview-stable
```

## Compiling Gerris

Before proceeding, you need to define the target installation folder. It is being done by providing a 'prefix' variable to the compile configuration scripts. Then, you can opt to use either:
- ./configure  #when the default values are going to be used
- ./configure --prefix=$HOME/local  #when a folder was choosed

Then, you must execute a sequence of configure/make/make-install commands to compile the system:
```bash
cd gts-stable
./configure
make
sudo make install
cd ../gerris-stable
./configure
make
sudo make install
cd ../gfsview-stable
./configure
make
sudo make install
sudo /sbin/ldconfig
```
Full instructions to install Gerris can be found at:
 - http://gfs.sourceforge.net/wiki/index.php/Installing_from_source

## Testing the installation

It is a good idea to test the Gerris installation now by using one of the online examples. This way you have a safe checkpoint to return in case anything fails.

## Compiling Controller Module

You should download the source code, compile and install it as in the original Gerris repository.

```bash
git clone https://github.com/pablodroca/Gerris-ControllerModule.git
cd Gerris-ControllerModule
cd gerris-stable
./configure
make
sudo make install
```

Note:
In order to have debugging information for development purposes, gerris-stable could be compiled with different log levels. You can do it by running:
```bash
make CFLAGS='-ggdb -g0 -DG_DEBUG=\"debug\"' && sudo make install
```

