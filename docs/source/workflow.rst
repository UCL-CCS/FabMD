.. _workflow:


FabMD Workflow
==============

Introduction
------------
FabMD is a tool that allows for the easy execution of molecular dynamics simulations in remote machines. This section of the documentation will cover an example of how one would go about configuring FabMD and running a simulation using LAMMPS.


Example of workflow for FabMD
-----------------------------

First, it is important to define a simulation. We create a directory called ``my-simulation`` which contains a single LAMMPS input script called ``in.lammps`` that defines the entire simulation. We need to make FabMD aware of this directory, which we can do by placing the ``my-simulation`` directory inside of the config_files directory (``FabSim3/plugins/FabMD/config_files``). With this, FabMD now recognises the LAMMPS simulation and we are free to call any of the ``fabsim`` commands on the command line.

Before submitting the simulation to a remote machine, two YAML files must be edited. First we modify the file ``FabSim3/deploy/machines_user.yml`` and add our login credentials in the template so that FabMD knows where to run the simulation. In this example we will use the PSNC HPC system called Eagle, so the only parameter we need to add is the ``username`` we use for that computer. Other computers may have have more parameters that need to be added, such as for example, the UK National Supercomputer ARCHER2, which also requires a password to be entered. 

The next file that needs to be updated is ``FabSim3/plugins/FabMD/machines_FabMD_user.yml``. In this file you can set the path to the LAMMPS executable on the remote machine. However, most HPC clusters have LAMMPS available as a module and this can be added in the loaded modules section of the file. This means that the ``lammps_exec`` parameter can be set to the LAMMPS command rather than the path of the compiled executable. For example, an arbitrary remote machine might look like:

	.. code-block:: yaml

		remote-machine-name:
		   lammps_exec: "lmp"
		   ...
		   ...
		   ...
		   modules:
		      loaded: ["lammps/15Apr2020"]

After all this configuration, we can submit a simulation to a remote machine using the command:

    .. code-block:: console
		
		fabsim eagle lammps:my-simulation	

To recap, this command can be read as follows: execute LAMMPS on a simulation in the directory ``my-simulation`` inside the remote machine ``eagle``. This command will automatically generate a batch script which is sent to the scheduler so that the remote machine can run the simulation. By default, the ``lammps`` subcommand will execute the file called ``in.lammps``. This behaviour can be changed by adding the optional command:

    .. code-block:: console
		
		fabsim eagle lammps:my-simulation,lammps_input=new-input.in

Where ``new-input.in`` is the name of the LAMMPS script you wish to execute.



Additionally, other parameters can be changed such as the number of cores that are used or the maximum ``job_wall_time``. An example of a optionally configured command is:


    .. code-block:: console
		
		fabsim eagle lammps:my-simulation,cores=1,job_wall_time=0:10:0

Once the simulation has been submitted, we can check on the status of the job using the command:

    .. code-block:: console
		
		fabsim eagle stat


The information provided will differ between machines, but in general this command will give the runtime of the simulation and which nodes are being used.


When the job has completed, we can use the command:

    .. code-block:: console
		
		fabsim eagle fetch_results


To copy all of the results from the remote machine to our local computer.




To summarise, a typical workflow would be composed of the three commands:

    .. code-block:: console
		
		fabsim <remote machine name> lammps:<directory in config_files>
		fabsim <remote machine name> stat
		fabsim <remote machine name> fetch_results
