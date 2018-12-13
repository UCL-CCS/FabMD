# Running a GROMACS job

For this example we assume GROMACS has been installed on the desired host machine and the location (`host: gromacs_exec`) has been specified in the file `deplot/machines_usr.yml`.

All the input files required for a G?ROMACS simulation should be contained in a directory in `config_files`. 

A minimal example GROMACS simulation is provided in `config_files/gromacs_test`, to execute this example type:

`fab localhost gromacs:gromacs_test`

The `gromacs` command first executes grompp and the input files then an MD run on the resulting files.

There are three required files for this command and two optional files. The required files are

- grompp file (`.mdp`)
- conformation file (`.gro`)
- topology file (`.top`)

These can be specified in three ways, which take decreasing priority:

1. In the command line argument
2. As a default in `default_settings/gromacs.yaml`
3. A file found in the specified config directory with the correct extension

Files are specified in the command line like this: 
```
fab localhost gromacs:gromacs_test,grompp=nvt.mdp,conf=npt4b.gro,topol=top.top
```
Defaults can be set in the gromacs default file as a dictionary value such as:
```
required files:
  grompp: npt.mdp
  conf: npt4b.gro
  topol top.top
```
Or finally, if a required file is not specified in the command line or as a default it will search for a file with the correct extension in the config directory. If one and only one is found this file is used. If multiple files with the correct extension are found it is ambiguous and an error is issued.

There are two optional files that, if desired, must be specified on the command line.

- checkpoint file (`.cpt`)
- index file (`.ndx`)

These could be specifed like this:
```
fab localhost gromacs:gromacs_test,grompp=nvt.mdp,conf=npt4b.gro,topol=top.top,checkpoint=npt4b.cpt,index=index.ndx
```

The grompp command executes with all required and optional files. This produces a `mdout.mdp` file which is run with:
```
gmx mdrun
```
