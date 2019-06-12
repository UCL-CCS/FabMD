# Run Ensemble Examples

### lammps_ensemble_example1

These examples assume that you have been able to run the basic FabSim examples described in the other documentation files, and that you have installed and configured LAMMPS on the target machine.

To run type:
```
fabsim localhost lammps_ensemble:lammps_ensemble_example1
```

FabMD looks for a directory called `lammps_ensemble_example1` in `config_files`. It then looks for a sweep directory (by default called `SWEEP`) that contains a number of input files to iterate through. All the files in `lammps_ensemble_example1` directory and one of the sweep directory files will be copied to the host in separate directories (one for each sweep file) and executed in the normal way. 
This example essentially runs the same input script with different topology (data) files.

### lammps_ensemble_example2

This example runs 3 simulations with different input files, which vary the simulation temperature, using the same topology file.

To run type:
```
fabsim localhost lammps_ensemble:lammps_ensemble_example2
```

NOTE if your input filename is not the same as the one set in ``FabMD/default_settings/lammps.yaml``, then you will have to specify this in the command line. For example the following command may be more suitable but will run the exact same simulations:
``fab localhost lammps_ensemble:lammps_ensemble_example2,lammps_input=in.peptide``

### Gromacs_ensemble_test

Hopefully the structure of the ensemble execusion is becoming familar. To run the minimal gromacs ensemble examples type:
```
fabsim localhost gromacs_ensemble:gromacs_ensemble_test,grompp=npt.mdp
```
The run files and SWEEP directory are contained with in `config_files/gromacs_ensemble_test`. The grompp file must be specified on the command line because there are a few options in the directory, if this does not make sense please read the `run_GROMACS_job.md` file
