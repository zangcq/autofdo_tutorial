AutoFDO tutorial ================

This package will help you understand and automate the process of using
feedback driven optimizations, the tutorial has been divided in three sections:

## 1. Basic understanding

In this repository you will find a `sort.c` file that contains a sorting
algorithm to start using optimizations, then you will need to read our document
in https://gcc.gnu.org/wiki/AutoFDO/Tutorial and follow the steps to compare
different types of optimizations:

1. GCC normal optimization (just add the -O flag to the gcc command)
2. FDO (By executing the instrumented binary, it will output data to a profile
   file)
3. AutoFDO (By using perf, it will sample the hardware events to create a
   profile file)
 
You can read more information about using optimization flags in here
https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html

## 2. Different use cases

You might will be willing to optimize a package that can include different
binaries, which may result in multiple binaries, so we included an example in
this tutorial. Every binary contains different algorithms with a timing measure
that prints at the end of the execution so you won't need to implement any time
mesurement tool.

#### GCC normal optimization

If you want to know how much performance is imporved by FDO, compile them with
`$ make release` This will enable the `-O3` flag.

Execute every binary to know how much they delay.

#### Normal FDO

For this case you will need to compile all the binaries with the debug symbols
and the `-fprofile-generate` flag to keep track of the execution feedback:

    $ gcc -g3 -Iinclude -lm -o bubble_sort src/bubble_sort.c src/debug.c
    -fprofile-generate $ gcc -g3 -Iinclude -lm -o matrix_multiplication
    src/matrix_multiplication.c src/debug.c -fprofile-generate $ gcc -g3
    -Iinclude -lm -o pi_calculation src/pi_calculation.c src/debug.c
    -fprofile-generate
    
Then execute each binary to get the feedback:

    $ ./bubble_sort $ ./matrix_multiplication $ ./pi_calculation
    
Then recompile again with the `-fprofile-use` flag and the optimization enabled
(`-O3`)

In case that you want to compile using `$ make release` you will need to change
the `RELEASEFLAGS` variable to include `-fprofile-use=*.gcda` to use all the
profile files

    $ make RELEASEFLAGS="-O3 -fprofile-use=*.gcda" release

Execute the binaries again to measure the time and compare with other
optimization methods.

#### AutoFDO

The first thing you do after downloading a source code is compiling, so go
ahead and execute:

    $ make

Then we have included a proccess that generates the profiles for you. We are
taking advantage of a perf wrapper named `ocperf.py`, this tool can be found in
the repository in here: https://github.com/andikleen/pmu-tools. We are also
downloading and compiling AutoFDO from https://github.com/google/autofdo. The
default location for this tools is /tmp/ you can change it by overwriting the
`INSTALLATION_PATH` variable:

    $ make autofdo
    
Then before recompiling, you will need to change the `RELEASEFLAGS` variable to
use the .afdo profile files

    $ make RELEASEFLAGS="-O3 -fauto-profile=*.afdo" release
    

Another option is to merge the profiles using the `profile_merger` binary in
AutoFDO package. This will make you handle only just one .afdo file instead of
multiple (Remember to include `-gcov_version=1` flag):

    $ /tmp/autofdo/profile_merger -gcov_version=1 *.afdo $ make
    RELEASEFLAGS="-O3 -fauto-profile=fbdata.afdo" release

Execute the binaries again to measure the time and compare with other
optimization methods.

In case you want to clean everithing run `$ make distclean` this will delete
all generated files to start compiling again.

## 3. Automation scripts

If you want to get the perf.data of any execution you can use the
`generate_perf_data.sh` file. This script will automatically download the
pmu_tools repository in specified directory (/tmp/ by default):

    $ ./generate_perf_data.sh --command="./some_tool --params"

If you want to generate an AutoFDO profile, you can use the
`profile_generator.py`. This script will automatically download and compile
AutoFDO package in specified directory (/tmp/ by default)

    $ ./profile_generator.py some_tool.data

Then you will have a `some_tool.afdo` merged profile that can be used to
recompile the "some_tool" binaries



    
