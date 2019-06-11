# Run Ensemble Examples

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
