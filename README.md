
# FabMD
FabMD is a  [FabSim3](https://github.com/djgroen/FabSim3) plugin for automated [LAMMPS](https://lammps.sandia.gov/)-based simulations.

This plugin provides functionality to extend FabSim3's workflow and remote submission capabilities to LAMMPS specific tasks.


For the full FabMD documentation, please visit https://fabmd.readthedocs.io

## EasyVVUQ+FabMD 
After updating the following files with your credentials

```
  -FabSim3/deploy/machines_user.yml
  -FabSim3/deploy/machines.yml
  -FabSim3/plugins/FabMD/machines_FabMD_user.yml
  
```

run the following:

```
  -  fabsim   <remote machine name>   lammps_init_run_analyse_campaign:fabmd_easyvvuq_InRuAn
```

and copy the results back to your local machine with

```
  -  fabsim  <remote machine name>   fetch_results
```

