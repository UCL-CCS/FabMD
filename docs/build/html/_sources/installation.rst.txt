.. _installation:

.. Installation
.. ============

LAMMPS Installation
===================

We suggest to install it from source files.


* Download the latest stable version from https://lammps.sandia.gov/tars/lammps-stable.tar.gz

* Extract tar file by ``tar xvf lammps-stable.tar.gz``. This will create a folder named: ``lammps-29Oct20`` (The date may change depending of the updates in the website). Rename ``lammps-29Oct20`` folder to ``lammps``. 

* Before keep going it is necessary to solve some dependencies: build-essential (to compile in C), MPIch (to work in parallel) , FFTW ( to compute long-range interactions), libxaw7 (to compute the movies). In one line code you choose

    .. code-block:: console
		
		sudo apt-get install build-essential libxaw7-dev	

* Then, go to the extract folder, and execute following commands. For provided example in FabMD, ``MOLECULE``, ``KSPACE``, and ``RIGID`` packages should be installed too.

    .. code-block:: console
		
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



.. Note:: If the installation part worked correctly, you should be able to find ``lmp_serial`` executable file inside ``lammps/src folder``.

* Modify ``machines_FabMD_user.yml`` to make the ``lammps_exec`` variable point to the location of the LAMMPS executable. e.g.

	.. code-block:: yaml

		...
		localhost:
			lammps_exec: "/home/hamid/lammps/src/lmp_serial"
		    ...
		...

NAMD Installation
=================

We suggest to follow installation instructions from the `NAMD website <https://www.ks.uiuc.edu/Research/namd/2.9/ug/node94.html>`_.

* After installing NAMD, modify ``machines_FabMD_user.yml`` to make the ``namd_exec`` variable point to the location of the NAMD executable

	.. code-block:: yaml

		...
		localhost:
			namd_exec: "/home/hamid/opt/path/to/namd/sources/namd2"
		    ...
		...


GROMACS Installation
====================

We suggest to use automate installer (`source <https://bioinformaticsreview.com/20151126/how-to-install-gromacs-5-x-x-on-linux-ubuntu-14-04-lts/>`_).

* Download the auto-installer script from https://bioinformaticsreview.com/repository/gromacs-installer.sh
* make installer executable

    .. code-block:: console
		
		chmod +x gromacs-installer.sh	

* Start Installer. This will create ``gromacs`` folder where you execute this auto-installer script.

    .. code-block:: console
		
		./gromacs-installer.sh	


FabMD Installation
==================

Before run LAMMPS test data set, you should install FabMD which provides functionality to extend FabSim3's workflow and remote submission capabilities to LAMMPS specific tasks. 

* To install FabSim3 tool, please follow the installation from https://fabsim3.readthedocs.io/en/latest/installation.html

* To install FabMD plugin, simple type:

    .. code-block:: console
		
		fabsim localhost install_plugin:FabMD	
