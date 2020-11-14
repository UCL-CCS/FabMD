# FabMD
FabMD is a  [FabSim3](https://github.com/djgroen/FabSim3) plugin for automated [LAMMPS](https://lammps.sandia.gov/)-based simulations.

This plugin provides functionality to extend FabSim3's workflow and remote submission capabilities to LAMMPS specific tasks.


   * [Installation](#installation)
      * [LAMMPS Installation](#lammps-installation)
      * [GROMACS Installation](#gromacs-installation)
      * [FabMD Installation](#fabmd-installation)
   * [How to run a LAMMPS Job](#how-to-run-a-lammps-job)
   * [How to run a GROMACS Job](#how-to-run-a-gromacs-job)
   * [Run Ensemble Examples](#run-ensemble-examples)     

## Installation

### LAMMPS Installation

We suggest to install it from source files.
- Download the latest stable version from [https://lammps.sandia.gov/tars/lammps-stable.tar.gz](https://lammps.sandia.gov/tars/lammps-stable.tar.gz>)
- Extract tar file by `tar xvf lammps-stable.tar.gz`. This will create a folder named: *`lammps-29Oct20`* (The date may change depending of the updates in the website). Rename  *`lammps-29Oct20`* folder to *`lammps`*.
- Before keep going it is necessary to solve some dependencies: build-essential (to compile in C), MPIch (to work in parallel) , FFTW ( to compute long-range interactions), libxaw7 (to compute the movies). In one line code you choose
	```sh
	sudo apt-get install build-essential libxaw7-dev
	```
- Then, go to the extract folder, and execute following commands. For provided example in FabMD,  `MOLECULE`, `KSPACE`, and `RIGID` packages should be installed too.
	```sh
	~$ cd lammps
	~/lammps$ cd src/STUBS
	~/lammps/src/STUBS$ make clean
	~/lammps/src/STUBS$ make
	~/lammps/src/STUBS$ cd ..
	~/lammps/src$ make clean-all
	~/lammps/src$ make yes-molecule
	~/lammps/src$ make yes-kspace
	~/lammps/src$ make yes-rigid		
	~/lammps/src$ make serial
	```
- If the installation part worked correctly, you should be able to find ``lmp_serial`` executable file inside ``lammps/src`` folder
- Modify ``machines_FabMD_user.yml`` to make the *`lammps_exec`* variable point to the location of the LAMMPS executable. e.g.
	```yaml
	...
	localhost:
	         lammps_exec: "/home/hamid/lammps/src/lmp_serial"
	         ...
	...
	```

### GROMACS Installation
We suggest to use automate installer ([source](https://bioinformaticsreview.com/20151126/how-to-install-gromacs-5-x-x-on-linux-ubuntu-14-04-lts/) ).

- Download the auto-installer script from [https://bioinformaticsreview.com/repository/gromacs-installer.sh](https://bioinformaticsreview.com/repository/gromacs-installer.sh)
- make installer executable
	```sh
	chmod +x gromacs-installer.sh
	```
- Start Installer. This will create `gromacs` folder where you execute this auto-installer script.
	```sh
	./gromacs-installer.sh
	```

## FabMD Installation
Before run LAMMPS test data set, you should install FabMD which provides functionality to extend FabSim3's workflow and remote submission capabilities to LAMMPS specific tasks. Please install it by typing:

```sh
fabsim localhost install_plugin:FabMD
```

## How to run a LAMMPS Job
For this example we assume LAMMPS has been installed on the desired host machine and the location (`lammps_exec`) has been specified in the file `machines_FabMD_user.yml`.

All the input files required for a LAMMPS simulation should be contained in a directory in `config_files`.

A minimal example LAMMPS simulation is provided in `config_files/lammps_test1`, to execute this example type:

```sh
fabsim localhost lammps:lammps_test1
```
Modifications can be added in the command line like:
```sh
fabsim host lammps:lammps_test1,lammps_input:in.lammps
```
or by specifying default values for these arguments in: `machines_FabMD_user.yml`.

```yaml
default:
  lammps_params:
    lammps_input: "in.lammps"
    sweep_dir_name: "SWEEP"    
...
```
## How to run a GROMACS Job
For this example we assume GROMACS has been installed on the desired host machine and the location (`gromacs_exec`) has been specified in the file `machines_FabMD_user.yml`.

All the input files required for a GROMACS simulation should be contained in a directory in `config_files`.

A minimal example GROMACS simulation is provided in `config_files/gromacs_test`, to execute this example type:
```sh
fabsim localhost gromacs:gromacs_test
```
The `gromacs` command first executes grompp and the input files then an MD run on the resulting files.
There are three required files for this command and two optional files. The required files are
- grompp file (`.mdp`)
- conformation file (`.gro`)
- topology file (`.top`)

These can be specified in three ways, which take decreasing priority:
1. In the command line argument.
2. As a default in `gromacs_params` in `machines_FabMD_user.yml`.
3. A file found in the specified `config_files` directory with the correct extension

Files are specified in the command line like this:
```sh
fabsim localhost gromacs:gromacs_test,grompp=nvt.mdp,conf=npt4b.gro,topol=top.top
```
Defaults can be also set in the gromacs default parameters in  `machines_FabMD_user.yml`.

```yaml
default:
   gromacs_params:
      sweep_dir_name: "SWEEP"
      required_files:
         grompp: nvt.mdp
         conf: npt4b.gro
         topol: top.top
         checkpoint:
         index: index.ndx
...
```
Or finally, if a required file is not specified in the command line or as a default it will search for a file with the correct extension in the config directory. If one and only one is found this file is used. If multiple files with the correct extension are found it is ambiguous and an error is issued.

There are two optional files that, if desired, must be specified on the command line.
- checkpoint file (`.cpt`)
- index file (`.ndx`)

These could be specifed like this:
```sh
fabsim localhost gromacs:gromacs_test,grompp=nvt.mdp,conf=npt4b.gro,topol=top.top,checkpoint=npt4b.cpt,index=index.ndx
```
or simply set them inside `machines_FabMD_user.yml`.
The grompp command executes with all required and optional files. This produces a `mdout.mdp` file which is run with:
```sh
gmx mdrun
```
## Run Ensemble Examples

### lammps_ensemble_example1
These examples assume that you have been able to run the basic examples described above, and that you have installed and configured LAMMPS on the target machine.

To run type:
```sh
fabsim localhost lammps_ensemble:lammps_ensemble_example1
```
FabMD looks for a directory called `lammps_ensemble_example1` in `config_files`. It then looks for a sweep directory (by default called `SWEEP`) that contains a number of input files to iterate through. All the files in `lammps_ensemble_example1` directory and one of the sweep directory files will be copied to the host in separate directories (one for each sweep file) and executed in the normal way. This example essentially runs the same input script with different topology (data) files.

### lammps_ensemble_example2

This example runs 3 simulations with different input files, which vary the simulation temperature, using the same topology file.

To run type:
```sh
fabsim localhost lammps_ensemble:lammps_ensemble_example2
```

- NOTE if your input filename is not the same as the one set in `lammps_params` entry in  `machines_FabMD_user.yml` file, then you will have to specify this in the command line. For example the following command may be more suitable but will run the exact same simulations:
	 ```sh
	fab localhost lammps_ensemble:lammps_ensemble_example2,lammps_input=in.peptide
	```

### Gromacs_ensemble_test

Hopefully the structure of the ensemble execusion is becoming familar. To run the minimal gromacs ensemble examples type:
```sh
fabsim localhost gromacs_ensemble:gromacs_ensemble_test,grompp=npt.mdp
```
The run files and SWEEP directory are contained with in `config_files/gromacs_ensemble_test`. The grompp file must be specified on the command line because there are a few options in the directory, if this does not make sense please read the  [How to run a GROMACS Job](#how-to-run-a-gromacs-job) section.

