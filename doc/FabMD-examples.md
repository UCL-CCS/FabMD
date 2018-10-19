### Running a lammmps job

For these examples we assume LAMMPS has been installed on the desired host machine and the location (``host: lammps_exec``) has been specified in the file ``deplot/machines_usr.yml``.

# Running Lammps_test1

All the input files required for the LAMMPS simulation should be contained in a directory in ``config_files``. Then type:
``fab localhost lammps:lammps_test1```

Modifications can be added in the command line like:
```fab host lammps:lammps_test1,lammps_input:in.lammps,wall_time:1:00:00,cores=1```
or by specifiying default values for these arguments in: ``FabMD/default_settings/lammps.yaml``. 

