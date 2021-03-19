.. _execution:

This document briefly details how user/developers can set up a remote machine on FabSim3 for job submission.

How to run a LAMMPS Job
=======================

For this example we assume LAMMPS has been installed on the desired host machine and the location (``lammps_exec``) has been specified in the file ``machines_FabMD_user.yml``.

All the input files required for a LAMMPS simulation should be contained in a directory in ``config_files``.


A minimal example LAMMPS simulation is provided in ``config_files/lammps_test1``, to execute this example type:

    .. code-block:: console
		
		fabsim localhost lammps:lammps_test1	

Modifications can be added in the command line like:

    .. code-block:: console
		
		fabsim host lammps:lammps_test1,lammps_input:in.lammps	


or by specifying default values for these arguments in: ``machines_FabMD_user.yml``.

	.. code-block:: yaml

		default:
		   lammps_params:
		      lammps_input: "in.lammps"
		      sweep_dir_name: "SWEEP"
		      ...


How to run a NAMD Job
=====================

For this example we assume NAMD has been installed on the desired host machine and the location (``namd_exec``) has been specified in the file ``machines_FabMD_user.yml``.

All the input files required for a NAMD simulation should be contained in a directory in ``config_files``.

A minimal example NAMD simulation is provided in ``config_files/namd_test1``, to execute this example type:

    .. code-block:: console
		
		fabsim localhost namd:namd_test1

Modifications can be added in the command line like:

    .. code-block:: console
		
		fabsim host namd:namd_test1,namd_input:eq0.conf	


or by specifying default values for these arguments in: ``machines_FabMD_user.yml``.

	.. code-block:: yaml

		default:
		   namd_params:
		      namd_input: "eq0.conf"
		      sweep_dir_name: "SWEEP"
		      ...

How to run a GROMACS Job
========================

For this example we assume GROMACS has been installed on the desired host machine and the location (``gromacs_exec``) has been specified in the file ``machines_FabMD_user.yml``.

All the input files required for a GROMACS simulation should be contained in a directory in ``config_files``.

A minimal example GROMACS simulation is provided in ``config_files/gromacs_test``, to execute this example type:

    .. code-block:: console
		
		fabsim localhost gromacs:gromacs_test

The ``gromacs`` command first executes grompp and the input files then an MD run on the resulting files. There are three required files for this command and two optional files. The required files are

	* grompp file (``.mdp``)
	* conformation file (``.gro``)
	* topology file (``.top``)

These can be specified in three ways, which take decreasing priority:

	1. In the command line argument.
	2. As a default in ``gromacs_params`` in ``machines_FabMD_user.yml``.
	3. A file found in the specified ``config_files`` directory with the correct extension

Files are specified in the command line like this:

    .. code-block:: console
		
		fabsim localhost gromacs:gromacs_test,grompp=nvt.mdp,conf=npt4b.gro,topol=top.top


Defaults can be also set in the gromacs default parameters in ``machines_FabMD_user.yml``.

	.. code-block:: yaml

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

Or finally, if a required file is not specified in the command line or as a default it will search for a file with the correct extension in the config directory. If one and only one is found this file is used. If multiple files with the correct extension are found it is ambiguous and an error is issued.

There are two optional files that, if desired, must be specified on the command line.

	* checkpoint file (.cpt)
	* index file (.ndx)

These could be specifed like this:

    .. code-block:: console
		
		fabsim localhost gromacs:gromacs_test,grompp=nvt.mdp,conf=npt4b.gro,topol=top.top,checkpoint=npt4b.cpt,index=index.ndx

or simply set them inside ``machines_FabMD_user.yml``. The grompp command executes with all required and optional files. This produces a ``mdout.mdp`` file which is run with:

    .. code-block:: console
		
		gmx mdrun

Run Ensemble Examples
=====================

lammps_ensemble_example1
------------------------
These examples assume that you have been able to run the basic examples described above, and that you have installed and configured LAMMPS on the target machine.

To run type:

    .. code-block:: console
		
		fabsim localhost lammps_ensemble:lammps_ensemble_example1

FabMD looks for a directory called ``lammps_ensemble_example1`` in ``config_files``. It then looks for a sweep directory (by default called ``SWEEP``) that contains a number of input files to iterate through. All the files in ``lammps_ensemble_example1`` directory and one of the sweep directory files will be copied to the host in separate directories (one for each sweep file) and executed in the normal way. This example essentially runs the same input script with different topology (data) files.


lammps_ensemble_example2
------------------------

This example runs 3 simulations with different input files, which vary the simulation temperature, using the same topology file.

To run type:

    .. code-block:: console
		
		fabsim localhost lammps_ensemble:lammps_ensemble_example2



* **NOTE** if your input filename is not the same as the one set in lammps_params entry in machines_FabMD_user.yml file, then you will have to specify this in the command line. For example the following command may be more suitable but will run the exact same simulations:

    .. code-block:: console
		
		fabsim localhost lammps_ensemble:lammps_ensemble_example2,lammps_input=in.peptide


Gromacs ensemble test
=====================

Hopefully the structure of the ensemble execusion is becoming familar. To run the minimal gromacs ensemble examples type:

    .. code-block:: console
		
		fabsim localhost gromacs_ensemble:gromacs_ensemble_test,grompp=npt.mdp

The run files and SWEEP directory are contained with in ``config_files/gromacs_ensemble_test``. The ``grompp`` file must be specified on the command line because there are a few options in the directory, if this does not make sense please read the **How to run a GROMACS Job section**.		


EasyVVUQ + FabMD example
========================

This example shows how to create an ensemble of LAMMPS simulations using EasyVVUQ, execute the jobs through FabMD, then analyse them within the `EasyVVUQ <https://easyvvuq.readthedocs.io/en/dev/>`_ architecture. All within 3 FabSim commands!!!

.. Note:: All the easyvvuq campaign infantilization, runs execution, and the results analyse will be done on target machine which can be your localhost or remote HPC machine.

Its a very simple example of a LAMMPS ensemble. 3 runs are created and given different velocity seeds. The solvation energy is calculated at the end of each simulation and the average and standard deviation are output to screen. The intention for this example is to provide a guide to designing your own workflow that uses these two tools together.

The input files needed for this example are found in ``plugins/FabMD/config_files/fabmd_easyvvuq_test1``. This directory contains three files:


* ``lammps.template``: is the LAMMPS input script in ``sampler_inputs`` subfolder, EasyVVUQ will substitute certain variables in this file to create the ensemble.
* ``data.peptide``: is the configuration file for a peptide in water for LAMMPS simulation. This remains common to all simulations.
* ``campaign_params.yml``: is the configuration file, in ``sampler_inputs`` subfolder, for EasyVVUQ sampler. If you need different sampler, parameter to be varied, or polynomial order, you can set them in this file.

Execution
---------
These are the commands you needed to run this example:

    .. code-block:: console
		
		fabsim <remote machine> lammps_init_campaign:fabmd_easyvvuq_test1
		fabsim <remote machine> lammps_run_campaign:fabmd_easyvvuq_test1
		fabsim <remote machine> lammps_analyse_campaign:fabmd_easyvvuq_test1

``<remote machine>`` can be your ``localhost`` or a HPC resources.