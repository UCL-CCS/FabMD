#!/bin/bash
module load namd

# Equilibration simulation
srun -n $SLURM_NTASKS namd2 eq0.conf
