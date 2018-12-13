# How to run a LAMMPS Job

For this example we assume LAMMPS has been installed on the desired host machine and the location (``host: lammps_exec``) has been specified in the file ``deplot/machines_usr.yml``.

All the input files required for a LAMMPS simulation should be contained in a directory in ``config_files``. 

A minimal example LAMMPS simulation is provided in ``config_files/lammps_test1``, to execute this example type:

``fab localhost lammps:lammps_test1``

Modifications can be added in the command line like:

```fab host lammps:lammps_test1,lammps_input:in.lammps,wall_time:1:00:00,cores=1```

or by specifiying default values for these arguments in: ``FabMD/default_settings/lammps.yaml``. 
