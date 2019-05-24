# EasyVVUQ + FabMD example

### Overview

This example shows how to create an ensemble of LAMMPS simulations using [EassyVVUQ](https://github.com/UCL-CCS/EasyVVUQ), execute the jobs through FabMD, then analyse them within the EasyVVUQ architecture.

Its a very simple example of a LAMMPS ensemble. 5 replicas are created and given different velocity seeds. The solvation energy is calculated at the end of each simulation and the average and standard deviation is output. The intention for this example is to provide a guide to designing your own workflow that uses these two tools together. 

The input files needed for this example are found in `FabMD/config_files/fabmd_easyvvuq`. This directory contains three files:

+ `in.lammps`: is the LAMMPS input script, EasyVVUQ will substitute certain variables in this file to create the ensemble. 

+ `ensemble_input.json`: EasyVVUQ input file. 

+ `data.peptide`: is the configuration file for a peptide in water for LAMMPS simulation. This remains common to all simulations.

For this example it is assumed you can run the basic FabMD and EasyVVUQ examples.

### Execution

These are the commands I needed to run this example:

```
fab archer easymd_example:fabmd_easyvvuq
fab archer monitor - (wait until execution has finished)
fab archer easymd_example_analyse:fabmd_easyvvuq,fabmd_easyvvuq_archer_24
```

---
The generalised commands are:

```
fab remote_machine easymd_example:config_dir
fab remote_machine monitor - (wait until execution has finished)
fab remote_machine easymd_example_analyse:config_dir,output_dir
```

### Command explanation

Each of the three commands is discussed below. They are intended to serve as templates for your own workflows. See the commented code for more information in `FabMD.py`.

---

The first command `easymd_example` is detailed in `FabMD.py`. This sets up the ensemble with EasyVVUQ and executes them with FabSim on the remote machine. 

EasyVVUQ requires a separate place to store the run information, this is put in a `FabMD/tmp/`. 

We vary the random seed that LAMMPS uses to generate atomic velocities with: `my_campaign.vary_param("velocity_seed", dist=uq.distributions.uniform_integer(1,1000000))` 

Note that EasyVVUQ by default uses a `$` to identify variables to carry out variable substitution, however `$` is used by LAMMPS so we escape this clash by defining the delimiter to `@` in `ensemble_input.json` with the line: `"encoder_delimiter": "@" `

We sample 5 different velocity seeds and replicate each only once because given a seed the answer is deterministic. If you were varying a separate parameter that had a stochasitc ouput you would add replicas to each sample.

Then we save the campagin state for later, convert the campaign to a `FabSim` ensemble and execute a `lammps_ensemble`.

---

The second command is used to check when the simulatinos have completed. You could also use `fab remote_machine stat`.

---

The third command `easymd_example_analyse` is detailed in `FabMD.py`. This fetches the results, transfers it back to an EasyVVUQ campaign and then analyses it. It must be passed two arguments: the `config_dir` as usual and the name of the results directory `output_dir`. `output_dir` will be the name of the directory containg the results in your `local_results` directory (set in your `machines_user.yml` file).

Note that we have made LAMMPS output a file that looks like a pnadas dataframse csv file, a more general output could be read by EasyVVUQ by using a custom decoder. 

This command does the equivalent of:

+ fetching the results from the remote machine
+ convert FabSim ensemble to EasyVVUQ campaign
+ aggregate results into a pandas dataframe
+ print all the information of from the campaign
+ prints the mean and standard deviation of the solvation energies


